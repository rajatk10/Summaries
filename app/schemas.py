from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class SummaryWrite(BaseModel):
    model_config = ConfigDict(extra="forbid")
    url: HttpUrl
    summary: str = Field(min_length=1)


class SummaryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    url: HttpUrl
    summary: str
    created_at: datetime
    updated_at: datetime
    ai_summary: str | None
    ai_task_status: Literal["pending", "completed", "failed"]
    processed_at: datetime | None
