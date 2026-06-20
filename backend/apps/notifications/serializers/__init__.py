"""
通知序列化器
"""

from pathlib import Path

from django.urls import NoReverseMatch
from rest_framework import serializers
from rest_framework.reverse import reverse

from apps.utils.upload_validation import validate_platform_material_file
from apps.users.models import Role

from ..models import Notification, PlatformMaterial, PlatformNotice


def validate_target_roles(value):
    if value in (None, ""):
        return []
    if not isinstance(value, list):
        raise serializers.ValidationError("可见角色必须为角色代码列表")

    cleaned = []
    seen = set()
    for role_code in value:
        if not isinstance(role_code, str):
            raise serializers.ValidationError("可见角色必须为角色代码列表")
        role_code = role_code.strip()
        if not role_code:
            continue
        if role_code in seen:
            continue
        cleaned.append(role_code)
        seen.add(role_code)

    if not cleaned:
        return []

    existing_codes = set(
        Role.objects.filter(code__in=cleaned, is_active=True).values_list(
            "code", flat=True
        )
    )
    missing_codes = [
        role_code for role_code in cleaned if role_code not in existing_codes
    ]
    if missing_codes:
        raise serializers.ValidationError(
            f"可见角色不存在或已停用: {', '.join(missing_codes)}"
        )
    return cleaned


class NotificationSerializer(serializers.ModelSerializer):
    """
    通知序列化器
    """

    type_display = serializers.CharField(
        source="get_notification_type_display", read_only=True
    )
    notification_type_display = serializers.CharField(
        source="get_notification_type_display", read_only=True
    )
    project_title = serializers.CharField(
        source="related_project.title", read_only=True
    )

    class Meta:
        model = Notification
        fields = [
            "id",
            "title",
            "content",
            "notification_type",
            "type_display",
            "notification_type_display",
            "recipient",
            "related_project",
            "project_title",
            "is_read",
            "read_at",
            "created_at",
        ]
        read_only_fields = ["id", "recipient", "created_at", "read_at"]


class PlatformNoticeSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    created_by_name = serializers.CharField(
        source="created_by.real_name", read_only=True
    )

    class Meta:
        model = PlatformNotice
        fields = [
            "id",
            "title",
            "content",
            "target_roles",
            "status",
            "status_display",
            "is_pinned",
            "published_at",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]

    def validate_target_roles(self, value):
        return validate_target_roles(value)


class PlatformMaterialSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(
        source="created_by.real_name", read_only=True
    )
    file = serializers.FileField(
        required=False, allow_null=True, allow_empty_file=True
    )
    file_url = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()

    class Meta:
        model = PlatformMaterial
        fields = [
            "id",
            "title",
            "description",
            "category",
            "target_roles",
            "file",
            "file_url",
            "file_name",
            "external_url",
            "is_active",
            "download_count",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_by",
            "created_at",
            "updated_at",
            "download_count",
        ]

    def get_file_url(self, obj):
        if not obj.file:
            return ""
        request = self.context.get("request")
        try:
            return reverse("platform-material-download", args=[obj.pk], request=request)
        except NoReverseMatch:
            return f"/api/v1/notifications/materials/{obj.pk}/download/"

    def get_file_name(self, obj):
        if not obj.file:
            return ""
        return Path(obj.file.name).name

    def validate_file(self, value):
        return validate_platform_material_file(value)

    def validate_target_roles(self, value):
        return validate_target_roles(value)
