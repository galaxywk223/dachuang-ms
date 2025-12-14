"""
数据字典模型定义
"""

from django.db import models


class DictionaryType(models.Model):
    """
    数据字典类型模型
    用于管理各种下拉选项的类型定义
    """

    code = models.CharField(
        max_length=50, unique=True, verbose_name="字典类型编码", db_index=True
    )
    name = models.CharField(max_length=100, verbose_name="字典类型名称")
    description = models.TextField(blank=True, default="", verbose_name="描述")
    is_system = models.BooleanField(
        default=False, verbose_name="系统内置", help_text="系统内置字典类型不可删除"
    )
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "dictionary_types"
        verbose_name = "字典类型"
        verbose_name_plural = verbose_name
        ordering = ["code"]

    def __str__(self):
        return f"{self.name} ({self.code})"


class DictionaryItem(models.Model):
    """
    数据字典条目模型
    存储具体的选项值
    """

    dict_type = models.ForeignKey(
        DictionaryType,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="字典类型",
    )
    value = models.CharField(max_length=50, verbose_name="选项值", db_index=True)
    label = models.CharField(max_length=100, verbose_name="显示名称")
    sort_order = models.IntegerField(default=0, verbose_name="排序")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    extra_data = models.JSONField(
        null=True, blank=True, verbose_name="扩展数据", help_text="JSON格式的额外配置"
    )
    description = models.CharField(
        max_length=255, blank=True, default="", verbose_name="说明"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "dictionary_items"
        verbose_name = "字典条目"
        verbose_name_plural = verbose_name
        ordering = ["dict_type", "sort_order", "id"]
        unique_together = [["dict_type", "value"]]
        indexes = [
            models.Index(fields=["dict_type", "is_active"]),
        ]

    def __str__(self):
        return f"{self.dict_type.code}: {self.label} ({self.value})"
