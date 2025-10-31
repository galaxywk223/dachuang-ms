"""
审核业务逻辑层
"""

from django.utils import timezone
from django.db import transaction
from .models import Review
from apps.projects.models import Project


class ReviewService:
    """
    审核服务类
    """

    @staticmethod
    @transaction.atomic
    def create_review(project, review_type, review_level):
        """
        创建审核记录
        """
        return Review.objects.create(
            project=project,
            review_type=review_type,
            review_level=review_level,
            status=Review.ReviewStatus.PENDING,
        )

    @staticmethod
    @transaction.atomic
    def create_level2_review(project):
        """
        创建二级审核记录（申报审核）
        """
        # 更新项目状态
        project.status = Project.ProjectStatus.LEVEL2_REVIEWING
        project.save()

        return ReviewService.create_review(
            project=project,
            review_type=Review.ReviewType.APPLICATION,
            review_level=Review.ReviewLevel.LEVEL2,
        )

    @staticmethod
    @transaction.atomic
    def create_level1_review(project):
        """
        创建一级审核记录
        """
        return ReviewService.create_review(
            project=project,
            review_type=Review.ReviewType.APPLICATION,
            review_level=Review.ReviewLevel.LEVEL1,
        )

    @staticmethod
    @transaction.atomic
    def approve_review(review, reviewer, comments="", score=None):
        """
        审核通过
        """
        review.status = Review.ReviewStatus.APPROVED
        review.reviewer = reviewer
        review.comments = comments
        review.score = score
        review.reviewed_at = timezone.now()
        review.save()

        # 更新项目状态
        project = review.project
        if review.review_level == Review.ReviewLevel.LEVEL2:
            project.status = Project.ProjectStatus.LEVEL2_APPROVED
        elif review.review_level == Review.ReviewLevel.LEVEL1:
            project.status = Project.ProjectStatus.LEVEL1_APPROVED
            # 一级审核通过后，项目进入进行中状态
            project.status = Project.ProjectStatus.IN_PROGRESS

        project.save()
        return True

    @staticmethod
    @transaction.atomic
    def reject_review(review, reviewer, comments=""):
        """
        审核不通过
        """
        review.status = Review.ReviewStatus.REJECTED
        review.reviewer = reviewer
        review.comments = comments
        review.reviewed_at = timezone.now()
        review.save()

        # 更新项目状态
        project = review.project
        if review.review_level == Review.ReviewLevel.LEVEL2:
            project.status = Project.ProjectStatus.LEVEL2_REJECTED
        elif review.review_level == Review.ReviewLevel.LEVEL1:
            project.status = Project.ProjectStatus.LEVEL1_REJECTED

        project.save()
        return True

    @staticmethod
    def get_pending_reviews_for_admin(admin_user):
        """
        获取管理员的待审核列表
        """
        if admin_user.is_level2_admin:
            return Review.objects.filter(
                project__college=admin_user.college,
                review_level=Review.ReviewLevel.LEVEL2,
                status=Review.ReviewStatus.PENDING,
            )
        elif admin_user.is_level1_admin:
            return Review.objects.filter(
                review_level=Review.ReviewLevel.LEVEL1,
                status=Review.ReviewStatus.PENDING,
            )
        return Review.objects.none()
