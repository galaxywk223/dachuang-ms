from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0032_change_review_workflow_node"),
        ("system_settings", "0018_change_allowed_reject_to_single"),
    ]

    operations = [
        migrations.AddField(
            model_name="projectexpenditure",
            name="leader_review_status",
            field=models.CharField(
                choices=[
                    ("PENDING", "待负责人审核"),
                    ("APPROVED", "负责人通过"),
                    ("REJECTED", "负责人驳回"),
                    ("SKIPPED", "无需负责人审核"),
                ],
                default="SKIPPED",
                max_length=20,
                verbose_name="负责人审核状态",
            ),
        ),
        migrations.AddField(
            model_name="projectexpenditure",
            name="leader_reviewed_at",
            field=models.DateTimeField(
                blank=True, null=True, verbose_name="负责人审核时间"
            ),
        ),
        migrations.AddField(
            model_name="projectexpenditure",
            name="leader_review_comment",
            field=models.TextField(blank=True, verbose_name="负责人审核意见"),
        ),
        migrations.AddField(
            model_name="projectexpenditure",
            name="leader_reviewed_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="leader_reviewed_expenditures",
                to=settings.AUTH_USER_MODEL,
                verbose_name="负责人审核人",
            ),
        ),
        migrations.AddField(
            model_name="projectexpenditure",
            name="current_node_id",
            field=models.IntegerField(
                blank=True,
                help_text="关联到 WorkflowNode.id，用于经费流程",
                null=True,
                verbose_name="当前流程节点ID",
            ),
        ),
        migrations.CreateModel(
            name="ProjectExpenditureReview",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PENDING", "待审核"),
                            ("APPROVED", "审核通过"),
                            ("REJECTED", "审核不通过"),
                        ],
                        default="PENDING",
                        max_length=20,
                        verbose_name="审核状态",
                    ),
                ),
                ("comments", models.TextField(blank=True, verbose_name="审核意见")),
                (
                    "reviewed_at",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="审核时间"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="创建时间"),
                ),
                (
                    "expenditure",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reviews",
                        to="projects.projectexpenditure",
                        verbose_name="经费支出",
                    ),
                ),
                (
                    "reviewer",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="审核人",
                    ),
                ),
                (
                    "workflow_node",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="expenditure_reviews",
                        to="system_settings.workflownode",
                        verbose_name="关联工作流节点",
                    ),
                ),
            ],
            options={
                "verbose_name": "经费审核",
                "verbose_name_plural": "经费审核",
                "db_table": "project_expenditure_reviews",
                "ordering": ["-created_at"],
            },
        ),
    ]

