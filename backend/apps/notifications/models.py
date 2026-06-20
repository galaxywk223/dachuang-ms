# mypy: disable-error-code=var-annotated
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


class PlatformNotice(models.Model):
    class NoticeStatus(models.TextChoices):
        DRAFT = "DRAFT", "草稿"
        PUBLISHED = "PUBLISHED", "已发布"

    title = models.CharField(max_length=200, verbose_name="公告标题")
    content = models.TextField(verbose_name="公告内容")
    target_roles = models.JSONField(default=list, blank=True, verbose_name="可见角色")
    status = models.CharField(
        max_length=20,
        choices=NoticeStatus.choices,
        default=NoticeStatus.PUBLISHED,
        verbose_name="状态",
    )
    is_pinned = models.BooleanField(default=False, verbose_name="是否置顶")
    published_at = models.DateTimeField(null=True, blank=True, verbose_name="发布时间")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_platform_notices",
        verbose_name="创建人",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "platform_notices"
        verbose_name = "平台公告"
        verbose_name_plural = verbose_name
        ordering = ["-is_pinned", "-published_at", "-created_at"]

    def __str__(self):
        return self.title


class PlatformMaterial(models.Model):
    title = models.CharField(max_length=200, verbose_name="资料名称")
    description = models.TextField(blank=True, verbose_name="资料说明")
    category = models.CharField(max_length=50, blank=True, verbose_name="资料分类")
    target_roles = models.JSONField(default=list, blank=True, verbose_name="可见角色")
    file = models.FileField(
        upload_to="materials/",
        blank=True,
        null=True,
        max_length=255,
        verbose_name="资料文件",
    )
    external_url = models.URLField(blank=True, verbose_name="外部链接")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    download_count = models.PositiveIntegerField(default=0, verbose_name="下载次数")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_platform_materials",
        verbose_name="创建人",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "platform_materials"
        verbose_name = "资料下载"
        verbose_name_plural = verbose_name
        ordering = ["category", "-created_at"]

    def __str__(self):
        return self.title
