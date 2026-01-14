# mypy: disable-error-code=var-annotated
"""
审核模型定义
"""

from django.db import models
from django.conf import settings


class Review(models.Model):
    """
    审核记录模型
    """

    class ReviewType(models.TextChoices):
        APPLICATION = "APPLICATION", "申报审核"
        TASK_BOOK = "TASK_BOOK", "任务书审核"
        MID_TERM = "MID_TERM", "中期审核"
        CLOSURE = "CLOSURE", "结题审核"

    # ReviewLevel 枚举已删除 - 改为动态值，支持任意角色
    # 管理员可在工作流配置中添加任意多个审核角色，无需修改代码

    class ReviewStatus(models.TextChoices):
        PENDING = "PENDING", "待审核"
        APPROVED = "APPROVED", "审核通过"
        REJECTED = "REJECTED", "审核不通过"

    class ClosureRating(models.TextChoices):
        EXCELLENT = "EXCELLENT", "优秀"
        GOOD = "GOOD", "良好"
        QUALIFIED = "QUALIFIED", "合格"
        UNQUALIFIED = "UNQUALIFIED", "不合格"
        DEFERRED = "DEFERRED", "延期"

    # 基本信息
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="项目",
    )
    phase_instance = models.ForeignKey(
        "projects.ProjectPhaseInstance",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviews",
        verbose_name="关联阶段轮次",
    )
    review_type = models.CharField(
        max_length=20, choices=ReviewType.choices, verbose_name="审核类型"
    )
    # review_level 改为纯CharField，允许任意角色值
    # 值从工作流节点的 review_level 或 role 字段读取
    review_level = models.CharField(
        max_length=50,
        verbose_name="审核级别/角色",
        help_text="动态值，由工作流节点配置决定",
    )

    # 审核人和状态
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="审核人",
    )
    status = models.CharField(
        max_length=20,
        choices=ReviewStatus.choices,
        default=ReviewStatus.PENDING,
        verbose_name="审核状态",
    )

    # 审核意见
    comments = models.TextField(blank=True, verbose_name="审核意见")
    score = models.IntegerField(null=True, blank=True, verbose_name="评分")
    score_details = models.JSONField(default=list, blank=True, verbose_name="评分明细")

    # 结题审核专用字段
    closure_rating = models.CharField(
        max_length=20,
        choices=ClosureRating.choices,
        null=True,
        blank=True,
        verbose_name="结题评价",
    )

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name="审核时间")

    class Meta:
        db_table = "reviews"
        verbose_name = "审核记录"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["project", "review_level"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.project.project_no} - {self.get_review_type_display()} - {self.get_review_level_display()}"


class ExpertGroup(models.Model):
    """
    专家组模型
    """

    name = models.CharField(max_length=100, verbose_name="专家组名称")
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        limit_choices_to={"role_fk__code": "EXPERT"},
        related_name="expert_groups",
        verbose_name="专家成员",
    )
    # 区分专家组级别：SCHOOL (校级), COLLEGE (院级)
    scope = models.CharField(
        max_length=20, default="COLLEGE", verbose_name="专家组级别"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_expert_groups",
        verbose_name="创建人",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "expert_groups"
        verbose_name = "专家组"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
