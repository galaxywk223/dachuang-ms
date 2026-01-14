"""
Project workflow/expert-summary actions.

Keep `ProjectViewSet` smaller by extracting workflow-heavy endpoints here.
"""

from django.db import transaction
from django.db.models import Avg
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from apps.projects.models import ProjectPhaseInstance
from apps.projects.services.phase_service import ProjectPhaseService
from apps.system_settings.services import WorkflowService, AdminAssignmentService
from apps.reviews.models import Review
from apps.reviews.services import ReviewService

from ...models import Project


class ProjectWorkflowMixin:
    def _get_current_phase_instance(
        self, project: Project, phase: str
    ) -> ProjectPhaseInstance | None:
        return ProjectPhaseService.get_current(project, phase)

    def _assert_assigned_admin(self, project: Project, phase: str, user):
        phase_instance = self._get_current_phase_instance(project, phase)
        if not phase_instance or not phase_instance.current_node_id:
            raise PermissionDenied("流程状态异常：缺少当前节点")
        node_obj = WorkflowService.get_node_by_id(phase_instance.current_node_id)
        if not node_obj:
            raise PermissionDenied("流程状态异常：当前节点不存在")
        try:
            admin_user = AdminAssignmentService.resolve_admin_user(
                project, phase, node_obj
            )
        except ValueError as exc:
            raise PermissionDenied(str(exc)) from exc
        if admin_user.id != user.id:
            raise PermissionDenied("无权限操作该节点")
        return phase_instance

    def _get_review_type_for_phase(self, phase: str):
        return {
            "APPLICATION": Review.ReviewType.APPLICATION,
            "MID_TERM": Review.ReviewType.MID_TERM,
            "CLOSURE": Review.ReviewType.CLOSURE,
        }.get(phase)

    def _get_pending_admin_review(
        self,
        *,
        user,
        project: Project,
        phase: str,
        phase_instance: ProjectPhaseInstance | None,
    ):
        review_type = self._get_review_type_for_phase(phase)
        if not review_type:
            return None
        qs = ReviewService.get_pending_reviews_for_admin(user).filter(
            project=project,
            review_type=review_type,
        )
        if phase_instance:
            qs = qs.filter(phase_instance=phase_instance)
            if phase_instance.current_node_id:
                qs = qs.filter(workflow_node_id=phase_instance.current_node_id)
        return qs.first()

    def _get_expert_reviews_qs(
        self,
        *,
        project: Project,
        review_type: str | None,
        phase_instance: ProjectPhaseInstance | None,
        workflow_node_id: int | None = None,
    ):
        qs = Review.objects.filter(project=project, is_expert_review=True)
        if review_type:
            qs = qs.filter(review_type=review_type)
        if phase_instance:
            qs = qs.filter(phase_instance=phase_instance)
        if workflow_node_id:
            qs = qs.filter(workflow_node_id=workflow_node_id)
        elif phase_instance and phase_instance.current_node_id:
            qs = qs.filter(workflow_node_id=phase_instance.current_node_id)
        return qs

    @action(detail=True, methods=["get"], url_path="expert-summary")
    def expert_summary(self, request, pk=None):
        """
        获取当前阶段专家评审进度/统计（不改变流程）
        query: review_type=APPLICATION|MID_TERM|CLOSURE, scope=COLLEGE|SCHOOL(optional), node_id(optional)
        """
        project = self.get_object()
        review_type = (
            request.query_params.get("review_type") or Review.ReviewType.APPLICATION
        )
        scope = (request.query_params.get("scope") or "").upper()
        phase_instance = self._get_current_phase_instance(project, review_type)

        node_id_param = request.query_params.get("node_id")
        node_id = (
            int(node_id_param)
            if node_id_param and str(node_id_param).isdigit()
            else None
        )
        if not node_id and phase_instance and phase_instance.current_node_id:
            node_id = phase_instance.current_node_id
        if not node_id and scope:
            for node in WorkflowService.get_nodes(review_type, project.batch):
                if node.require_expert_review:
                    node_id = node.id
                    break
        node_obj = WorkflowService.get_node_by_id(node_id) if node_id else None
        require_expert_review = (
            bool(node_obj.require_expert_review) if node_obj else False
        )
        qs = self._get_expert_reviews_qs(
            project=project,
            review_type=review_type,
            phase_instance=phase_instance,
            workflow_node_id=node_id,
        )
        assigned = qs.count()
        pending = qs.filter(status=Review.ReviewStatus.PENDING).count()
        submitted = assigned - pending
        approved_count = qs.filter(status=Review.ReviewStatus.APPROVED).count()
        rejected_count = qs.filter(status=Review.ReviewStatus.REJECTED).count()
        avg_score = (
            qs.exclude(status=Review.ReviewStatus.PENDING)
            .aggregate(avg=Avg("score"))
            .get("avg")
        )

        return Response(
            {
                "code": 200,
                "message": "获取成功",
                "data": {
                    "phase_instance_id": phase_instance.id if phase_instance else None,
                    "attempt_no": phase_instance.attempt_no if phase_instance else None,
                    "step": phase_instance.step if phase_instance else "",
                    "state": phase_instance.state if phase_instance else "",
                    "node_id": node_id,
                    "require_expert_review": require_expert_review,
                    "assigned": assigned,
                    "submitted": submitted,
                    "pending": pending,
                    "approved": approved_count,
                    "rejected": rejected_count,
                    "all_submitted": assigned > 0 and pending == 0,
                    "avg_score": avg_score,
                },
            }
        )

    @action(detail=True, methods=["post"], url_path="workflow/return-to-student")
    def workflow_return_to_student(self, request, pk=None):
        """
        管理员退回学生修改（创建新一轮由学生重新提交触发）
        body: { phase: APPLICATION|MID_TERM|CLOSURE, reason?: str }
        """
        project = self.get_object()
        user = request.user
        phase = request.data.get("phase") or ProjectPhaseInstance.Phase.APPLICATION
        reason = request.data.get("reason", "")

        self._assert_assigned_admin(project, phase, user)

        status_map = {
            ProjectPhaseInstance.Phase.APPLICATION: Project.ProjectStatus.APPLICATION_RETURNED,
            ProjectPhaseInstance.Phase.MID_TERM: Project.ProjectStatus.MID_TERM_RETURNED,
            ProjectPhaseInstance.Phase.CLOSURE: Project.ProjectStatus.CLOSURE_RETURNED,
        }
        new_status = status_map.get(phase, Project.ProjectStatus.DRAFT)

        with transaction.atomic():
            phase_instance = self._get_current_phase_instance(project, phase)
            moved = False
            if phase_instance:
                initial_node = WorkflowService.get_initial_node(
                    phase_instance.phase, project.batch
                )
                if initial_node and WorkflowService.get_node_by_id(initial_node.id):
                    ReviewService._move_to_target_node(
                        project, phase_instance, initial_node.id, reason
                    )
                    moved = True
                else:
                    ProjectPhaseService.mark_returned(
                        phase_instance,
                        return_to=ProjectPhaseInstance.ReturnTo.STUDENT,
                        reason=reason,
                    )
                Review.objects.filter(
                    project=project,
                    phase_instance=phase_instance,
                    is_expert_review=True,
                    status=Review.ReviewStatus.PENDING,
                ).update(
                    status=Review.ReviewStatus.REJECTED,
                    comments="管理员退回，评审任务作废",
                    reviewed_at=timezone.now(),
                )

            if not moved:
                project.status = new_status
                project.save(update_fields=["status", "updated_at"])

        return Response({"code": 200, "message": "已退回学生修改"})

    @action(detail=True, methods=["post"], url_path="workflow/report-to-school")
    def workflow_report_to_school(self, request, pk=None):
        """
        学院管理员上报校级（立项流程）
        要求：院级专家评审任务已全部提交
        """
        project = self.get_object()
        user = request.user
        self._assert_assigned_admin(
            project, ProjectPhaseInstance.Phase.APPLICATION, user
        )

        phase_instance = self._get_current_phase_instance(
            project, ProjectPhaseInstance.Phase.APPLICATION
        )
        review = self._get_pending_admin_review(
            user=user,
            project=project,
            phase=ProjectPhaseInstance.Phase.APPLICATION,
            phase_instance=phase_instance,
        )
        if not review:
            return Response(
                {"code": 404, "message": "未找到待审核记录或无权限"},
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            ReviewService.approve_review(review, user, "")
        except ValueError as exc:
            return Response(
                {"code": 400, "message": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"code": 200, "message": "已上报校级"})

    @action(detail=True, methods=["post"], url_path="workflow/report-to-school-closure")
    def workflow_report_to_school_closure(self, request, pk=None):
        """
        学院管理员上报校级（结题流程）
        要求：院级专家评审任务已全部提交
        """
        project = self.get_object()
        user = request.user
        self._assert_assigned_admin(project, ProjectPhaseInstance.Phase.CLOSURE, user)

        phase_instance = self._get_current_phase_instance(
            project, ProjectPhaseInstance.Phase.CLOSURE
        )
        if phase_instance is None:
            return Response(
                {
                    "code": 400,
                    "message": "流程状态异常：缺少结题阶段轮次，请重新上报或联系管理员",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        review = self._get_pending_admin_review(
            user=user,
            project=project,
            phase=ProjectPhaseInstance.Phase.CLOSURE,
            phase_instance=phase_instance,
        )
        if not review:
            return Response(
                {"code": 404, "message": "未找到待审核记录或无权限"},
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            ReviewService.approve_review(review, user, "")
        except ValueError as exc:
            return Response(
                {"code": 400, "message": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"code": 200, "message": "已上报校级"})

    @action(detail=True, methods=["post"], url_path="workflow/publish-establishment")
    def workflow_publish_establishment(self, request, pk=None):
        """
        校级管理员发布立项（录入批准金额）
        body: { approved_budget?: number }
        """
        project = self.get_object()
        user = request.user
        self._assert_assigned_admin(
            project, ProjectPhaseInstance.Phase.APPLICATION, user
        )

        approved_budget = request.data.get("approved_budget")
        try:
            approved_budget_val = (
                float(approved_budget)
                if approved_budget is not None and approved_budget != ""
                else None
            )
        except Exception:
            return Response(
                {"code": 400, "message": "approved_budget格式错误"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        phase_instance = self._get_current_phase_instance(
            project, ProjectPhaseInstance.Phase.APPLICATION
        )
        review = self._get_pending_admin_review(
            user=user,
            project=project,
            phase=ProjectPhaseInstance.Phase.APPLICATION,
            phase_instance=phase_instance,
        )
        if not review:
            return Response(
                {"code": 404, "message": "未找到待审核记录或无权限"},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            with transaction.atomic():
                if approved_budget_val is not None:
                    project.approved_budget = approved_budget_val
                    project.save(update_fields=["approved_budget", "updated_at"])
                ReviewService.approve_review(review, user, "")
        except ValueError as exc:
            return Response(
                {"code": 400, "message": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"code": 200, "message": "立项已发布"})

    @action(detail=True, methods=["post"], url_path="workflow/finalize-midterm")
    def workflow_finalize_midterm(self, request, pk=None):
        """
        中期阶段管理员最终处理（通过/退回）
        body: { action: pass|return, reason?: str }
        """
        project = self.get_object()
        user = request.user
        self._assert_assigned_admin(project, ProjectPhaseInstance.Phase.MID_TERM, user)

        action_type = request.data.get("action")
        reason = request.data.get("reason", "")
        if action_type not in ("pass", "return"):
            return Response(
                {"code": 400, "message": "action必须为pass或return"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        phase_instance = self._get_current_phase_instance(
            project, ProjectPhaseInstance.Phase.MID_TERM
        )
        review = self._get_pending_admin_review(
            user=user,
            project=project,
            phase=ProjectPhaseInstance.Phase.MID_TERM,
            phase_instance=phase_instance,
        )
        if not review:
            return Response(
                {"code": 404, "message": "未找到待审核记录或无权限"},
                status=status.HTTP_404_NOT_FOUND,
            )

        target_node_id = request.data.get("target_node_id")
        try:
            if action_type == "pass":
                ReviewService.approve_review(review, user, "")
            else:
                ReviewService.reject_review(
                    review,
                    user,
                    reason,
                    target_node_id=target_node_id,
                )
        except ValueError as exc:
            return Response(
                {"code": 400, "message": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"code": 200, "message": "处理中期完成"})

    @action(detail=True, methods=["post"], url_path="workflow/finalize-closure")
    def workflow_finalize_closure(self, request, pk=None):
        """
        结题阶段校级管理员最终处理（通过/退回）
        body: { action: approve|return, reason?: str, return_to?: student|teacher }
        """
        project = self.get_object()
        user = request.user
        self._assert_assigned_admin(project, ProjectPhaseInstance.Phase.CLOSURE, user)

        action_type = request.data.get("action")
        reason = request.data.get("reason", "")
        return_to = (request.data.get("return_to") or "student").lower()
        if action_type not in ("approve", "return"):
            return Response(
                {"code": 400, "message": "action必须为approve或return"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if action_type == "return" and return_to not in ("student", "teacher"):
            return Response(
                {"code": 400, "message": "return_to必须为student或teacher"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        phase_instance = self._get_current_phase_instance(
            project, ProjectPhaseInstance.Phase.CLOSURE
        )
        if phase_instance is None:
            return Response(
                {"code": 400, "message": "请先分配专家评审"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        review = self._get_pending_admin_review(
            user=user,
            project=project,
            phase=ProjectPhaseInstance.Phase.CLOSURE,
            phase_instance=phase_instance,
        )
        if not review:
            return Response(
                {"code": 404, "message": "未找到待审核记录或无权限"},
                status=status.HTTP_404_NOT_FOUND,
            )

        target_node_id = request.data.get("target_node_id")
        if not target_node_id:
            if return_to == "teacher":
                teacher_node = ReviewService._find_teacher_node(
                    ProjectPhaseInstance.Phase.CLOSURE, project.batch
                )
                target_node_id = ReviewService._resolve_workflow_node_id(teacher_node)
            else:
                initial_node = WorkflowService.get_initial_node(
                    phase_instance.phase, project.batch
                )
                if initial_node and WorkflowService.get_node_by_id(initial_node.id):
                    target_node_id = initial_node.id

        try:
            if action_type == "approve":
                ReviewService.approve_review(review, user, "")
            else:
                ReviewService.reject_review(
                    review,
                    user,
                    reason,
                    target_node_id=target_node_id,
                )
        except ValueError as exc:
            return Response(
                {"code": 400, "message": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"code": 200, "message": "处理完成"})
