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
        # 更新项目状态（沿用 SUBMITTED 作为在审状态）
        project.status = Project.ProjectStatus.SUBMITTED
        project.save(update_fields=["status"])

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
    def approve_review(review, reviewer, comments="", score=None, closure_rating=None):
        """
        审核通过
        """
        review.status = Review.ReviewStatus.APPROVED
        review.reviewer = reviewer
        review.comments = comments
        review.score = score
        review.reviewed_at = timezone.now()

        # 如果是结题审核，设置评价等级
        if review.review_type == Review.ReviewType.CLOSURE and closure_rating:
            review.closure_rating = closure_rating

        review.save()

        # 更新项目状态
        project = review.project

        # 申报审核
        if review.review_type == Review.ReviewType.APPLICATION:
            if review.review_level == Review.ReviewLevel.LEVEL2:
                # 二级管理员通过后，项目进入进行中（学生可后续结题）
                project.status = Project.ProjectStatus.IN_PROGRESS
            elif review.review_level == Review.ReviewLevel.LEVEL1:
                project.status = Project.ProjectStatus.IN_PROGRESS

        # 结题审核
        elif review.review_type == Review.ReviewType.CLOSURE:
            if review.review_level == Review.ReviewLevel.LEVEL2:
                project.status = Project.ProjectStatus.CLOSURE_LEVEL2_APPROVED
                # 二级审核通过后，自动创建一级审核记录
                ReviewService.create_closure_level1_review(project)
            elif review.review_level == Review.ReviewLevel.LEVEL1:
                project.status = Project.ProjectStatus.CLOSURE_LEVEL1_APPROVED
                # 一级审核通过后，项目结题
                project.status = Project.ProjectStatus.CLOSED

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

        # 申报审核
        if review.review_type == Review.ReviewType.APPLICATION:
            if review.review_level == Review.ReviewLevel.LEVEL2:
                project.status = Project.ProjectStatus.DRAFT
            elif review.review_level == Review.ReviewLevel.LEVEL1:
                project.status = Project.ProjectStatus.DRAFT

        # 结题审核
        elif review.review_type == Review.ReviewType.CLOSURE:
            if review.review_level == Review.ReviewLevel.LEVEL2:
                project.status = Project.ProjectStatus.CLOSURE_LEVEL2_REJECTED
            elif review.review_level == Review.ReviewLevel.LEVEL1:
                project.status = Project.ProjectStatus.CLOSURE_LEVEL1_REJECTED

        project.save()
        return True

    @staticmethod
    @transaction.atomic
    def create_closure_level2_review(project):
        """
        创建结题二级审核记录
        """
        # 更新项目状态
        project.status = Project.ProjectStatus.CLOSURE_LEVEL2_REVIEWING
        project.save()

        return ReviewService.create_review(
            project=project,
            review_type=Review.ReviewType.CLOSURE,
            review_level=Review.ReviewLevel.LEVEL2,
        )

    @staticmethod
    @transaction.atomic
    def create_closure_level1_review(project):
        """
        创建结题一级审核记录
        """
        # 更新项目状态
        project.status = Project.ProjectStatus.CLOSURE_LEVEL1_REVIEWING
        project.save()

        return ReviewService.create_review(
            project=project,
            review_type=Review.ReviewType.CLOSURE,
            review_level=Review.ReviewLevel.LEVEL1,
        )

        project.save()
        return True

    @staticmethod
    def get_pending_reviews_for_admin(admin_user):
        """
        获取管理员的待审核列表
        """
        if admin_user.is_level2_admin:
            return Review.objects.filter(
                project__leader__college=admin_user.college,
                review_level=Review.ReviewLevel.LEVEL2,
                status=Review.ReviewStatus.PENDING,
            )
        elif admin_user.is_level1_admin:
            return Review.objects.filter(
                review_level=Review.ReviewLevel.LEVEL1,
                status=Review.ReviewStatus.PENDING,
            )
        return Review.objects.none()
