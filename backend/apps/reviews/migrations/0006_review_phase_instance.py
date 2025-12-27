from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0015_project_phase_instance"),
        ("reviews", "0005_expertgroup_scope_alter_review_review_level"),
    ]

    operations = [
        migrations.AddField(
            model_name="review",
            name="phase_instance",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="reviews",
                to="projects.projectphaseinstance",
                verbose_name="关联阶段轮次",
            ),
        ),
    ]

