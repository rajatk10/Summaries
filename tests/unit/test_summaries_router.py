"""
A unit test file for summaries api router.
1. Fetch Summary using summary id
2. Failed to fetch summary, 404 error if incorrect ID
3. Create summary, post endpoint - pass validation
4. Failed to create summary, post endpoint - fail validation
"""

import uuid
from unittest.mock import AsyncMock

from fastapi import HTTPException

from app.api import summaries as summaries_api
from app.models import Summary


class TestSummariesRouter:
    def test_valid_get_summary(self, api_client, summaries_record, monkeypatch):
        """
          Code under test: get_summary()
        - Dependency: fetch_summary()
        - Deeper external dependency: Summary.get_or_none()
        - Recommended patch: Summary.get_or_none() so the route and helper are tested together.
        """
        fetch_summary_mock = AsyncMock(return_value=summaries_record)
        monkeypatch.setattr(summaries_api, "fetch_summary", fetch_summary_mock)
        res = api_client.get(f"/summaries/{summaries_record.id}")
        assert res.status_code == 200
        body = res.json()
        assert body["summary"] == str(summaries_record.summary)
        fetch_summary_mock.assert_called_once()

    def test_missing_id_get_summary(self, api_client, monkeypatch):
        fetch_missing_summary_mock = AsyncMock(
            side_effect=HTTPException(status_code=404, detail="Summary not found")
        )
        id = uuid.uuid4()
        monkeypatch.setattr(summaries_api, "fetch_summary", fetch_missing_summary_mock)
        res = api_client.get(f"/summaries/{id}")
        assert res.status_code == 404
        assert res.json() == {"detail": "Summary not found"}

    def test_invalid_id_get_summary(self, api_client, monkeypatch):
        id = "inva-lid-id"
        fetch_summary_mock = AsyncMock(return_value=None)
        monkeypatch.setattr(summaries_api, "fetch_summary", fetch_summary_mock)
        res = api_client.get(f"/summaries/{id}")
        assert res.status_code == 422

    def test_summary_post_request(self, api_client, summaries_record, monkeypatch):
        payload = {
            "url": "https://example.com/article",
            "summary": "Example summary",
        }
        create_summary_mock = AsyncMock(return_value=summaries_record)
        process_summary_mock = AsyncMock()
        monkeypatch.setattr(Summary, "create", create_summary_mock)
        monkeypatch.setattr(
            summaries_api,
            "process_nlp_summary_task",
            process_summary_mock,
        )
        # The create_summary def in summaries_api calls Summary.create tortoise call so we need to mimick that
        res = api_client.post("/summaries", json=payload)
        assert res.status_code == 201
        body = res.json()
        assert body["summary"] == str(summaries_record.summary)
        assert body["ai_task_status"] == "pending"
        create_summary_mock.assert_awaited_once_with(
            url=payload["url"],
            summary=payload["summary"],
            ai_task_status="pending",
        )
        process_summary_mock.assert_awaited_once_with(
            summaries_record.id,
            summaries_record.url,
        )
