"""
经费流程服务
"""

from django.utils import timezone
from django.db import transaction
from typing import Any, cast

from apps.system_settings.models import WorkflowNode
from apps.system_settings.services import WorkflowService, AdminAssignmentService

from ..models import ProjectExpenditure, ProjectExpenditureReview


class ExpenditureWorkflowService:
    @staticmethod
    def _has_teacher_review(expenditure: ProjectExpenditure) -> bool:
        return expenditure.project.advisors.exists()

    @staticmethod
    def _get_review_nodes(expenditure: ProjectExpenditure):
        workflow = WorkflowService.get_active_workflow(
            "BUDGET", expenditure.project.batch
        )
        if not workflow:
            raise ValueError("经费流程未配置可用审核节点")

        persisted_node_ids = set(
            WorkflowNode.objects.filter(workflow=workflow, is_active=True).values_list(
                "id", flat=True
            )
        )
        nodes = WorkflowService.get_nodes("BUDGET", expenditure.project.batch)
        review_nodes = [
            node
            for node in nodes
            if node.node_type != "SUBMIT" and node.id in persisted_node_ids
        ]
        if not review_nodes:
            raise ValueError("经费流程未配置可用审核节点")
        return review_nodes

    @staticmethod
    def _create_review(
        expenditure: ProjectExpenditure, workflow_node_id: int
    ) -> ProjectExpenditureReview:
        return ProjectExpenditureReview.objects.create(
            expenditure=expenditure,
            workflow_node_id=workflow_node_id,
            status=ProjectExpenditureReview.ReviewStatus.PENDING,
        )

    @staticmethod
    def _lock_review(review: ProjectExpenditureReview) -> ProjectExpenditureReview:
        if not review.pk:
            raise ValueError("审核记录不存在")

        try:
            locked_review = ProjectExpenditureReview.objects.select_for_update().get(
                pk=review.pk
            )
            expenditure = ProjectExpenditure.objects.select_for_update().get(
                pk=locked_review.expenditure_id
            )
        except ProjectExpenditureReview.DoesNotExist as exc:
            raise ValueError("审核记录不存在") from exc
        except ProjectExpenditure.DoesNotExist as exc:
            raise ValueError("经费记录不存在") from exc

        locked_review.expenditure = expenditure
        return locked_review

    @staticmethod
    def _get_next_review_node(expenditure: ProjectExpenditure, current_node_id: int):
        review_nodes = ExpenditureWorkflowService._get_review_nodes(expenditure)
        current_index = next(
            (
                index
                for index, node in enumerate(review_nodes)
                if node.id == current_node_id
            ),
            None,
        )
        if current_index is None:
            raise ValueError("当前审核节点不在经费流程配置中")
        next_node = None
        for node in review_nodes[current_index + 1 :]:
            if node.role == "TEACHER" and not ExpenditureWorkflowService._has_teacher_review(
                expenditure
            ):
                continue
            next_node = node
            break
        return next_node

    @staticmethod
    def _ensure_pending_review(review: ProjectExpenditureReview) -> None:
        if review.status != ProjectExpenditureReview.ReviewStatus.PENDING:
            raise ValueError("当前审核记录不可处理")

        expenditure = review.expenditure
        if expenditure.status != ProjectExpenditure.ExpenditureStatus.PENDING:
            raise ValueError("当前经费流程已结束，无法处理该审核记录")

    @staticmethod
    def _ensure_current_review_node(review: ProjectExpenditureReview) -> None:
        expenditure = review.expenditure
        workflow_node_id = cast(Any, review).workflow_node_id
        if not workflow_node_id or expenditure.current_node_id != workflow_node_id:
            raise ValueError("审核记录不是当前经费流程节点")

    @staticmethod
    @transaction.atomic
    def start_workflow(expenditure: ProjectExpenditure) -> None:
        review_nodes = ExpenditureWorkflowService._get_review_nodes(expenditure)
        next_node = None
        for node in review_nodes:
            if node.role == "TEACHER" and not ExpenditureWorkflowService._has_teacher_review(
                expenditure
            ):
                continue
            next_node = node
            break

        if next_node:
            ExpenditureWorkflowService._create_review(expenditure, next_node.id)
            expenditure.current_node_id = next_node.id
            expenditure.status = ProjectExpenditure.ExpenditureStatus.PENDING
            expenditure.save(update_fields=["current_node_id", "status", "updated_at"])
            return

        raise ValueError("经费流程未配置可用审核节点")

    @staticmethod
    @transaction.atomic
    def apply_leader_review(
        expenditure: ProjectExpenditure,
        reviewer,
        approved: bool,
        comment: str = "",
    ) -> None:
        if expenditure.leader_review_status != ProjectExpenditure.LeaderReviewStatus.PENDING:
            raise ValueError("当前状态不允许负责人审核")

        expenditure.leader_review_status = (
            ProjectExpenditure.LeaderReviewStatus.APPROVED
            if approved
            else ProjectExpenditure.LeaderReviewStatus.REJECTED
        )
        expenditure.leader_reviewed_by = reviewer
        expenditure.leader_reviewed_at = timezone.now()
        expenditure.leader_review_comment = comment or ""

        if not approved:
            expenditure.status = ProjectExpenditure.ExpenditureStatus.REJECTED
            expenditure.reviewed_by = reviewer
            expenditure.reviewed_at = timezone.now()
            expenditure.review_comment = comment or ""
            expenditure.current_node_id = None
            expenditure.save(
                update_fields=[
                    "leader_review_status",
                    "leader_reviewed_by",
                    "leader_reviewed_at",
                    "leader_review_comment",
                    "status",
                    "reviewed_by",
                    "reviewed_at",
                    "review_comment",
                    "current_node_id",
                    "updated_at",
                ]
            )
            return

        expenditure.save(
            update_fields=[
                "leader_review_status",
                "leader_reviewed_by",
                "leader_reviewed_at",
                "leader_review_comment",
                "updated_at",
            ]
        )
        ExpenditureWorkflowService.start_workflow(expenditure)

    @staticmethod
    @transaction.atomic
    def approve_review(
        review: ProjectExpenditureReview, reviewer, comment: str = ""
    ) -> None:
        review = ExpenditureWorkflowService._lock_review(review)
        ExpenditureWorkflowService._ensure_pending_review(review)
        expenditure = review.expenditure
        workflow_node_id = cast(Any, review).workflow_node_id
        next_node = ExpenditureWorkflowService._get_next_review_node(
            expenditure, workflow_node_id
        )
        ExpenditureWorkflowService._ensure_current_review_node(review)

        review.status = ProjectExpenditureReview.ReviewStatus.APPROVED
        review.reviewer = reviewer
        review.comments = comment or ""
        review.reviewed_at = timezone.now()
        review.save(update_fields=["status", "reviewer", "comments", "reviewed_at"])

        if next_node:
            ExpenditureWorkflowService._create_review(expenditure, next_node.id)
            expenditure.current_node_id = next_node.id
            expenditure.save(update_fields=["current_node_id", "updated_at"])
            return

        expenditure.status = ProjectExpenditure.ExpenditureStatus.APPROVED
        expenditure.reviewed_by = reviewer
        expenditure.reviewed_at = timezone.now()
        expenditure.review_comment = comment or ""
        expenditure.current_node_id = None
        expenditure.save(
            update_fields=[
                "status",
                "reviewed_by",
                "reviewed_at",
                "review_comment",
                "current_node_id",
                "updated_at",
            ]
        )

    @staticmethod
    @transaction.atomic
    def reject_review(
        review: ProjectExpenditureReview, reviewer, comment: str = ""
    ) -> None:
        review = ExpenditureWorkflowService._lock_review(review)
        ExpenditureWorkflowService._ensure_pending_review(review)
        workflow_node_id = cast(Any, review).workflow_node_id
        ExpenditureWorkflowService._get_next_review_node(
            review.expenditure, workflow_node_id
        )
        ExpenditureWorkflowService._ensure_current_review_node(review)

        review.status = ProjectExpenditureReview.ReviewStatus.REJECTED
        review.reviewer = reviewer
        review.comments = comment or ""
        review.reviewed_at = timezone.now()
        review.save(update_fields=["status", "reviewer", "comments", "reviewed_at"])

        expenditure = review.expenditure
        expenditure.status = ProjectExpenditure.ExpenditureStatus.REJECTED
        expenditure.reviewed_by = reviewer
        expenditure.reviewed_at = timezone.now()
        expenditure.review_comment = comment or ""
        expenditure.current_node_id = None
        expenditure.save(
            update_fields=[
                "status",
                "reviewed_by",
                "reviewed_at",
                "review_comment",
                "current_node_id",
                "updated_at",
            ]
        )

    @staticmethod
    def get_pending_review_for_user(expenditure: ProjectExpenditure, user):
        if expenditure.status in (
            ProjectExpenditure.ExpenditureStatus.APPROVED,
            ProjectExpenditure.ExpenditureStatus.REJECTED,
        ):
            return None

        if (
            expenditure.leader_review_status
            == ProjectExpenditure.LeaderReviewStatus.PENDING
        ):
            if expenditure.project.leader_id == user.id:
                return {"type": "LEADER", "review": None}
            return None
        if not expenditure.current_node_id:
            return None

        pending_review = (
            ProjectExpenditureReview.objects.filter(
                expenditure=expenditure,
                status=ProjectExpenditureReview.ReviewStatus.PENDING,
                workflow_node_id=expenditure.current_node_id,
            )
            .select_related("workflow_node", "workflow_node__role_fk")
            .order_by("id")
            .first()
        )
        if not pending_review:
            return None

        node = pending_review.workflow_node
        if not node:
            return None
        role_code = node.get_role_code()

        if role_code == "TEACHER":
            if (user.is_teacher or user.is_admin) and expenditure.project.advisors.filter(
                user=user
            ).exists():
                return {"type": "NODE", "review": pending_review}
            return None

        if user.is_admin:
            try:
                admin_user = AdminAssignmentService.resolve_admin_user(
                    expenditure.project, "BUDGET", node
                )
            except ValueError:
                return None
            if admin_user.id == user.id:
                return {"type": "NODE", "review": pending_review}
        return None
