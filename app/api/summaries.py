import logging
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, HTTPException, Response, status

from app.models import Summary
from app.nlp.ai_summary import process_nlp_summary_task
from app.schemas import SummaryRead, SummaryWrite

router = APIRouter(prefix="/summaries", tags=["summaries"])

logger = logging.getLogger(__name__)


async def fetch_summary(summary_id: UUID) -> Summary:
    logger.info(f"Fetching summary with id {summary_id}")
    summary = await Summary.get_or_none(id=summary_id)
    if summary is None:
        logger.error(f"Summary with id {summary_id} not found")
        raise HTTPException(status_code=404, detail="Summary not found")
    return summary


async def fetch_all_summaries() -> list[Summary]:
    return await Summary.all()


@router.get("", response_model=list[SummaryRead])
async def get_summaries() -> list[Summary]:
    logger.info("HTTP GET - '/summaries' -  ALL summaries")
    return await fetch_all_summaries()


@router.get("/{summary_id}", response_model=SummaryRead)
async def get_summary(summary_id: UUID) -> Summary:
    logger.info(f"HTTP GET - '/summaries/{summary_id}'")
    return await fetch_summary(summary_id)


@router.post("", response_model=SummaryRead, status_code=status.HTTP_201_CREATED)
async def create_summary(
    payload: SummaryWrite,
    background_tasks: BackgroundTasks,
) -> Summary:
    logger.info("HTTP POST - '/summaries/', Creating summary with payload")
    summary = await Summary.create(
        url=str(payload.url),
        summary=str(payload.summary),
        ai_task_status="pending",
    )
    background_tasks.add_task(
        process_nlp_summary_task,
        summary.id,
        summary.url,
    )
    return summary


@router.put("/{summary_id}", response_model=SummaryRead)
async def update_summary(
    payload: SummaryWrite, summary_id: UUID, background_task: BackgroundTasks
) -> Summary:
    logger.info(f"HTTP PUT - '/summaries/{summary_id}', Updating summary with payload")
    summary = await fetch_summary(summary_id)
    logger.info(
        f"Setting Summary URL to {payload.url} and summary to {payload.summary}"
    )
    summary.url = str(payload.url)
    summary.summary = str(payload.summary)
    summary.ai_task_status = "pending"
    summary.ai_summary = None
    summary.processed_at = None
    await summary.save()
    background_task.add_task(process_nlp_summary_task, summary.id, summary.url)
    logger.info(f"Setting updated summary id : {summary_id} ")
    return summary


@router.delete("/{summary_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_summary(summary_id: UUID) -> Response:
    summary = await fetch_summary(summary_id)

    await summary.delete()
    logger.info(f"Deleted summary with id {summary_id}")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
