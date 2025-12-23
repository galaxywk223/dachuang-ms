"""
系统设置模型
"""

from django.db import models
from django.conf import settings

from apps.dictionaries.models import DictionaryItem


class SystemSetting(models.Model):
    """
    系统配置（JSON）
    """

    code = models.CharField(max_length=50, unique=True, verbose_name="配置编码")
    name = models.CharField(max_length=100, verbose_name="配置名称")
    data = models.JSONField(default=dict, verbose_name="配置数据")
    is_locked = models.BooleanField(default=False, verbose_name="是否锁定")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_settings",
        verbose_name="更新人",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "system_settings"
        verbose_name = "系统配置"
        verbose_name_plural = verbose_name
        ordering = ["code"]

    def __str__(self):
        return f"{self.name}({self.code})"


class CertificateSetting(models.Model):
    """
    结题证书配置
    """

    name = models.CharField(max_length=100, verbose_name="模板名称")
    school_name = models.CharField(max_length=100, verbose_name="学校名称")
    issuer_name = models.CharField(max_length=100, verbose_name="证书发放单位")
    template_code = models.CharField(max_length=50, default="DEFAULT", verbose_name="模板编码")
    background_image = models.ImageField(
        upload_to="certificates/backgrounds/",
        null=True,
        blank=True,
        verbose_name="证书底图",
    )
    seal_image = models.ImageField(
        upload_to="certificates/seals/",
        null=True,
        blank=True,
        verbose_name="电子印章",
    )
    style_config = models.JSONField(default=dict, verbose_name="样式配置")
    project_level = models.ForeignKey(
        DictionaryItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="certificate_level_settings",
        verbose_name="适用项目级别",
    )
    project_category = models.ForeignKey(
        DictionaryItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="certificate_category_settings",
        verbose_name="适用项目类别",
    )
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_certificates",
        verbose_name="更新人",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "certificate_settings"
        verbose_name = "结题证书配置"
        verbose_name_plural = verbose_name
        ordering = ["-updated_at"]

    def __str__(self):
        return self.name
