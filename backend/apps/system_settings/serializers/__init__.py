"""
系统设置序列化器
"""

from pathlib import Path

from django.urls import NoReverseMatch
from rest_framework import serializers
from rest_framework.reverse import reverse

from apps.utils.upload_validation import ValidatedImageField

from ..models import (
    SystemSetting,
    CertificateSetting,
    ProjectBatch,
)


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
    class Meta:
        model = ProjectBatch
        fields = [
            "id",
            "name",
            "year",
            "code",
            "status",
            "is_current",
            "is_active",
            "is_deleted",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "is_deleted"]

    def validate(self, attrs):
        instance = getattr(self, "instance", None)
        new_status = attrs.get("status")
        if not instance and new_status and new_status != ProjectBatch.STATUS_DRAFT:
            raise serializers.ValidationError({"status": "新建批次仅允许草稿状态"})
        if new_status == ProjectBatch.STATUS_ACTIVE:
            active_qs = ProjectBatch.objects.filter(
                status=ProjectBatch.STATUS_ACTIVE, is_active=True, is_deleted=False
            )
            if instance:
                active_qs = active_qs.exclude(id=instance.id)
            if active_qs.exists():
                raise serializers.ValidationError({"status": "请先结束当前进行中的批次"})
        if instance and new_status and new_status != instance.status:
            transitions = {
                ProjectBatch.STATUS_DRAFT: ProjectBatch.STATUS_ACTIVE,
                ProjectBatch.STATUS_ACTIVE: ProjectBatch.STATUS_FINISHED,
                ProjectBatch.STATUS_FINISHED: ProjectBatch.STATUS_ARCHIVED,
            }
            expected = transitions.get(instance.status)
            if expected != new_status:
                labels = dict(ProjectBatch.STATUS_CHOICES)
                from_label = labels.get(instance.status, instance.status)
                to_label = labels.get(new_status, new_status)
                raise serializers.ValidationError(
                    {"status": f"批次状态不允许从{from_label}变更为{to_label}"}
                )
        return attrs


class CertificateSettingSerializer(serializers.ModelSerializer):
    updated_by_name = serializers.CharField(
        source="updated_by.real_name", read_only=True
    )
    background_image = ValidatedImageField(
        label="证书底图", required=False, allow_null=True, write_only=True
    )
    seal_image = ValidatedImageField(
        label="电子印章", required=False, allow_null=True, write_only=True
    )
    background_image_url = serializers.SerializerMethodField()
    seal_image_url = serializers.SerializerMethodField()
    background_image_name = serializers.SerializerMethodField()
    seal_image_name = serializers.SerializerMethodField()

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
            "background_image_name",
            "seal_image_name",
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

    def _build_file_url(self, obj, field_name):
        file_field = getattr(obj, field_name, None)
        if not file_field:
            return ""
        try:
            request = self.context.get("request")
            return reverse(
                "certificate-settings-download-file",
                args=[obj.pk, field_name],
                request=request,
            )
        except NoReverseMatch:
            return (
                f"/api/v1/system-settings/certificates/"
                f"{obj.pk}/files/{field_name}/download/"
            )
        except Exception:
            return ""

    def get_background_image_url(self, obj):
        return self._build_file_url(obj, "background_image")

    def get_seal_image_url(self, obj):
        return self._build_file_url(obj, "seal_image")

    def get_background_image_name(self, obj):
        if not obj.background_image:
            return ""
        return Path(obj.background_image.name).name

    def get_seal_image_name(self, obj):
        if not obj.seal_image:
            return ""
        return Path(obj.seal_image.name).name

    def validate(self, attrs):
        attrs = super().validate(attrs)
        instance = getattr(self, "instance", None)
        is_active = attrs.get(
            "is_active",
            instance.is_active if instance is not None else True,
        )
        if not is_active:
            return attrs

        project_level = attrs.get(
            "project_level",
            instance.project_level if instance is not None else None,
        )
        project_category = attrs.get(
            "project_category",
            instance.project_category if instance is not None else None,
        )
        duplicate_qs = CertificateSetting.objects.filter(
            is_active=True,
            project_level=project_level,
            project_category=project_category,
        )
        if instance is not None:
            duplicate_qs = duplicate_qs.exclude(id=instance.id)
        if duplicate_qs.exists():
            raise serializers.ValidationError(
                {"is_active": "同一适用范围只能启用一个证书模板"}
            )
        return attrs
