"""
项目变更/延期/终止 业务逻辑
"""

from django.utils import timezone
from django.db import transaction

from ..models import (
    Project,
    ProjectChangeRequest,
    ProjectChangeReview,
    ProjectPhaseInstance,
)
from apps.system_settings.services import WorkflowService


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
    def _set_status_for_node(
        change_request: ProjectChangeRequest, node_role: str
    ) -> None:
        status_map = {
            "TEACHER": ProjectChangeRequest.ChangeStatus.TEACHER_REVIEWING,
            "LEVEL2_ADMIN": ProjectChangeRequest.ChangeStatus.LEVEL2_REVIEWING,
            "LEVEL1_ADMIN": ProjectChangeRequest.ChangeStatus.LEVEL1_REVIEWING,
        }
        status = status_map.get(node_role)
        if not status:
            raise ValueError(f"不支持的审核角色: {node_role}")
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
    @transaction.atomic
    def submit_request(change_request: ProjectChangeRequest) -> None:
        """
        提交变更申请，创建首个审核节点
        """
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

        ProjectChangeService._set_status_for_node(change_request, target_node.role)
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
        review.status = ProjectChangeReview.ReviewStatus.APPROVED
        review.reviewer = reviewer
        review.comments = comments
        review.reviewed_at = timezone.now()
        review.save(update_fields=["status", "reviewer", "comments", "reviewed_at"])

        change_request = review.change_request
        _, review_nodes = ProjectChangeService._get_review_nodes(change_request)
        if not review.workflow_node_id:
            raise ValueError("审核记录缺少工作流节点")

        current_index = next(
            (
                index
                for index, node in enumerate(review_nodes)
                if node.id == review.workflow_node_id
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

        if next_node:
            ProjectChangeService._set_status_for_node(change_request, next_node.role)
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

        if request_type == ProjectChangeRequest.ChangeType.EXTENSION:
            if change_request.requested_end_date:
                project.end_date = change_request.requested_end_date
                project.save(update_fields=["end_date"])
            return

        if request_type == ProjectChangeRequest.ChangeType.TERMINATION:
            project.status = Project.ProjectStatus.TERMINATED
            project.save(update_fields=["status"])
            return

        if request_type == ProjectChangeRequest.ChangeType.CHANGE:
            change_data = change_request.change_data or {}
            allowed_fields = {
                "title",
                "description",
                "level_id",
                "category_id",
                "source_id",
                "start_date",
                "end_date",
                "budget",
                "approved_budget",
                "research_content",
                "research_plan",
                "expected_results",
                "innovation_points",
                "is_key_field",
                "key_domain_code",
                "category_description",
                "self_funding",
            }
            updated_fields = []
            for field, value in change_data.items():
                if field in allowed_fields:
                    setattr(project, field, value)
                    updated_fields.append(field)
            if updated_fields:
                project.save(update_fields=updated_fields)
