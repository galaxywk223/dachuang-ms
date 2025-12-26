"""
系统设置序列化器
"""

from rest_framework import serializers

from .models import SystemSetting, CertificateSetting, ProjectBatch
from apps.dictionaries.models import DictionaryItem


class SystemSettingSerializer(serializers.ModelSerializer):
    updated_by_name = serializers.CharField(
        source="updated_by.real_name", read_only=True
    )

    class Meta:
        model = SystemSetting
        fields = [
            "id",
            "code",
            "name",
            "data",
            "batch",
            "is_locked",
            "is_active",
            "updated_by",
            "updated_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "updated_by"]


class ProjectBatchSerializer(serializers.ModelSerializer):
    project_level = serializers.PrimaryKeyRelatedField(
        queryset=DictionaryItem.objects.filter(dict_type__code="project_level"),
        allow_null=True,
        required=False,
    )

    class Meta:
        model = ProjectBatch
        fields = [
            "id",
            "name",
            "year",
            "code",
            "project_level",
            "status",
            "is_current",
            "is_active",
            "is_deleted",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "is_deleted"]


class CertificateSettingSerializer(serializers.ModelSerializer):
    updated_by_name = serializers.CharField(
        source="updated_by.real_name", read_only=True
    )
    background_image_url = serializers.SerializerMethodField()
    seal_image_url = serializers.SerializerMethodField()

    class Meta:
        model = CertificateSetting
        fields = [
            "id",
            "name",
            "school_name",
            "issuer_name",
            "template_code",
            "background_image",
            "seal_image",
            "background_image_url",
            "seal_image_url",
            "style_config",
            "project_level",
            "project_category",
            "is_active",
            "updated_by",
            "updated_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "updated_by"]

    def _build_file_url(self, file_field):
        if not file_field:
            return ""
        try:
            request = self.context.get("request")
            url = file_field.url
            if request:
                return request.build_absolute_uri(url)
            return url
        except Exception:
            return ""

    def get_background_image_url(self, obj):
        return self._build_file_url(obj.background_image)

    def get_seal_image_url(self, obj):
        return self._build_file_url(obj.seal_image)
