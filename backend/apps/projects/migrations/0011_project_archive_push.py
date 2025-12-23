from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0010_project_status_terminated"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProjectArchive",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("snapshot", models.JSONField(default=dict, verbose_name="项目快照")),
                ("attachments", models.JSONField(default=list, verbose_name="附件清单")),
                ("archived_at", models.DateTimeField(auto_now_add=True, verbose_name="归档时间")),
                ("project", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="archive", to="projects.project", verbose_name="项目")),
            ],
            options={
                "verbose_name": "项目归档",
                "verbose_name_plural": "项目归档",
                "db_table": "project_archives",
                "ordering": ["-archived_at"],
            },
        ),
        migrations.CreateModel(
            name="ProjectPushRecord",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("target", models.CharField(max_length=100, verbose_name="目标平台")),
                ("payload", models.JSONField(default=dict, verbose_name="推送数据")),
                ("response_message", models.TextField(blank=True, verbose_name="响应信息")),
                ("status", models.CharField(choices=[("PENDING", "待推送"), ("SUCCESS", "推送成功"), ("FAILED", "推送失败")], default="PENDING", max_length=20, verbose_name="推送状态")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="创建时间")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="更新时间")),
                ("project", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="push_records", to="projects.project", verbose_name="项目")),
            ],
            options={
                "verbose_name": "项目推送记录",
                "verbose_name_plural": "项目推送记录",
                "db_table": "project_push_records",
                "ordering": ["-created_at"],
            },
        ),
    ]
