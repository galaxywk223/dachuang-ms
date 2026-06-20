from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0028_alter_projectrecyclebin_resource_type"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="project",
            name="contract_file",
        ),
        migrations.RemoveField(
            model_name="project",
            name="task_book_file",
        ),
    ]
