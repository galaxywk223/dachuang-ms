from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0019_project_recycle_bin"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="discipline",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="projects_discipline", to="dictionaries.dictionaryitem", verbose_name="学科分类"),
        ),
    ]
