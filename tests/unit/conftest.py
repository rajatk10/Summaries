from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.ping import router as ping_router
from app.api.summaries import router as summaries_router
from app.main import app


@pytest.fixture
def summaries_record():
    now = datetime.now(UTC)
    return SimpleNamespace(
        id=uuid4(),
        url="http://example.com",
        summary="A test based Example Summary",
        ai_summary=None,
        ai_task_status="pending",
        created_at=now,
        updated_at=now,
        processed_at=None,
        save=AsyncMock(),
        delete=AsyncMock(),
    )


@pytest.fixture
def ping_api_client():
    client = FastAPI(app=app)
    client.include_router(ping_router)
    return TestClient(client)


@pytest.fixture
def api_client():
    client = FastAPI(app=app)
    client.include_router(summaries_router)
    return TestClient(client)
