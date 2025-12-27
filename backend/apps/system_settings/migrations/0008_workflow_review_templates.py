from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("system_settings", "0007_remove_projectbatch_reviewing"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="WorkflowConfig",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, verbose_name="流程名称")),
                ("phase", models.CharField(choices=[("APPLICATION", "立项"), ("MID_TERM", "中期"), ("CLOSURE", "结题")], max_length=20, verbose_name="流程阶段")),
                ("version", models.IntegerField(default=1, verbose_name="版本号")),
                ("description", models.TextField(blank=True, default="", verbose_name="说明")),
                ("is_active", models.BooleanField(default=True, verbose_name="是否启用")),
                ("is_locked", models.BooleanField(default=False, verbose_name="是否锁定")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="创建时间")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="更新时间")),
                (
                    "batch",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="workflow_configs", to="system_settings.projectbatch", verbose_name="所属批次"),
                ),
                (
                    "created_by",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="created_workflows", to=settings.AUTH_USER_MODEL, verbose_name="创建人"),
                ),
                (
                    "updated_by",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="updated_workflows", to=settings.AUTH_USER_MODEL, verbose_name="更新人"),
                ),
            ],
            options={
                "verbose_name": "流程配置",
                "verbose_name_plural": "流程配置",
                "db_table": "workflow_configs",
                "ordering": ["-updated_at"],
                "unique_together": {("phase", "batch", "version")},
            },
        ),
        migrations.CreateModel(
            name="ReviewTemplate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, verbose_name="模板名称")),
                ("review_type", models.CharField(max_length=20, verbose_name="评审类型")),
                ("review_level", models.CharField(max_length=20, verbose_name="评审级别")),
                ("scope", models.CharField(choices=[("COLLEGE", "院级"), ("SCHOOL", "校级")], default="COLLEGE", max_length=20, verbose_name="范围")),
                ("description", models.TextField(blank=True, default="", verbose_name="模板说明")),
                ("notice", models.TextField(blank=True, default="", verbose_name="评审注意事项")),
                ("is_active", models.BooleanField(default=True, verbose_name="是否启用")),
                ("is_locked", models.BooleanField(default=False, verbose_name="是否锁定")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="创建时间")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="更新时间")),
                (
                    "batch",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="review_templates", to="system_settings.projectbatch", verbose_name="所属批次"),
                ),
                (
                    "created_by",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="created_review_templates", to=settings.AUTH_USER_MODEL, verbose_name="创建人"),
                ),
                (
                    "updated_by",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="updated_review_templates", to=settings.AUTH_USER_MODEL, verbose_name="更新人"),
                ),
            ],
            options={
                "verbose_name": "评审模板",
                "verbose_name_plural": "评审模板",
                "db_table": "review_templates",
                "ordering": ["-updated_at"],
            },
        ),
        migrations.CreateModel(
            name="ReviewTemplateItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200, verbose_name="评分项")),
                ("description", models.TextField(blank=True, default="", verbose_name="说明")),
                ("weight", models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name="权重")),
                ("max_score", models.IntegerField(default=100, verbose_name="最高分")),
                ("is_required", models.BooleanField(default=False, verbose_name="是否必填")),
                ("sort_order", models.IntegerField(default=0, verbose_name="排序")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="创建时间")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="更新时间")),
                (
                    "template",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="items", to="system_settings.reviewtemplate", verbose_name="评审模板"),
                ),
            ],
            options={
                "verbose_name": "评审模板评分项",
                "verbose_name_plural": "评审模板评分项",
                "db_table": "review_template_items",
                "ordering": ["sort_order", "id"],
            },
        ),
        migrations.CreateModel(
            name="WorkflowNode",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=50, verbose_name="节点编码")),
                ("name", models.CharField(max_length=100, verbose_name="节点名称")),
                ("node_type", models.CharField(choices=[("REVIEW", "审核"), ("EXPERT_REVIEW", "专家评审"), ("APPROVAL", "管理员确认")], max_length=20, verbose_name="节点类型")),
                ("role", models.CharField(choices=[("TEACHER", "导师"), ("LEVEL2_ADMIN", "二级管理员"), ("LEVEL1_ADMIN", "一级管理员"), ("EXPERT", "专家")], max_length=20, verbose_name="角色")),
                ("review_level", models.CharField(blank=True, default="", max_length=20, verbose_name="审核级别")),
                ("scope", models.CharField(blank=True, default="", max_length=20, verbose_name="专家范围")),
                ("return_policy", models.CharField(choices=[("NONE", "不允许退回"), ("STUDENT", "退回学生"), ("TEACHER", "退回导师"), ("PREVIOUS", "退回上一级")], default="NONE", max_length=20, verbose_name="退回规则")),
                ("notice", models.TextField(blank=True, default="", verbose_name="评审注意事项")),
                ("sort_order", models.IntegerField(default=0, verbose_name="排序")),
                ("is_active", models.BooleanField(default=True, verbose_name="是否启用")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="创建时间")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="更新时间")),
                (
                    "review_template",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="workflow_nodes", to="system_settings.reviewtemplate", verbose_name="关联评审模板"),
                ),
                (
                    "workflow",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="nodes", to="system_settings.workflowconfig", verbose_name="流程配置"),
                ),
            ],
            options={
                "verbose_name": "流程节点",
                "verbose_name_plural": "流程节点",
                "db_table": "workflow_nodes",
                "ordering": ["sort_order", "id"],
                "unique_together": {("workflow", "code")},
            },
        ),
    ]
