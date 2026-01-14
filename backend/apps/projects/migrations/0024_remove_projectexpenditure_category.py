# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0023_remove_project_discipline'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='projectexpenditure',
            name='category',
        ),
    ]
