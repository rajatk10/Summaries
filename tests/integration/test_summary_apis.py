from unittest.mock import AsyncMock

import pytest
from tortoise import connections

from app.api import summaries as summaries_api
from app.models import Summary
from app.nlp import ai_summary


@pytest.mark.integration
@pytest.mark.asyncio
async def test_connected_integration_database(integration_client):
    # The above fixture makes sure that integration client is given

    rows = await connections.get("default").execute_query_dict(
        "SELECT current_database() AS database_name, current_user AS database_user"
    )

    assert rows[0]["database_name"] == "summaries-test"
    assert rows[0]["database_user"] == "summaries_test"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_create_and_read_summary(
    integration_client,
    monkeypatch,
):
    # GIVEN a migrated, empty PostgreSQL test database
    process_task = AsyncMock()
    monkeypatch.setattr(
        summaries_api,
        "process_nlp_summary_task",
        process_task,
    )
    payload = {
        "url": "https://example.com/integration-article",
        "summary": "Integration test summary",
    }

    # WHEN the client creates a summary
    create_response = await integration_client.post(
        "/summaries",
        json=payload,
    )

    # THEN the API and real database contain the same record
    assert create_response.status_code == 201
    body = create_response.json()
    stored = await Summary.get(id=body["id"])
    assert stored.url == payload["url"]
    assert stored.summary == payload["summary"]
    assert stored.ai_task_status == "pending"
    process_task.assert_awaited_once()

    read_response = await integration_client.get(
        f"/summaries/{body['id']}",
    )
    assert read_response.status_code == 200
    assert read_response.json()["id"] == body["id"]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_migrations_create_summary_read_columns(integration_client):
    # GIVEN all committed migrations were applied to a fresh database

    # WHEN PostgreSQL metadata is inspected
    rows = await connections.get("default").execute_query_dict(
        "SELECT column_name FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'summaries'"
    )
    columns = {row["column_name"] for row in rows}

    # THEN the current model fields exist in the migrated schema
    assert {
        "ai_summary",
        "ai_task_status",
        "processed_at",
        "created_at",
        "updated_at",
        "url",
        "summary",
        "id",
    } <= columns


@pytest.mark.integration
@pytest.mark.asyncio
async def test_process_ai_task_summary(integration_client, monkeypatch):
    # GIVEN a real pending row and deterministic extracted article text
    record = await Summary.create(
        url="https://example.com/ai-integration",
        summary="User supplied summary",
        ai_task_status="pending",
    )
    monkeypatch.setattr(
        ai_summary,
        "fetch_and_clean_text",
        AsyncMock(return_value="A sufficiently long deterministic article."),
    )
    monkeypatch.setattr(
        ai_summary,
        "generate_nlp_summary",
        lambda text: "Generated integration summary.",
    )

    # WHEN the background-task function runs
    await ai_summary.process_nlp_summary_task(record.id, record.url)

    # THEN its result is persisted through the real ORM/database
    await record.refresh_from_db()
    assert record.ai_summary == "Generated integration summary."
    assert record.ai_task_status == "completed"
    assert record.processed_at is not None
