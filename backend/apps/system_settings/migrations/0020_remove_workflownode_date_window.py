from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("system_settings", "0019_delete_admin_assignment"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="workflownode",
            name="start_date",
        ),
        migrations.RemoveField(
            model_name="workflownode",
            name="end_date",
        ),
    ]
