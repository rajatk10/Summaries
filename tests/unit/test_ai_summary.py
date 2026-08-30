from unittest.mock import AsyncMock

import pytest

from app.nlp import ai_summary


def test_short_text_is_returned_without_summarizing(monkeypatch):
    # Given
    text = "First sentence. Second sentence."
    monkeypatch.setattr(
        ai_summary,
        "sent_tokenize",
        lambda value: ["First sentence.", "Second sentence."],
    )
    # When
    result = ai_summary.generate_nlp_summary(text, num_sentences=3)
    # Then
    assert result == text


@pytest.mark.asyncio
async def test_background_task_marks_summary_completed(
    summaries_record,
    monkeypatch,
):
    # Given
    get_or_none = AsyncMock(return_value=summaries_record)
    fetch_and_clean_text = AsyncMock(return_value="Extracted article text.")
    run_in_threadpool = AsyncMock(return_value="Generated summary.")
    monkeypatch.setattr(ai_summary.Summary, "get_or_none", get_or_none)
    monkeypatch.setattr(
        ai_summary,
        "fetch_and_clean_text",
        fetch_and_clean_text,
    )
    monkeypatch.setattr(ai_summary, "run_in_threadpool", run_in_threadpool)

    # When
    await ai_summary.process_nlp_summary_task(
        summaries_record.id,
        summaries_record.url,
    )
    # Then
    assert summaries_record.ai_summary == "Generated summary."
    assert summaries_record.ai_task_status == "completed"
    assert summaries_record.processed_at is not None
    summaries_record.save.assert_awaited_once()


@pytest.mark.asyncio
async def test_background_task_marks_summary_failed(
    summaries_record,
    monkeypatch,
):
    # Given
    get_or_none = AsyncMock(return_value=summaries_record)
    fetch_and_clean_text = AsyncMock(side_effect=RuntimeError("fetch failed"))
    monkeypatch.setattr(ai_summary.Summary, "get_or_none", get_or_none)
    monkeypatch.setattr(
        ai_summary,
        "fetch_and_clean_text",
        fetch_and_clean_text,
    )
    # When
    await ai_summary.process_nlp_summary_task(
        summaries_record.id,
        summaries_record.url,
    )
    assert summaries_record.ai_summary is None
    assert summaries_record.ai_task_status == "failed"
    assert summaries_record.processed_at is not None
    summaries_record.save.assert_awaited_once()
