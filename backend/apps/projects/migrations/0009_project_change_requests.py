from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0008_project_approved_budget"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ProjectChangeRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("request_type", models.CharField(choices=[("CHANGE", "项目变更"), ("TERMINATION", "项目终止"), ("EXTENSION", "项目延期")], max_length=20, verbose_name="申请类型")),
                ("reason", models.TextField(blank=True, verbose_name="申请原因")),
                ("change_data", models.JSONField(blank=True, null=True, verbose_name="变更内容")),
                ("requested_end_date", models.DateField(blank=True, null=True, verbose_name="延期至")),
                ("attachment", models.FileField(blank=True, max_length=255, null=True, upload_to="change_requests/", verbose_name="附件")),
                ("status", models.CharField(choices=[("DRAFT", "草稿"), ("SUBMITTED", "已提交"), ("TEACHER_REVIEWING", "导师审核中"), ("LEVEL2_REVIEWING", "二级审核中"), ("LEVEL1_REVIEWING", "一级审核中"), ("APPROVED", "审核通过"), ("REJECTED", "审核不通过")], default="DRAFT", max_length=30, verbose_name="状态")),
                ("submitted_at", models.DateTimeField(blank=True, null=True, verbose_name="提交时间")),
                ("reviewed_at", models.DateTimeField(blank=True, null=True, verbose_name="审核时间")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="创建时间")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="更新时间")),
                ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="created_change_requests", to=settings.AUTH_USER_MODEL, verbose_name="申请人")),
                ("project", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="change_requests", to="projects.project", verbose_name="项目")),
            ],
            options={
                "verbose_name": "项目变更申请",
                "verbose_name_plural": "项目变更申请",
                "db_table": "project_change_requests",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="ProjectChangeReview",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("review_level", models.CharField(choices=[("TEACHER", "导师审核"), ("LEVEL2", "二级审核"), ("LEVEL1", "一级审核")], max_length=20, verbose_name="审核级别")),
                ("status", models.CharField(choices=[("PENDING", "待审核"), ("APPROVED", "审核通过"), ("REJECTED", "审核不通过")], default="PENDING", max_length=20, verbose_name="审核状态")),
                ("comments", models.TextField(blank=True, verbose_name="审核意见")),
                ("reviewed_at", models.DateTimeField(blank=True, null=True, verbose_name="审核时间")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="创建时间")),
                ("change_request", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="reviews", to="projects.projectchangerequest", verbose_name="变更申请")),
                ("reviewer", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name="审核人")),
            ],
            options={
                "verbose_name": "项目变更审核",
                "verbose_name_plural": "项目变更审核",
                "db_table": "project_change_reviews",
                "ordering": ["-created_at"],
            },
        ),
    ]
