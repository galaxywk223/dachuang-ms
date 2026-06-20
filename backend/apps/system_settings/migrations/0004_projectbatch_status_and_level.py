from django.db import migrations, models
import django.db.models.deletion


def map_batch_status(apps, schema_editor):
    ProjectBatch = apps.get_model("system_settings", "ProjectBatch")
    mapping = {
        "draft": "draft",
        "published": "active",
        "running": "active",
        "active": "active",
        "reviewing": "reviewing",
        "finished": "finished",
        "archived": "archived",
    }
    for batch in ProjectBatch.objects.all():
        next_status = mapping.get(batch.status, "draft")
        if batch.is_current:
            next_status = "active"
        batch.status = next_status
        batch.save(update_fields=["status"])


def rollback_batch_status(apps, schema_editor):
    ProjectBatch = apps.get_model("system_settings", "ProjectBatch")
    for batch in ProjectBatch.objects.all():
        batch.status = "draft"
        batch.save(update_fields=["status"])


class Migration(migrations.Migration):

    dependencies = [
        ("dictionaries", "0004_seed_project_level_items"),
        ("system_settings", "0003_projectbatch_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="projectbatch",
            name="project_level",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="batch_project_levels",
                to="dictionaries.dictionaryitem",
                verbose_name="项目级别",
            ),
        ),
        migrations.AddField(
            model_name="projectbatch",
            name="is_deleted",
            field=models.BooleanField(default=False, verbose_name="是否删除"),
        ),
        migrations.AlterField(
            model_name="projectbatch",
            name="status",
            field=models.CharField(
                choices=[
                    ("draft", "草稿"),
                    ("active", "进行中"),
                    ("reviewing", "评审中"),
                    ("finished", "已结束"),
                    ("archived", "已归档"),
                ],
                default="draft",
                max_length=20,
                verbose_name="批次状态",
            ),
        ),
        migrations.RunPython(map_batch_status, rollback_batch_status),
    ]
