import os
import subprocess
import sys
from urllib.parse import urlparse

# These assignments must happen before importing app.main or app.config.
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql://summaries_test:summaries_test@127.0.0.1:15433/summaries-test",
)

database_url = os.environ["DATABASE_URL"]
parsed_database_url = urlparse(database_url)

if os.environ["ENVIRONMENT"] != "test":
    raise RuntimeError("Integration tests require ENVIRONMENT=test")
if parsed_database_url.path != "/summaries-test":
    raise RuntimeError("Refusing to run outside the summaries-test database")
if parsed_database_url.hostname not in {"127.0.0.1", "localhost", "test-db"}:
    raise RuntimeError("Integration database must use an approved test host")

import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.models import Summary


@pytest.fixture(scope="session", autouse=True)
def migrated_database():
    """Apply committed migrations before opening the application lifespan."""
    subprocess.run(
        [
            sys.executable,
            "-m",
            "tortoise",
            "-c",
            "app.config.TORTOISE_ORM",
            "migrate",
        ],
        check=True,
        env=os.environ.copy(),
    )


@pytest_asyncio.fixture
async def integration_client(migrated_database):
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(
            transport=transport,
            base_url="http://integration-test",
        ) as client:
            yield client

        # The URL/name guard above makes this cleanup deliberately test-only.
        await Summary.all().delete()
