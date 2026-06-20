from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0013_project_contract_task_book"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="expected_results_data",
            field=models.JSONField(blank=True, default=list, verbose_name="预期成果清单"),
        ),
        migrations.AddField(
            model_name="projectachievement",
            name="extra_data",
            field=models.JSONField(blank=True, default=dict, verbose_name="扩展信息"),
        ),
    ]
