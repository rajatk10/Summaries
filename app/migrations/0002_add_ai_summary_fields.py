from tortoise import fields, migrations
from tortoise.migrations import operations as ops


class Migration(migrations.Migration):
    dependencies = [("models", "0001_initial")]

    initial = False

    operations = [
        ops.AddField(
            model_name="Summary",
            name="ai_summary",
            field=fields.TextField(null=True, unique=False),
        ),
        ops.AddField(
            model_name="Summary",
            name="ai_task_status",
            field=fields.TextField(default="pending", unique=False),
        ),
        ops.AddField(
            model_name="Summary",
            name="processed_at",
            field=fields.DatetimeField(null=True, auto_now=False, auto_now_add=False),
        ),
    ]
