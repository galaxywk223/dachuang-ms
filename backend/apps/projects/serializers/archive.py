"""
项目归档/推送序列化器
"""

from rest_framework import serializers

from ..models import ProjectArchive


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
