from django.db import migrations, models


def set_batch_status(apps, schema_editor):
    ProjectBatch = apps.get_model("system_settings", "ProjectBatch")
    ProjectBatch.objects.filter(is_current=True).update(status="running")
    ProjectBatch.objects.filter(is_current=False).update(status="published")


def rollback_batch_status(apps, schema_editor):
    ProjectBatch = apps.get_model("system_settings", "ProjectBatch")
    ProjectBatch.objects.update(status="draft")


class Migration(migrations.Migration):

    dependencies = [
        ("system_settings", "0002_project_batch_and_settings_batch"),
    ]

    operations = [
        migrations.AddField(
            model_name="projectbatch",
            name="status",
            field=models.CharField(
                choices=[
                    ("draft", "草稿"),
                    ("published", "已发布"),
                    ("running", "进行中"),
                    ("archived", "已归档"),
                ],
                default="draft",
                max_length=20,
                verbose_name="批次状态",
            ),
        ),
        migrations.RunPython(set_batch_status, rollback_batch_status),
    ]
