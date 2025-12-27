"""
项目成员相关序列化器
"""

from rest_framework import serializers

from ..models import ProjectAdvisor, ProjectMember


class ProjectAdvisorSerializer(serializers.ModelSerializer):
    """
    项目指导教师序列化器
    """

    job_number = serializers.CharField(source="user.employee_id", read_only=True)
    name = serializers.CharField(source="user.real_name", read_only=True)
    user_name = serializers.CharField(source="user.real_name", read_only=True)
    department = serializers.CharField(source="user.department", read_only=True)
    contact = serializers.CharField(source="user.phone", read_only=True)
    email = serializers.CharField(source="user.email", read_only=True)
    title = serializers.CharField(
        source="user.title", read_only=True, allow_blank=True, default=""
    )

    class Meta:
        model = ProjectAdvisor
        fields = [
            "id",
            "user",
            "job_number",
            "name",
            "user_name",
            "department",
            "contact",
            "email",
            "title",
            "order",
        ]


class ProjectMemberSerializer(serializers.ModelSerializer):
    """
    项目成员序列化器
    """

    user_name = serializers.CharField(source="user.real_name", read_only=True)
    student_id = serializers.CharField(source="user.employee_id", read_only=True)
    name = serializers.CharField(source="user.real_name", read_only=True)

    class Meta:
        model = ProjectMember
        fields = [
            "id",
            "user",
            "user_name",
            "student_id",
            "name",
            "role",
            "join_date",
            "contribution",
        ]
