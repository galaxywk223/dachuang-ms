from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("projects", "0022_projectphaseinstance_current_node_id"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="project",
            name="discipline",
        ),
    ]
