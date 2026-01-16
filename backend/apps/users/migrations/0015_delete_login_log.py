from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0014_add_expert_flags"),
    ]

    operations = [
        migrations.DeleteModel(
            name="LoginLog",
        ),
    ]
