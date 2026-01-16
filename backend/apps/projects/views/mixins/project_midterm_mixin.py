"""
Project mid-term actions.
"""

from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.projects.models import ProjectPhaseInstance, Project
from apps.projects.services.phase_service import ProjectPhaseService
from apps.reviews.services import ReviewService
from apps.notifications.services import NotificationService

from ...serializers.midterm import ProjectMidTermSerializer
from ...services import ProjectService


class ProjectMidtermMixin:
    @action(methods=["post"], detail=True, url_path="apply-mid-term")
    def apply_mid_term(self, request, pk=None):
        """
        申请中期检查
        """
        project = self.get_object()

        if project.leader != request.user:
            return Response(
                {"code": 403, "message": "只有项目负责人可以申请中期检查"},
                status=status.HTTP_403_FORBIDDEN,
            )

        data = request.data.copy()
        data["project_id"] = project.id
        serializer = ProjectMidTermSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        mid_term_report = serializer.validated_data.get("mid_term_report")
        is_draft = serializer.validated_data.get("is_draft", False)

        try:
            if not is_draft:
                from apps.system_settings.services.workflow_service import (
                    WorkflowService,
                )

                ok, msg = WorkflowService.check_phase_window(
                    "MID_TERM", project.batch, timezone.now().date()
                )
                if not ok:
                    return Response(
                        {"code": 400, "message": msg or "当前不在中期提交时间范围内"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            ProjectService.apply_mid_term(project, mid_term_report, is_draft)
            message = "中期检查已保存为草稿" if is_draft else "中期检查申请提交成功"

            if not is_draft:
                current_phase = ProjectPhaseService.get_current(
                    project, ProjectPhaseInstance.Phase.MID_TERM
                )
                if (
                    current_phase
                    and current_phase.state == ProjectPhaseInstance.State.RETURNED
                ):
                    ProjectPhaseService.start_new_attempt(
                        project,
                        ProjectPhaseInstance.Phase.MID_TERM,
                        created_by=request.user,
                    )
                ReviewService.create_mid_term_teacher_review(project)
                NotificationService.notify_midterm_submitted(project)

            return Response({"code": 200, "message": message})
        except ValueError as e:
            return Response(
                {"code": 400, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(methods=["post"], detail=True, url_path="submit-mid-term")
    def submit_mid_term(self, request, pk=None):
        """
        提交中期检查（从草稿状态）
        """
        project = self.get_object()

        if project.leader != request.user:
            return Response(
                {"code": 403, "message": "只有项目负责人可以提交中期检查"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            from apps.system_settings.services.workflow_service import WorkflowService

            ok, msg = WorkflowService.check_phase_window(
                "MID_TERM", project.batch, timezone.now().date()
            )
            if not ok:
                return Response(
                    {"code": 400, "message": msg or "当前不在中期提交时间范围内"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if ProjectService.submit_mid_term(project):
                current_phase = ProjectPhaseService.get_current(
                    project, ProjectPhaseInstance.Phase.MID_TERM
                )
                if (
                    current_phase
                    and current_phase.state == ProjectPhaseInstance.State.RETURNED
                ):
                    ProjectPhaseService.start_new_attempt(
                        project,
                        ProjectPhaseInstance.Phase.MID_TERM,
                        created_by=request.user,
                    )
                ReviewService.create_mid_term_teacher_review(project)
                NotificationService.notify_midterm_submitted(project)
                return Response({"code": 200, "message": "中期检查申请提交成功"})

            return Response(
                {"code": 400, "message": "项目状态不允许提交"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ValueError as e:
            return Response(
                {"code": 400, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(methods=["post"], detail=True, url_path="delete-mid-term")
    def delete_mid_term(self, request, pk=None):
        """
        删除中期提交（进入回收站）
        """
        project = self.get_object()

        if project.leader != request.user:
            return Response(
                {"code": 403, "message": "只有项目负责人可以删除中期提交"},
                status=status.HTTP_403_FORBIDDEN,
            )

        allowed_statuses = {
            Project.ProjectStatus.MID_TERM_DRAFT,
            Project.ProjectStatus.MID_TERM_SUBMITTED,
            Project.ProjectStatus.MID_TERM_REVIEWING,
            Project.ProjectStatus.MID_TERM_RETURNED,
            Project.ProjectStatus.MID_TERM_REJECTED,
        }
        if project.status not in allowed_statuses:
            return Response(
                {"code": 400, "message": "当前项目状态不允许删除中期提交"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        project.mid_term_report = None
        project.mid_term_submitted_at = None
        project.status = Project.ProjectStatus.IN_PROGRESS
        project.save(
            update_fields=[
                "mid_term_report",
                "mid_term_submitted_at",
                "status",
                "updated_at",
            ]
        )
        return Response({"code": 200, "message": "已移入回收站"})
