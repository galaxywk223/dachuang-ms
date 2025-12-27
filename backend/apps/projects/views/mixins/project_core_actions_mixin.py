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

        if not (
            user.is_level1_admin
            or user.is_level2_admin
            or (user.is_student and project.leader_id == user.id)
        ):
            return Response(
                {"code": 403, "message": "无权限访问"},
                status=status.HTTP_403_FORBIDDEN,
            )

        html = render_certificate_html(project)
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
                step="TEACHER_REVIEWING",
            )

        ReviewService.create_teacher_review(project)

        project.submitted_at = timezone.now()
        project.save(update_fields=["submitted_at"])

        return Response({"code": 200, "message": "项目提交成功，等待导师审核"})

