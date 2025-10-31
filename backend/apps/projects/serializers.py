"""
项目序列化器
"""

from rest_framework import serializers
from .models import Project, ProjectMember, ProjectProgress


class ProjectMemberSerializer(serializers.ModelSerializer):
    """
    项目成员序列化器
    """

    user_name = serializers.CharField(source="user.real_name", read_only=True)
    employee_id = serializers.CharField(source="user.employee_id", read_only=True)

    class Meta:
        model = ProjectMember
        fields = [
            "id",
            "user",
            "user_name",
            "employee_id",
            "role",
            "join_date",
            "contribution",
        ]


class ProjectSerializer(serializers.ModelSerializer):
    """
    项目序列化器
    """

    leader_name = serializers.CharField(source="leader.real_name", read_only=True)
    members_info = ProjectMemberSerializer(
        source="projectmember_set", many=True, read_only=True
    )
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    level_display = serializers.CharField(source="get_level_display", read_only=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "project_no",
            "title",
            "description",
            "level",
            "level_display",
            "leader",
            "leader_name",
            "members_info",
            "advisor",
            "advisor_title",
            "category",
            "research_field",
            "keywords",
            "start_date",
            "end_date",
            "budget",
            "research_content",
            "research_plan",
            "expected_results",
            "innovation_points",
            "proposal_file",
            "final_report",
            "achievement_file",
            "status",
            "status_display",
            "college",
            "created_at",
            "updated_at",
            "submitted_at",
        ]
        read_only_fields = [
            "id",
            "project_no",
            "created_at",
            "updated_at",
            "submitted_at",
        ]

    def create(self, validated_data):
        # 自动生成项目编号
        import datetime

        year = datetime.datetime.now().year
        count = Project.objects.filter(project_no__startswith=f"DC{year}").count() + 1
        validated_data["project_no"] = f"DC{year}{count:04d}"

        # 自动设置学院为负责人的学院
        leader = validated_data["leader"]
        validated_data["college"] = leader.college

        return super().create(validated_data)


class ProjectListSerializer(serializers.ModelSerializer):
    """
    项目列表序列化器（简化版）
    """

    leader_name = serializers.CharField(source="leader.real_name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    level_display = serializers.CharField(source="get_level_display", read_only=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "project_no",
            "title",
            "level",
            "level_display",
            "leader",
            "leader_name",
            "status",
            "status_display",
            "college",
            "created_at",
            "submitted_at",
        ]


class ProjectProgressSerializer(serializers.ModelSerializer):
    """
    项目进度序列化器
    """

    creator_name = serializers.CharField(source="created_by.real_name", read_only=True)

    class Meta:
        model = ProjectProgress
        fields = [
            "id",
            "project",
            "title",
            "content",
            "attachment",
            "created_by",
            "creator_name",
            "created_at",
        ]
        read_only_fields = ["id", "created_by", "created_at"]


class ProjectSubmitSerializer(serializers.Serializer):
    """
    项目提交序列化器
    """

    project_id = serializers.IntegerField()

    def validate_project_id(self, value):
        try:
            project = Project.objects.get(id=value)
            # 检查项目是否可以提交
            if project.status not in [Project.ProjectStatus.DRAFT]:
                raise serializers.ValidationError("项目状态不允许提交")
            return value
        except Project.DoesNotExist:
            raise serializers.ValidationError("项目不存在")
