"""
系统设置序列化器
"""

from rest_framework import serializers

from ..models import (
    SystemSetting,
    CertificateSetting,
    ProjectBatch,
    WorkflowConfig,
    WorkflowNode,
    ReviewTemplate,
    ReviewTemplateItem,
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


class ReviewTemplateItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewTemplateItem
        fields = [
            "id",
            "template",
            "title",
            "description",
            "weight",
            "max_score",
            "is_required",
            "sort_order",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ReviewTemplateSerializer(serializers.ModelSerializer):
    updated_by_name = serializers.CharField(
        source="updated_by.real_name", read_only=True
    )
    items = ReviewTemplateItemSerializer(many=True, read_only=True)

    class Meta:
        model = ReviewTemplate
        fields = [
            "id",
            "name",
            "review_type",
            "review_level",
            "scope",
            "batch",
            "description",
            "notice",
            "is_active",
            "is_locked",
            "updated_by",
            "updated_by_name",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "updated_by"]


class WorkflowNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowNode
        fields = [
            "id",
            "workflow",
            "code",
            "name",
            "node_type",
            "role",
            "review_level",
            "scope",
            "return_policy",
            "review_template",
            "notice",
            "sort_order",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class WorkflowConfigSerializer(serializers.ModelSerializer):
    updated_by_name = serializers.CharField(
        source="updated_by.real_name", read_only=True
    )
    nodes = WorkflowNodeSerializer(many=True, read_only=True)

    class Meta:
        model = WorkflowConfig
        fields = [
            "id",
            "name",
            "phase",
            "batch",
            "version",
            "description",
            "is_active",
            "is_locked",
            "updated_by",
            "updated_by_name",
            "nodes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "updated_by"]
