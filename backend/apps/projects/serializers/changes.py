"""
项目异动序列化器
"""

from pathlib import Path

from django.urls import NoReverseMatch
from rest_framework import serializers
from rest_framework.reverse import reverse

from ..models import ProjectChangeRequest, ProjectChangeReview
from ..upload_validation import validate_project_support_file


class ProjectChangeReviewSerializer(serializers.ModelSerializer):
    reviewer_name = serializers.CharField(source="reviewer.real_name", read_only=True)
    role_code = serializers.CharField(
        source="workflow_node.role_fk.code", read_only=True, allow_null=True
    )
    role_name = serializers.CharField(
        source="workflow_node.role_fk.name", read_only=True, allow_null=True
    )
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = ProjectChangeReview
        fields = [
            "id",
            "change_request",
            "workflow_node",
            "role_code",
            "role_name",
            "reviewer",
            "reviewer_name",
            "status",
            "status_display",
            "comments",
            "reviewed_at",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "reviewed_at"]


class ProjectChangeRequestSerializer(serializers.ModelSerializer):
    project_title = serializers.CharField(source="project.title", read_only=True)
    project_no = serializers.CharField(source="project.project_no", read_only=True)
    leader_name = serializers.CharField(source="project.leader.real_name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    request_type_display = serializers.CharField(
        source="get_request_type_display", read_only=True
    )
    attachment = serializers.FileField(required=False, allow_null=True, write_only=True)
    attachment_url = serializers.SerializerMethodField()
    attachment_name = serializers.SerializerMethodField()
    reviews = ProjectChangeReviewSerializer(many=True, read_only=True)

    class Meta:
        model = ProjectChangeRequest
        fields = [
            "id",
            "project",
            "project_title",
            "project_no",
            "leader_name",
            "request_type",
            "request_type_display",
            "reason",
            "change_data",
            "attachment",
            "attachment_url",
            "attachment_name",
            "status",
            "status_display",
            "created_by",
            "submitted_at",
            "reviewed_at",
            "created_at",
            "updated_at",
            "reviews",
        ]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]

    def get_attachment_url(self, obj):
        if not obj.attachment:
            return ""
        try:
            request = self.context.get("request")
            return reverse(
                "change-request-download",
                args=[obj.pk],
                request=request,
            )
        except NoReverseMatch:
            return f"/api/v1/projects/change-requests/{obj.pk}/download/"

    def get_attachment_name(self, obj):
        if not obj.attachment:
            return ""
        return Path(obj.attachment.name).name

    def validate_change_data(self, value):
        if isinstance(value, str):
            try:
                import json

                value = json.loads(value) if value else {}
            except json.JSONDecodeError:
                raise serializers.ValidationError("变更内容JSON格式不正确")
        if value in (None, ""):
            return {}
        if not isinstance(value, dict):
            raise serializers.ValidationError("变更内容必须为JSON对象")
        return value

    def validate_attachment(self, value):
        return validate_project_support_file(
            value,
            label="异动附件",
            max_size_mb=20,
            empty_as_none=True,
        )


class ProjectChangeReviewActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(
        choices=["approve", "reject"], help_text="审核操作"
    )
    comments = serializers.CharField(required=False, allow_blank=True)
