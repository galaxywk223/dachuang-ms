"""
项目变更/延期/终止 业务逻辑
"""

from django.utils import timezone
from django.db import transaction

from ..models import Project, ProjectChangeRequest, ProjectChangeReview


class ProjectChangeService:
    """
    项目异动申请服务类
    """

    @staticmethod
    def _has_teacher_review(change_request: ProjectChangeRequest) -> bool:
        return change_request.project.advisors.exists()

    @staticmethod
    def _create_review(
        change_request: ProjectChangeRequest, review_level: str
    ) -> ProjectChangeReview:
        return ProjectChangeReview.objects.create(
            change_request=change_request,
            review_level=review_level,
            status=ProjectChangeReview.ReviewStatus.PENDING,
        )

    @staticmethod
    @transaction.atomic
    def submit_request(change_request: ProjectChangeRequest) -> None:
        """
        提交变更申请，创建首个审核节点
        """
        change_request.submitted_at = timezone.now()

        if ProjectChangeService._has_teacher_review(change_request):
            change_request.status = ProjectChangeRequest.ChangeStatus.TEACHER_REVIEWING
            change_request.save(update_fields=["submitted_at", "status"])
            ProjectChangeService._create_review(
                change_request, ProjectChangeReview.ReviewLevel.TEACHER
            )
            return

        change_request.status = ProjectChangeRequest.ChangeStatus.LEVEL2_REVIEWING
        change_request.save(update_fields=["submitted_at", "status"])
        ProjectChangeService._create_review(
            change_request, ProjectChangeReview.ReviewLevel.LEVEL2
        )

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

        if review.review_level == ProjectChangeReview.ReviewLevel.TEACHER:
            change_request.status = ProjectChangeRequest.ChangeStatus.LEVEL2_REVIEWING
            change_request.save(update_fields=["status"])
            ProjectChangeService._create_review(
                change_request, ProjectChangeReview.ReviewLevel.LEVEL2
            )
            return

        if review.review_level == ProjectChangeReview.ReviewLevel.LEVEL2:
            change_request.status = ProjectChangeRequest.ChangeStatus.LEVEL1_REVIEWING
            change_request.save(update_fields=["status"])
            ProjectChangeService._create_review(
                change_request, ProjectChangeReview.ReviewLevel.LEVEL1
            )
            return

        if review.review_level == ProjectChangeReview.ReviewLevel.LEVEL1:
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
