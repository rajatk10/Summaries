import logging
from collections import Counter
from datetime import UTC, datetime
from uuid import UUID

import httpx
import trafilatura
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from starlette.concurrency import run_in_threadpool

from app.models import Summary

logger = logging.getLogger(__name__)


async def fetch_and_clean_text(url: str) -> str:
    logger.info("Fetching %s and cleaning text", url)
    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        response = await client.get(url)
        response.raise_for_status()

    cleaned_text = await run_in_threadpool(
        trafilatura.extract,
        response.content,
        url=url,
        include_comments=False,
        include_tables=False,
    )
    if not cleaned_text:
        raise ValueError("Could not extract article text")
    return cleaned_text


def generate_nlp_summary(text: str, num_sentences: int = 3) -> str:
    logger.info("Generating NLP summary using NLTK")
    sentences = sent_tokenize(text)
    if len(sentences) <= num_sentences:
        logger.info(
            "Found %d sentences, returning the original text",
            len(sentences),
        )
        return text

    stop_words = set(stopwords.words("english"))
    words = [
        word.lower()
        for word in word_tokenize(text.lower())
        if word.isalnum() and word not in stop_words
    ]

    word_freq = Counter(words)
    logger.info("Found %d unique words", len(word_freq))
    sentence_scores: dict[str, int] = {}

    for sentence in sentences:
        for word in word_tokenize(sentence.lower()):
            if word in word_freq:
                sentence_scores[sentence] = (
                    sentence_scores.get(sentence, 0) + word_freq[word]
                )

    if not sentence_scores:
        return " ".join(sentences[:num_sentences])

    top_sentences = sorted(
        sentence_scores,
        key=lambda sentence: sentence_scores[sentence],
        reverse=True,
    )[:num_sentences]
    logger.info("Processed %d sentences using NLTK", len(top_sentences))
    return " ".join(top_sentences)


async def process_nlp_summary_task(summary_id: UUID, url: str) -> None:
    logger.info("Processing background task summary for id=%s", summary_id)
    summary = await Summary.get_or_none(id=summary_id)
    if summary is None:
        logger.error("Could not find summary for id=%s", summary_id)
        return

    try:
        raw_text = await fetch_and_clean_text(url)
        nlp_summary = await run_in_threadpool(generate_nlp_summary, raw_text)
    except Exception:
        logger.exception("Could not process NLP summary for id=%s", summary_id)
        summary.ai_summary = None
        summary.ai_task_status = "failed"
        summary.processed_at = datetime.now(UTC)
        await summary.save()
        return

    summary.ai_summary = nlp_summary
    summary.ai_task_status = "completed"
    summary.processed_at = datetime.now(UTC)
    await summary.save()
    logger.info("Successfully processed background task summary for id=%s", summary_id)
