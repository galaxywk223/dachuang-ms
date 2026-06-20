from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("reviews", "0006_review_phase_instance"),
        ("system_settings", "0008_workflow_review_templates"),
    ]

    operations = [
        migrations.AddField(
            model_name="review",
            name="score_details",
            field=models.JSONField(blank=True, default=list, verbose_name="评分明细"),
        ),
        migrations.AddField(
            model_name="review",
            name="review_template",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="reviews", to="system_settings.reviewtemplate", verbose_name="评审模板"),
        ),
    ]
