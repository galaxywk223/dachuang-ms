from django.db import migrations, models


def migrate_reviewing_to_active(apps, schema_editor):
    ProjectBatch = apps.get_model("system_settings", "ProjectBatch")
    ProjectBatch.objects.filter(status="reviewing").update(status="active")


class Migration(migrations.Migration):
    dependencies = [
        ("system_settings", "0006_remove_projectbatch_project_level"),
    ]

    operations = [
        migrations.AlterField(
            model_name="projectbatch",
            name="status",
            field=models.CharField(
                choices=[
                    ("draft", "草稿"),
                    ("active", "进行中"),
                    ("finished", "已结束"),
                    ("archived", "已归档"),
                ],
                default="draft",
                max_length=20,
                verbose_name="批次状态",
            ),
        ),
        migrations.RunPython(migrate_reviewing_to_active, migrations.RunPython.noop),
    ]
