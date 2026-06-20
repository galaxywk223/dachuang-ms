from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0014_project_expected_results_and_achievement_extra"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ProjectPhaseInstance",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("phase", models.CharField(choices=[("APPLICATION", "立项"), ("MID_TERM", "中期"), ("CLOSURE", "结题")], max_length=20, verbose_name="阶段")),
                ("attempt_no", models.PositiveIntegerField(default=1, verbose_name="轮次")),
                ("step", models.CharField(default="", max_length=50, verbose_name="当前环节")),
                ("state", models.CharField(choices=[("IN_PROGRESS", "进行中"), ("RETURNED", "已退回"), ("COMPLETED", "已完成")], default="IN_PROGRESS", max_length=20, verbose_name="状态")),
                ("return_to", models.CharField(blank=True, choices=[("STUDENT", "退回学生"), ("TEACHER", "退回导师")], default="", max_length=20, verbose_name="退回对象")),
                ("returned_reason", models.TextField(blank=True, default="", verbose_name="退回原因")),
                ("returned_at", models.DateTimeField(blank=True, null=True, verbose_name="退回时间")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="创建时间")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="更新时间")),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="created_phase_instances", to=settings.AUTH_USER_MODEL, verbose_name="创建人")),
                ("project", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="phase_instances", to="projects.project", verbose_name="项目")),
            ],
            options={
                "verbose_name": "项目阶段实例",
                "verbose_name_plural": "项目阶段实例",
                "db_table": "project_phase_instances",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="projectphaseinstance",
            constraint=models.UniqueConstraint(fields=("project", "phase", "attempt_no"), name="uniq_project_phase_attempt"),
        ),
    ]

