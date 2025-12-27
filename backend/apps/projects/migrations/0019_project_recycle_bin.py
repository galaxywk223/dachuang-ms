from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0018_project_achievement_summary"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ProjectRecycleBin",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("resource_type", models.CharField(choices=[("APPLICATION", "立项申报"), ("MID_TERM", "中期提交"), ("CLOSURE", "结题提交"), ("ACHIEVEMENT", "成果"), ("EXPENDITURE", "经费支出"), ("PROGRESS", "进度记录")], max_length=20, verbose_name="资源类型")),
                ("resource_id", models.IntegerField(blank=True, null=True, verbose_name="原始记录ID")),
                ("payload", models.JSONField(default=dict, verbose_name="数据快照")),
                ("attachments", models.JSONField(default=list, verbose_name="附件清单")),
                ("deleted_at", models.DateTimeField(auto_now_add=True, verbose_name="删除时间")),
                ("restored_at", models.DateTimeField(blank=True, null=True, verbose_name="恢复时间")),
                ("is_restored", models.BooleanField(default=False, verbose_name="是否已恢复")),
                (
                    "deleted_by",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="deleted_recycle_items", to=settings.AUTH_USER_MODEL, verbose_name="删除人"),
                ),
                (
                    "project",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="recycle_items", to="projects.project", verbose_name="项目"),
                ),
                (
                    "restored_by",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="restored_recycle_items", to=settings.AUTH_USER_MODEL, verbose_name="恢复人"),
                ),
            ],
            options={
                "verbose_name": "项目回收站",
                "verbose_name_plural": "项目回收站",
                "db_table": "project_recycle_bin",
                "ordering": ["-deleted_at"],
            },
        ),
    ]
