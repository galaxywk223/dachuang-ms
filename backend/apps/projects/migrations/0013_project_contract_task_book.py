from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0012_project_batch"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="contract_file",
            field=models.FileField(
                blank=True,
                max_length=255,
                null=True,
                upload_to="contracts/",
                verbose_name="项目合同",
            ),
        ),
        migrations.AddField(
            model_name="project",
            name="task_book_file",
            field=models.FileField(
                blank=True,
                max_length=255,
                null=True,
                upload_to="task_books/",
                verbose_name="项目任务书",
            ),
        ),
    ]
