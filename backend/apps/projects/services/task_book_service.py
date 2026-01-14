"""
项目任务书/开题服务
"""

from django.db import transaction
from django.utils import timezone
from ..models import Project, ProjectPhaseInstance
from apps.notifications.services import NotificationService
from apps.reviews.models import Review
from apps.reviews.services import ReviewService


class TaskBookService:
    """
    项目任务书服务
    """

    @staticmethod
    @transaction.atomic
    def submit_task_book(
        project, user, task_book_file=None, research_content=None, research_plan=None
    ):
        """
        提交项目任务书
        """
        # 检查项目状态
        if project.status not in [
            Project.ProjectStatus.IN_PROGRESS,
            Project.ProjectStatus.TASK_BOOK_DRAFT,
            Project.ProjectStatus.TASK_BOOK_RETURNED,
        ]:
            raise ValueError("只有立项后的项目才能提交任务书")

        # 检查是否是项目负责人
        if project.leader != user:
            raise ValueError("只有项目负责人可以提交任务书")

        # 更新项目信息
        if task_book_file:
            project.task_book_file = task_book_file
        if research_content:
            project.research_content = research_content
        if research_plan:
            project.research_plan = research_plan

        project.status = Project.ProjectStatus.TASK_BOOK_SUBMITTED
        project.save()

        # 创建或更新阶段实例
        phase_instance, created = ProjectPhaseInstance.objects.get_or_create(
            project=project,
            phase=ProjectPhaseInstance.Phase.TASK_BOOK,
            attempt_no=1,
            defaults={
                "step": ProjectPhaseInstance.Step.TEACHER_REVIEW,
                "state": ProjectPhaseInstance.State.IN_PROGRESS,
                "submitted_at": timezone.now(),
                "created_by": user,
            },
        )

        if not created:
            phase_instance.state = ProjectPhaseInstance.State.IN_PROGRESS
            phase_instance.submitted_at = timezone.now()
            phase_instance.save()

        # 创建导师审核任务
        ReviewService.create_task_book_teacher_review(project)

        # 发送通知
        NotificationService.notify_task_book_submitted(project, user)

        return project

    @staticmethod
    @transaction.atomic
    def review_task_book_teacher(project, reviewer, approved, comment=""):
        """
        导师审核任务书
        """
        if project.status != Project.ProjectStatus.TASK_BOOK_SUBMITTED:
            raise ValueError("项目状态不正确")

        # 查找导师审核记录
        review = Review.objects.filter(
            project=project,
            review_type=Review.ReviewType.TASK_BOOK,
            review_level="TEACHER",
            status=Review.ReviewStatus.PENDING,
        ).first()

        if not review:
            raise ValueError("未找到待审核的任务书")

        # 更新审核记录
        review.status = (
            Review.ReviewStatus.APPROVED if approved else Review.ReviewStatus.REJECTED
        )
        review.comment = comment
        review.reviewed_by = reviewer
        review.reviewed_at = timezone.now()
        review.save()

        # 更新项目状态
        if approved:
            project.status = Project.ProjectStatus.TASK_BOOK_APPROVED
            # 创建学院审核任务
            ReviewService.create_task_book_level2_review(project)
        else:
            project.status = Project.ProjectStatus.TASK_BOOK_RETURNED
            # 更新阶段实例状态
            ProjectPhaseInstance.objects.filter(
                project=project, phase=ProjectPhaseInstance.Phase.TASK_BOOK
            ).update(state=ProjectPhaseInstance.State.RETURNED)

        project.save()

        # 发送通知
        NotificationService.notify_task_book_reviewed(
            project, reviewer, approved, comment, "teacher"
        )

        return project

    @staticmethod
    @transaction.atomic
    def review_task_book_level2(project, reviewer, approved, comment=""):
        """
        学院审核任务书
        """
        if project.status != Project.ProjectStatus.TASK_BOOK_APPROVED:
            raise ValueError("项目状态不正确，必须先通过导师审核")

        # 查找学院审核记录
        review = Review.objects.filter(
            project=project,
            review_type=Review.ReviewType.TASK_BOOK,
            review_level="LEVEL2",
            status=Review.ReviewStatus.PENDING,
        ).first()

        if not review:
            raise ValueError("未找到待审核的任务书")

        # 更新审核记录
        review.status = (
            Review.ReviewStatus.APPROVED if approved else Review.ReviewStatus.REJECTED
        )
        review.comment = comment
        review.reviewed_by = reviewer
        review.reviewed_at = timezone.now()
        review.save()

        # 更新项目状态和阶段实例
        if approved:
            project.status = Project.ProjectStatus.IN_PROGRESS
            ProjectPhaseInstance.objects.filter(
                project=project, phase=ProjectPhaseInstance.Phase.TASK_BOOK
            ).update(
                state=ProjectPhaseInstance.State.COMPLETED, completed_at=timezone.now()
            )
        else:
            project.status = Project.ProjectStatus.TASK_BOOK_RETURNED
            ProjectPhaseInstance.objects.filter(
                project=project, phase=ProjectPhaseInstance.Phase.TASK_BOOK
            ).update(state=ProjectPhaseInstance.State.RETURNED)

        project.save()

        # 发送通知
        NotificationService.notify_task_book_reviewed(
            project, reviewer, approved, comment, "level2"
        )

        return project

    @staticmethod
    def can_submit_midterm(project):
        """
        检查项目是否可以提交中期报告
        """
        # 必须完成任务书审核
        task_book_phase = ProjectPhaseInstance.objects.filter(
            project=project,
            phase=ProjectPhaseInstance.Phase.TASK_BOOK,
            state=ProjectPhaseInstance.State.COMPLETED,
        ).exists()

        return task_book_phase or project.status in [
            Project.ProjectStatus.IN_PROGRESS,
            Project.ProjectStatus.MID_TERM_DRAFT,
        ]
