"""
Core actions on the Project resource.
"""

from django.http import HttpResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.projects.models import ProjectPhaseInstance
from apps.projects.services.phase_service import ProjectPhaseService
from apps.reviews.services import ReviewService
from apps.notifications.services import NotificationService

from ...certificates import render_certificate_html
from ...models import Project
from ...services import ProjectService


class ProjectCoreActionsMixin:
    @action(detail=True, methods=["get"], url_path="budget-stats")
    def budget_stats(self, request, pk=None):
        """
        获取项目经费统计
        """
        project = self.get_object()
        stats = ProjectService.get_budget_stats(project)
        return Response({"code": 200, "message": "获取成功", "data": stats})

    @action(detail=True, methods=["get"], url_path="certificate")
    def certificate(self, request, pk=None):
        """
        获取结题证书（HTML）
        """
        project = self.get_object()
        user = request.user

        if project.status != Project.ProjectStatus.CLOSED:
            return Response(
                {"code": 400, "message": "项目未结题，无法生成证书"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not (user.is_admin or (user.is_student and project.leader_id == user.id)):
            return Response(
                {"code": 403, "message": "无权限访问"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # 自动匹配最佳证书配置
        html = render_certificate_html(project, setting=None, request=request)
        return HttpResponse(html, content_type="text/html")

    @action(methods=["post"], detail=True)
    def submit(self, request, pk=None):
        """
        提交项目申报
        """
        project = self.get_object()

        if project.leader != request.user:
            return Response(
                {"code": 403, "message": "只有项目负责人可以提交项目"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if project.status not in [
            Project.ProjectStatus.DRAFT,
            Project.ProjectStatus.APPLICATION_RETURNED,
        ]:
            return Response(
                {"code": 400, "message": "项目状态不允许提交"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        current_phase = ProjectPhaseService.get_current(
            project, ProjectPhaseInstance.Phase.APPLICATION
        )
        if current_phase and current_phase.state == ProjectPhaseInstance.State.RETURNED:
            ProjectPhaseService.start_new_attempt(
                project,
                ProjectPhaseInstance.Phase.APPLICATION,
                created_by=request.user,
            )

        ReviewService.start_phase_review(
            project,
            ProjectPhaseInstance.Phase.APPLICATION,
            created_by=request.user,
        )

        project.submitted_at = timezone.now()
        project.save(update_fields=["submitted_at"])
        NotificationService.notify_project_submitted(project)

        return Response({"code": 200, "message": "项目提交成功，等待导师审核"})

    @action(methods=["post"], detail=True, url_path="delete-application")
    def delete_application(self, request, pk=None):
        """
        删除立项申报（进入回收站）
        """
        project = self.get_object()

        if project.leader != request.user:
            return Response(
                {"code": 403, "message": "只有项目负责人可以删除申报"},
                status=status.HTTP_403_FORBIDDEN,
            )

        allowed_statuses = {
            Project.ProjectStatus.SUBMITTED,
            Project.ProjectStatus.TEACHER_AUDITING,
            Project.ProjectStatus.TEACHER_REJECTED,
            Project.ProjectStatus.APPLICATION_RETURNED,
        }
        if project.status not in allowed_statuses:
            return Response(
                {"code": 400, "message": "当前状态不允许删除申报"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        project.proposal_file = None
        project.attachment_file = None
        project.submitted_at = None
        project.status = Project.ProjectStatus.DRAFT
        project.save(
            update_fields=[
                "proposal_file",
                "attachment_file",
                "submitted_at",
                "status",
                "updated_at",
            ]
        )
        return Response({"code": 200, "message": "已移入回收站"})
