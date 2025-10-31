"""
通知模型定义
"""

from django.db import models
from django.conf import settings


class Notification(models.Model):
    """
    通知模型
    """

    class NotificationType(models.TextChoices):
        SYSTEM = "SYSTEM", "系统通知"
        PROJECT = "PROJECT", "项目通知"
        REVIEW = "REVIEW", "审核通知"

    # 基本信息
    title = models.CharField(max_length=200, verbose_name="通知标题")
    content = models.TextField(verbose_name="通知内容")
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM,
        verbose_name="通知类型",
    )

    # 接收人
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="接收人",
    )

    # 关联对象（可选）
    related_project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="关联项目",
    )

    # 状态
    is_read = models.BooleanField(default=False, verbose_name="是否已读")
    read_at = models.DateTimeField(null=True, blank=True, verbose_name="阅读时间")

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = "notifications"
        verbose_name = "通知"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "is_read"]),
        ]

    def __str__(self):
        return f"{self.title} - {self.recipient.real_name}"
