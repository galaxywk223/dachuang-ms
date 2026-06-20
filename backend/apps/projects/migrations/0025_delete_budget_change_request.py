from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("projects", "0024_remove_projectexpenditure_category"),
    ]

    operations = [
        migrations.DeleteModel(
            name="BudgetChangeRequest",
        ),
    ]
