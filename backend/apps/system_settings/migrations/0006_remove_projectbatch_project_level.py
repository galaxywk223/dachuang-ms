from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("system_settings", "0005_alter_projectbatch_id"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="projectbatch",
            name="project_level",
        ),
    ]
