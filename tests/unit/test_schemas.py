"""
Test the schemas defined
1. Accept a valid write payload
2. Test a valid response
3. Reject invalid URL in payload
4. Reject an empty summary in payload
5. Test valid SummaryRead response
"""

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.schemas import SummaryRead, SummaryWrite


class TestSchemas:
    def test_accept_valid_payload(self):
        # given
        url = "https://www.testexampleurl.com/"
        summary = "This is a test generated summary"
        # when
        payload = SummaryWrite(url=url, summary=summary)
        # then
        assert str(payload.url) == url
        assert str(payload.summary) == summary

    def test_reject_invalid_url_in_payload(self):
        # Given
        invalid_url = "thisIsInvalidUrl.com"
        summary = "This is a test generated summary"
        # When
        with pytest.raises(ValueError) as error:
            SummaryWrite(url=invalid_url, summary=summary)

        assert any(issue["loc"] == ("url",) for issue in error.value.errors())

    def test_reject_invalid_summary_in_payload(self):
        url = "https://www.testexampleurl.com/"
        summary = ""
        with pytest.raises(ValueError) as error:
            SummaryWrite(url=url, summary=summary)

        assert any(issue["loc"] == ("summary",) for issue in error.value.errors())

    def test_valid_summary_read(self):
        id = uuid4()
        url = "https://www.testexampleurl.com/"
        summary = "This is a test generated summary"
        created_at = datetime.now(tz=UTC)
        updated_at = datetime.now(tz=UTC)

        res = SummaryRead(
            id=id,
            created_at=created_at,
            updated_at=updated_at,
            url=url,
            summary=summary,
            ai_summary=None,
            ai_task_status="pending",
            processed_at=None,
        )

        assert res.id == id
        assert res.created_at == created_at
        assert res.updated_at == updated_at
        assert str(res.url) == url
        assert str(res.summary) == summary
        assert res.ai_summary is None
        assert res.ai_task_status == "pending"
        assert res.processed_at is None
