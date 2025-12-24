from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("system_settings", "0002_project_batch_and_settings_batch"),
        ("projects", "0011_project_archive_push"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="batch",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="projects",
                to="system_settings.projectbatch",
                verbose_name="项目批次",
            ),
        ),
    ]
