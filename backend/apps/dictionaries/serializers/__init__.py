"""
数据字典序列化器
"""

from rest_framework import serializers
from ..models import DictionaryType, DictionaryItem


class DictionaryItemSerializer(serializers.ModelSerializer):
    """
    字典条目序列化器
    """

    class Meta:
        model = DictionaryItem
        fields = [
            "id",
            "dict_type",
            "value",
            "label",
            "sort_order",
            "is_active",
            "extra_data",
            "description",
            "template_file",
        ]
        read_only_fields = ["id"]


class DictionaryTypeSerializer(serializers.ModelSerializer):
    """
    字典类型序列化器（不包含条目）
    """

    class Meta:
        model = DictionaryType
        fields = [
            "id",
            "code",
            "name",
            "description",
            "is_system",
            "is_active",
        ]
        read_only_fields = ["id", "is_system"]


class DictionaryTypeDetailSerializer(serializers.ModelSerializer):
    """
    字典类型详情序列化器（包含条目）
    """

    items = DictionaryItemSerializer(many=True, read_only=True)

    class Meta:
        model = DictionaryType
        fields = [
            "id",
            "code",
            "name",
            "description",
            "is_system",
            "is_active",
            "items",
        ]
        read_only_fields = ["id", "is_system"]


class DictionaryBatchSerializer(serializers.Serializer):
    """
    批量获取字典数据的序列化器
    """

    codes = serializers.ListField(
        child=serializers.CharField(max_length=50, allow_null=True, allow_blank=False),
        required=False,
        default=list,
        help_text="字典类型编码列表",
    )

    def validate_codes(self, codes):
        cleaned = []
        seen = set()
        for code in codes or []:
            if not isinstance(code, str):
                continue
            code = code.strip()
            if not code or code in seen:
                continue
            seen.add(code)
            cleaned.append(code)
        return cleaned


class DictionaryItemSimpleSerializer(serializers.ModelSerializer):
    """
    简化的字典条目序列化器（仅包含value和label）
    用于前端下拉框
    """

    class Meta:
        model = DictionaryItem
        fields = ["id", "value", "label", "extra_data"]
