"""
项目业务逻辑层
"""

from django.utils import timezone
from django.db import transaction
from .models import Project, ProjectMember, ProjectProgress, ProjectAchievement


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
    @transaction.atomic
    def submit_project(project):
        """
        提交项目申报
        """
        if project.status == Project.ProjectStatus.DRAFT:
            project.status = Project.ProjectStatus.SUBMITTED
            project.submitted_at = timezone.now()
            project.save()
            return True
        return False

    @staticmethod
    def validate_member_participation(user, exclude_project_id=None):
        """
        验证学生是否已参与其他项目
        业务规则：每个学生不能同时参加两个项目
        """
        from django.db.models import Q

        # 查询用户参与的进行中的项目
        active_statuses = [
            Project.ProjectStatus.SUBMITTED,
            Project.ProjectStatus.LEVEL2_REVIEWING,
            Project.ProjectStatus.LEVEL2_APPROVED,
            Project.ProjectStatus.LEVEL1_REVIEWING,
            Project.ProjectStatus.LEVEL1_APPROVED,
            Project.ProjectStatus.IN_PROGRESS,
            Project.ProjectStatus.CLOSURE_DRAFT,
            Project.ProjectStatus.CLOSURE_SUBMITTED,
            Project.ProjectStatus.CLOSURE_LEVEL2_REVIEWING,
            Project.ProjectStatus.CLOSURE_LEVEL2_APPROVED,
            Project.ProjectStatus.CLOSURE_LEVEL1_REVIEWING,
        ]

        query = Q(leader=user) | Q(members=user)
        projects = Project.objects.filter(query, status__in=active_statuses)

        if exclude_project_id:
            projects = projects.exclude(id=exclude_project_id)

        return projects.count() == 0

    @staticmethod
    @transaction.atomic
    def add_project_member(project, user, role=ProjectMember.MemberRole.MEMBER):
        """
        添加项目成员
        """
        # 检查是否已经是成员
        if ProjectMember.objects.filter(project=project, user=user).exists():
            return None

        # 检查学生是否已参与其他项目
        if not ProjectService.validate_member_participation(user, project.id):
            raise ValueError("该学生已参与其他项目，不能重复参与")

        return ProjectMember.objects.create(project=project, user=user, role=role)

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

    @staticmethod
    @transaction.atomic
    def apply_closure(project, final_report, is_draft=False):
        """
        申请项目结题
        """
        if project.status != Project.ProjectStatus.IN_PROGRESS:
            raise ValueError("只有进行中的项目才能申请结题")

        # 更新结题报告
        project.final_report = final_report

        if is_draft:
            # 保存为草稿
            project.status = Project.ProjectStatus.CLOSURE_DRAFT
        else:
            # 提交结题申请
            project.status = Project.ProjectStatus.CLOSURE_SUBMITTED
            project.closure_applied_at = timezone.now()

        project.save()
        return True

    @staticmethod
    @transaction.atomic
    def submit_closure(project):
        """
        提交结题申请（从草稿状态）
        """
        if project.status == Project.ProjectStatus.CLOSURE_DRAFT:
            # 验证必需的材料
            if not project.final_report:
                raise ValueError("请先上传结题报告书")

            # 验证至少有一项成果
            if project.achievements.count() < 1:
                raise ValueError("请至少添加一项研究成果")

            project.status = Project.ProjectStatus.CLOSURE_SUBMITTED
            project.closure_applied_at = timezone.now()
            project.save()
            return True
        return False

    @staticmethod
    @transaction.atomic
    def revoke_closure(project):
        """
        撤销结题申请
        """
        # 只能在学院审核前撤销
        if project.status == Project.ProjectStatus.CLOSURE_SUBMITTED:
            project.status = Project.ProjectStatus.IN_PROGRESS
            project.closure_applied_at = None
            project.save()
            return True
        return False

    @staticmethod
    def add_achievement(
        project,
        achievement_type,
        title,
        description,
        attachment=None,
        **extra_fields,
    ):
        """
        添加项目成果
        """
        return ProjectAchievement.objects.create(
            project=project,
            achievement_type=achievement_type,
            title=title,
            description=description,
            attachment=attachment,
            **extra_fields,
        )
