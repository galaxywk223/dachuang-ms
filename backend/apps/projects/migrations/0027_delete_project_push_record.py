from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("projects", "0026_delete_project_progress"),
    ]

    operations = [
        migrations.DeleteModel(
            name="ProjectPushRecord",
        ),
    ]
