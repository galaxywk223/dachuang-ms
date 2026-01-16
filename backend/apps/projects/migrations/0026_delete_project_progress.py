from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("projects", "0025_delete_budget_change_request"),
    ]

    operations = [
        migrations.DeleteModel(
            name="ProjectProgress",
        ),
    ]
