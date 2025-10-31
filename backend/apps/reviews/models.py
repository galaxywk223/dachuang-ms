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
        CLOSURE = "CLOSURE", "结题审核"

    class ReviewLevel(models.TextChoices):
        LEVEL2 = "LEVEL2", "二级审核"
        LEVEL1 = "LEVEL1", "一级审核"

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
    review_type = models.CharField(
        max_length=20, choices=ReviewType.choices, verbose_name="审核类型"
    )
    review_level = models.CharField(
        max_length=20, choices=ReviewLevel.choices, verbose_name="审核级别"
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
