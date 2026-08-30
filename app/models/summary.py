from typing import ClassVar

from tortoise import fields
from tortoise.models import Model


class Summary(Model):
    id = fields.UUIDField(primary_key=True)
    url = fields.CharField(max_length=2048)
    summary = fields.TextField()
    ai_summary = fields.TextField(null=True)
    ai_task_status = fields.TextField(default="pending")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    processed_at = fields.DatetimeField(null=True)

    class Meta:
        table = "summaries"
        # Use classvar to separate and distinct the ruff format errors
        ordering: ClassVar[list[str]] = ["-created_at"]
