"""
Project closure actions.
"""

from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.projects.models import ProjectPhaseInstance
from apps.projects.services.phase_service import ProjectPhaseService
from apps.reviews.services import ReviewService
from apps.system_settings.services import SystemSettingService

from ...serializers import ProjectClosureSerializer
from ...services import ProjectService


class ProjectClosureMixin:
    @action(methods=["post"], detail=True, url_path="apply-closure")
    def apply_closure(self, request, pk=None):
        """
        申请项目结题
        """
        project = self.get_object()

        if project.leader != request.user:
            return Response(
                {"code": 403, "message": "只有项目负责人可以申请结题"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ProjectClosureSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        is_draft = serializer.validated_data.get("is_draft", False)
        final_report = serializer.validated_data.get("final_report")

        try:
            if not is_draft:
                ok, msg = SystemSettingService.check_window(
                    "CLOSURE_WINDOW", timezone.now().date(), batch=project.batch
                )
                if not ok:
                    return Response(
                        {"code": 400, "message": msg or "当前不在结题提交时间范围内"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            ProjectService.apply_closure(project, final_report, is_draft)
            if not is_draft:
                current_phase = ProjectPhaseService.get_current(
                    project, ProjectPhaseInstance.Phase.CLOSURE
                )
                if current_phase and current_phase.state == ProjectPhaseInstance.State.RETURNED:
                    ProjectPhaseService.start_new_attempt(
                        project,
                        ProjectPhaseInstance.Phase.CLOSURE,
                        created_by=request.user,
                        step="TEACHER_REVIEWING",
                    )
                ReviewService.create_closure_teacher_review(project)

            message = "结题申请已保存为草稿" if is_draft else "结题申请提交成功"
            return Response({"code": 200, "message": message})
        except ValueError as e:
            return Response(
                {"code": 400, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(methods=["post"], detail=True, url_path="submit-closure")
    def submit_closure(self, request, pk=None):
        """
        提交结题申请（从草稿状态）
        """
        project = self.get_object()

        if project.leader != request.user:
            return Response(
                {"code": 403, "message": "只有项目负责人可以提交结题"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            ok, msg = SystemSettingService.check_window(
                "CLOSURE_WINDOW", timezone.now().date(), batch=project.batch
            )
            if not ok:
                return Response(
                    {"code": 400, "message": msg or "当前不在结题提交时间范围内"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if ProjectService.submit_closure(project):
                current_phase = ProjectPhaseService.get_current(
                    project, ProjectPhaseInstance.Phase.CLOSURE
                )
                if current_phase and current_phase.state == ProjectPhaseInstance.State.RETURNED:
                    ProjectPhaseService.start_new_attempt(
                        project,
                        ProjectPhaseInstance.Phase.CLOSURE,
                        created_by=request.user,
                        step="TEACHER_REVIEWING",
                    )
                ReviewService.create_closure_teacher_review(project)
                return Response({"code": 200, "message": "结题申请提交成功"})

            return Response(
                {"code": 400, "message": "项目状态不允许提交"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ValueError as e:
            return Response(
                {"code": 400, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(methods=["post"], detail=True, url_path="revoke-closure")
    def revoke_closure(self, request, pk=None):
        """
        撤销结题申请
        """
        project = self.get_object()

        if project.leader != request.user:
            return Response(
                {"code": 403, "message": "只有项目负责人可以撤销申请"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if ProjectService.revoke_closure(project):
            return Response({"code": 200, "message": "结题申请已撤销"})

        return Response(
            {"code": 400, "message": "项目状态不允许撤销"},
            status=status.HTTP_400_BAD_REQUEST,
        )

