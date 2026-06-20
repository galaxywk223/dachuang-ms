"""
项目变更/延期/终止 业务逻辑
"""

from django.utils import timezone
from django.db import transaction
from typing import Any, cast

from ..models import (
    Project,
    ProjectChangeRequest,
    ProjectChangeReview,
    ProjectPhaseInstance,
)
from apps.system_settings.services import SystemSettingService, WorkflowService


CHANGE_REQUEST_BLOCKED_PROJECT_STATUSES = {
    Project.ProjectStatus.CLOSED,
    Project.ProjectStatus.COMPLETED,
    Project.ProjectStatus.TERMINATED,
}


class ProjectChangeService:
    """
    项目异动申请服务类
    """

    @staticmethod
    def _has_teacher_review(change_request: ProjectChangeRequest) -> bool:
        return change_request.project.advisors.exists()

    @staticmethod
    def _resolve_phase(change_request: ProjectChangeRequest) -> str:
        project = change_request.project
        phase_instance = (
            ProjectPhaseInstance.objects.filter(
                project=project, state=ProjectPhaseInstance.State.IN_PROGRESS
            )
            .order_by("-created_at", "-id")
            .first()
        )
        if not phase_instance:
            phase_instance = (
                ProjectPhaseInstance.objects.filter(project=project)
                .order_by("-created_at", "-id")
                .first()
            )
        return (
            phase_instance.phase
            if phase_instance
            else ProjectPhaseInstance.Phase.APPLICATION
        )

    @staticmethod
    def _get_review_nodes(change_request: ProjectChangeRequest):
        phase = "CHANGE"
        nodes = WorkflowService.get_nodes(phase, change_request.project.batch)
        review_nodes = [
            node
            for node in nodes
            if node.node_type != "SUBMIT" and WorkflowService.get_node_by_id(node.id)
        ]
        if not review_nodes:
            raise ValueError("流程未落库，请先配置并启用工作流")
        return phase, review_nodes

    @staticmethod
    def _status_for_node_role(node_role: str, role_scope_dimension=None):
        status_map = {
            "TEACHER": ProjectChangeRequest.ChangeStatus.TEACHER_REVIEWING,
            "LEVEL2_ADMIN": ProjectChangeRequest.ChangeStatus.LEVEL2_REVIEWING,
            "LEVEL1_ADMIN": ProjectChangeRequest.ChangeStatus.LEVEL1_REVIEWING,
        }
        status = status_map.get(node_role)
        if not status and role_scope_dimension == "COLLEGE":
            status = ProjectChangeRequest.ChangeStatus.LEVEL2_REVIEWING
        elif not status and role_scope_dimension == "SCHOOL":
            status = ProjectChangeRequest.ChangeStatus.LEVEL1_REVIEWING
        if not status:
            raise ValueError(f"不支持的审核角色: {node_role}")
        return status

    @staticmethod
    def _status_for_workflow_node(node):
        if not node:
            raise ValueError("审核记录缺少工作流节点")
        role_code = (
            node.get_role_code()
            if hasattr(node, "get_role_code")
            else getattr(node, "role", None)
        )
        role_fk = getattr(node, "role_fk", None)
        role_scope_dimension = role_fk.scope_dimension if role_fk else None
        role_fk_id = getattr(node, "role_fk_id", None)
        if not role_scope_dimension and role_fk_id:
            from apps.users.models import Role

            role_scope_dimension = (
                Role.objects.filter(id=role_fk_id)
                .values_list("scope_dimension", flat=True)
                .first()
            )
        return ProjectChangeService._status_for_node_role(
            role_code, role_scope_dimension
        )

    @staticmethod
    def _set_status_for_node(change_request: ProjectChangeRequest, node) -> None:
        status = ProjectChangeService._status_for_workflow_node(node)
        change_request.status = status

    @staticmethod
    def _create_review(
        change_request: ProjectChangeRequest, workflow_node_id: int
    ) -> ProjectChangeReview:
        return ProjectChangeReview.objects.create(
            change_request=change_request,
            workflow_node_id=workflow_node_id,
            status=ProjectChangeReview.ReviewStatus.PENDING,
        )

    @staticmethod
    def _lock_request(change_request: ProjectChangeRequest) -> ProjectChangeRequest:
        if not change_request.pk:
            raise ValueError("异动申请不存在")

        try:
            return (
                ProjectChangeRequest.objects.select_for_update(of=("self",))
                .select_related("project")
                .get(pk=change_request.pk)
            )
        except ProjectChangeRequest.DoesNotExist as exc:
            raise ValueError("异动申请不存在") from exc

    @staticmethod
    def _ensure_submittable_request(change_request: ProjectChangeRequest) -> None:
        project = change_request.project
        current_batch = SystemSettingService.get_current_batch()
        if not current_batch or project.batch_id != current_batch.id:
            raise ValueError("当前批次不允许提交该异动申请")
        if project.status in CHANGE_REQUEST_BLOCKED_PROJECT_STATUSES:
            raise ValueError("项目已结题或终止，无法申请异动")

    @staticmethod
    def _lock_review(review: ProjectChangeReview) -> ProjectChangeReview:
        if not review.pk:
            raise ValueError("审核记录不存在")

        try:
            locked_review = ProjectChangeReview.objects.select_for_update().get(
                pk=review.pk
            )
            change_request = ProjectChangeRequest.objects.select_for_update().get(
                pk=locked_review.change_request_id
            )
        except ProjectChangeReview.DoesNotExist as exc:
            raise ValueError("审核记录不存在") from exc
        except ProjectChangeRequest.DoesNotExist as exc:
            raise ValueError("异动申请不存在") from exc

        locked_review.change_request = change_request
        return locked_review

    @staticmethod
    def _ensure_pending_review(review: ProjectChangeReview) -> None:
        if review.status != ProjectChangeReview.ReviewStatus.PENDING:
            raise ValueError("审核记录已处理，无法重复审核")
        if review.change_request.status in {
            ProjectChangeRequest.ChangeStatus.APPROVED,
            ProjectChangeRequest.ChangeStatus.REJECTED,
        }:
            raise ValueError("异动流程已结束，无法处理该审核记录")

    @staticmethod
    def _ensure_current_review_node(review: ProjectChangeReview) -> None:
        node = review.workflow_node
        if not node:
            raise ValueError("审核记录缺少工作流节点")

        expected_status = ProjectChangeService._status_for_workflow_node(node)
        if review.change_request.status != expected_status:
            raise ValueError("审核记录不是当前异动流程节点")

    @staticmethod
    @transaction.atomic
    def submit_request(change_request: ProjectChangeRequest) -> None:
        """
        提交变更申请，创建首个审核节点
        """
        change_request = ProjectChangeService._lock_request(change_request)
        ProjectChangeService._ensure_submittable_request(change_request)
        change_request.submitted_at = timezone.now()

        _, review_nodes = ProjectChangeService._get_review_nodes(change_request)
        target_node = None
        for node in review_nodes:
            if node.role == "TEACHER" and not ProjectChangeService._has_teacher_review(
                change_request
            ):
                continue
            target_node = node
            break

        if not target_node:
            raise ValueError("流程未配置可用审核节点")

        ProjectChangeService._set_status_for_node(change_request, target_node)
        change_request.save(update_fields=["submitted_at", "status"])
        ProjectChangeService._create_review(change_request, target_node.id)

    @staticmethod
    @transaction.atomic
    def approve_review(
        review: ProjectChangeReview, reviewer, comments: str = ""
    ) -> None:
        """
        审核通过，推进到下一节点或完成
        """
        review = ProjectChangeService._lock_review(review)
        ProjectChangeService._ensure_pending_review(review)
        ProjectChangeService._ensure_current_review_node(review)
        change_request = review.change_request
        _, review_nodes = ProjectChangeService._get_review_nodes(change_request)
        workflow_node_id = cast(Any, review).workflow_node_id
        if not workflow_node_id:
            raise ValueError("审核记录缺少工作流节点")

        current_index = next(
            (
                index
                for index, node in enumerate(review_nodes)
                if node.id == workflow_node_id
            ),
            None,
        )
        if current_index is None:
            raise ValueError("当前审核节点不在流程配置中")

        next_node = None
        for node in review_nodes[current_index + 1 :]:
            if node.role == "TEACHER" and not ProjectChangeService._has_teacher_review(
                change_request
            ):
                continue
            next_node = node
            break

        review.status = ProjectChangeReview.ReviewStatus.APPROVED
        review.reviewer = reviewer
        review.comments = comments
        review.reviewed_at = timezone.now()
        review.save(update_fields=["status", "reviewer", "comments", "reviewed_at"])

        if next_node:
            ProjectChangeService._set_status_for_node(change_request, next_node)
            change_request.save(update_fields=["status"])
            ProjectChangeService._create_review(change_request, next_node.id)
            return

        change_request.status = ProjectChangeRequest.ChangeStatus.APPROVED
        change_request.reviewed_at = timezone.now()
        change_request.save(update_fields=["status", "reviewed_at"])
        ProjectChangeService.apply_change(change_request)

    @staticmethod
    @transaction.atomic
    def reject_review(
        review: ProjectChangeReview, reviewer, comments: str = ""
    ) -> None:
        """
        审核驳回，结束流程
        """
        review = ProjectChangeService._lock_review(review)
        ProjectChangeService._ensure_pending_review(review)
        ProjectChangeService._ensure_current_review_node(review)

        review.status = ProjectChangeReview.ReviewStatus.REJECTED
        review.reviewer = reviewer
        review.comments = comments
        review.reviewed_at = timezone.now()
        review.save(update_fields=["status", "reviewer", "comments", "reviewed_at"])

        change_request = review.change_request
        change_request.status = ProjectChangeRequest.ChangeStatus.REJECTED
        change_request.reviewed_at = timezone.now()
        change_request.save(update_fields=["status", "reviewed_at"])

    @staticmethod
    def apply_change(change_request: ProjectChangeRequest) -> None:
        """
        变更/延期/终止生效
        """
        project = change_request.project
        request_type = change_request.request_type

        if request_type == ProjectChangeRequest.ChangeType.CHANGE:
            change_data = change_request.change_data or {}
            allowed_fields = {
                "title",
                "description",
                "level_id",
                "category_id",
                "source_id",
                "approved_budget",
                "expected_results",
                "is_key_field",
                "key_domain_code",
            }
            updated_fields = []
            for field, value in change_data.items():
                if field in allowed_fields:
                    setattr(project, field, value)
                    updated_fields.append(field)
            if updated_fields:
                project.save(update_fields=updated_fields)
