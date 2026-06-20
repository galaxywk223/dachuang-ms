"""
项目结题相关序列化器
"""

from rest_framework import serializers

from ..models import Project
from ..upload_validation import validate_project_document_file


class ProjectClosureSerializer(serializers.Serializer):
    """
    项目结题申请序列化器
    """

    project_id = serializers.IntegerField()
    final_report = serializers.FileField(required=True, help_text="结题报告书（必需）")
    is_draft = serializers.BooleanField(default=False, help_text="是否保存为草稿")

    def validate_project_id(self, value):
        """
        验证项目ID和项目状态
        """
        try:
            project = Project.objects.get(id=value)
            # 只有进行中的项目才能结题
            if project.status != Project.ProjectStatus.IN_PROGRESS:
                raise serializers.ValidationError("只有进行中的项目才能申请结题")
            return value
        except Project.DoesNotExist:
            raise serializers.ValidationError("项目不存在")

    def validate_final_report(self, value):
        """
        验证结题报告文件
        """
        return validate_project_document_file(
            value,
            label="结题报告",
            max_size_mb=2,
        )
