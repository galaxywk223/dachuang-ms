"""
项目归档/推送序列化器
"""

from rest_framework import serializers

from ..models import ProjectArchive, ProjectPushRecord, ProjectRecycleBin


class ProjectArchiveSerializer(serializers.ModelSerializer):
    project_no = serializers.CharField(source="project.project_no", read_only=True)
    project_title = serializers.CharField(source="project.title", read_only=True)

    class Meta:
        model = ProjectArchive
        fields = [
            "id",
            "project",
            "project_no",
            "project_title",
            "snapshot",
            "attachments",
            "archived_at",
        ]
        read_only_fields = ["id", "archived_at"]


class ProjectPushRecordSerializer(serializers.ModelSerializer):
    project_no = serializers.CharField(source="project.project_no", read_only=True)
    project_title = serializers.CharField(source="project.title", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = ProjectPushRecord
        fields = [
            "id",
            "project",
            "project_no",
            "project_title",
            "target",
            "payload",
            "response_message",
            "status",
            "status_display",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ProjectRecycleBinSerializer(serializers.ModelSerializer):
    project_no = serializers.CharField(source="project.project_no", read_only=True)
    project_title = serializers.CharField(source="project.title", read_only=True)
    resource_type_display = serializers.CharField(
        source="get_resource_type_display", read_only=True
    )

    class Meta:
        model = ProjectRecycleBin
        fields = [
            "id",
            "project",
            "project_no",
            "project_title",
            "resource_type",
            "resource_type_display",
            "resource_id",
            "payload",
            "attachments",
            "deleted_by",
            "deleted_at",
            "restored_by",
            "restored_at",
            "is_restored",
        ]
        read_only_fields = ["id", "deleted_at", "restored_at", "is_restored"]
