"""
项目业务逻辑层
"""

from django.utils import timezone
from .models import Project, ProjectMember, ProjectProgress


class ProjectService:
    """
    项目服务类
    """

    @staticmethod
    def generate_project_no():
        """
        生成项目编号
        格式：DC + 年份 + 4位序号
        """
        import datetime

        year = datetime.datetime.now().year
        count = Project.objects.filter(project_no__startswith=f"DC{year}").count() + 1
        return f"DC{year}{count:04d}"

    @staticmethod
    def submit_project(project):
        """
        提交项目
        """
        if project.status == Project.ProjectStatus.DRAFT:
            project.status = Project.ProjectStatus.SUBMITTED
            project.submitted_at = timezone.now()
            project.save()
            return True
        return False

    @staticmethod
    def add_project_member(project, user, role=ProjectMember.MemberRole.MEMBER):
        """
        添加项目成员
        """
        if not ProjectMember.objects.filter(project=project, user=user).exists():
            return ProjectMember.objects.create(project=project, user=user, role=role)
        return None

    @staticmethod
    def remove_project_member(project, user):
        """
        移除项目成员
        """
        try:
            member = ProjectMember.objects.get(project=project, user=user)
            if member.role != ProjectMember.MemberRole.LEADER:
                member.delete()
                return True
        except ProjectMember.DoesNotExist:
            pass
        return False

    @staticmethod
    def add_progress(project, user, title, content, attachment=None):
        """
        添加项目进度
        """
        return ProjectProgress.objects.create(
            project=project,
            title=title,
            content=content,
            attachment=attachment,
            created_by=user,
        )

    @staticmethod
    def get_user_projects(user):
        """
        获取用户相关的项目
        """
        from django.db import models

        return Project.objects.filter(
            models.Q(leader=user) | models.Q(members=user)
        ).distinct()

    @staticmethod
    def get_college_projects(college):
        """
        获取学院的项目
        """
        return Project.objects.filter(college=college)
