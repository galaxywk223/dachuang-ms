from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("system_settings", "0018_change_allowed_reject_to_single"),
    ]

    operations = [
        migrations.DeleteModel(
            name="AdminAssignment",
        ),
    ]
