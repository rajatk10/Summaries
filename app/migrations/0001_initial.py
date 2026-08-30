from uuid import uuid4

from tortoise import fields, migrations
from tortoise.migrations import operations as ops


class Migration(migrations.Migration):
    initial = True

    operations = [
        ops.CreateModel(
            name="Summary",
            fields=[
                (
                    "id",
                    fields.UUIDField(
                        primary_key=True, default=uuid4, unique=True, db_index=True
                    ),
                ),
                ("url", fields.CharField(unique=True, max_length=2048)),
                ("summary", fields.TextField(unique=False)),
                ("created_at", fields.DatetimeField(auto_now=False, auto_now_add=True)),
                ("updated_at", fields.DatetimeField(auto_now=True, auto_now_add=False)),
            ],
            options={"table": "summaries", "app": "models", "pk_attr": "id"},
            bases=["Model"],
        ),
    ]
