from rest_framework import serializers

class ProjectMidTermSerializer(serializers.Serializer):
    """
    项目中期检查提交序列化器
    """

    project_id = serializers.IntegerField()
    mid_term_report = serializers.FileField(required=False, allow_null=True, help_text="中期检查报告")
    is_draft = serializers.BooleanField(default=False, help_text="是否保存为草稿")

    def validate_project_id(self, value):
        from ..models import Project
        try:
            project = Project.objects.get(id=value)
            # 只有进行中、中期草稿或中期被退回的项目才能提交
            allowed_statuses = [
                Project.ProjectStatus.IN_PROGRESS,
                Project.ProjectStatus.MID_TERM_DRAFT,
                Project.ProjectStatus.MID_TERM_REJECTED,
            ]
            if project.status not in allowed_statuses:
                raise serializers.ValidationError("当前项目状态不允许提交中期检查")
            return value
        except Project.DoesNotExist:
            raise serializers.ValidationError("项目不存在")

    def validate_mid_term_report(self, value):
        """
        验证中期报告文件
        """
        if not value:
             return value
             
        # 检查文件格式
        if not value.name.lower().endswith(".pdf"):
            raise serializers.ValidationError("中期报告必须是PDF格式")

        # 检查文件大小（不超过5MB）
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("中期报告文件大小不能超过5MB")

        return value
