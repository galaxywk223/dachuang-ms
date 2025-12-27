"""
审核业务逻辑层
"""

from django.utils import timezone
from django.db import transaction
from ..models import (
    Review,
    ExpertGroup,
)
from apps.projects.models import Project
from apps.projects.models import ProjectPhaseInstance
from apps.projects.services.phase_service import ProjectPhaseService
from apps.system_settings.services import SystemSettingService


class ReviewService:
    """
    审核服务类
    """

    @staticmethod
    @transaction.atomic
    def create_review(
        project,
        review_type,
        review_level,
        *,
        phase_instance: ProjectPhaseInstance | None = None,
    ):
        """
        创建审核记录
        """
        return Review.objects.create(
            project=project,
            phase_instance=phase_instance,
            review_type=review_type,
            review_level=review_level,
            status=Review.ReviewStatus.PENDING,
        )

    @staticmethod
    @transaction.atomic
    def create_teacher_review(project):
        """
        创建导师审核记录（申报审核）
        """
        phase_instance = ProjectPhaseService.ensure_current(
            project, ProjectPhaseInstance.Phase.APPLICATION, step="TEACHER_REVIEWING"
        )
        project.status = Project.ProjectStatus.TEACHER_AUDITING
        project.save(update_fields=["status"])

        return ReviewService.create_review(
            project=project,
            review_type=Review.ReviewType.APPLICATION,
            review_level=Review.ReviewLevel.TEACHER,
            phase_instance=phase_instance,
        )

    @staticmethod
    @transaction.atomic
    def create_level2_review(project):
        """
        创建二级审核记录（申报审核 - 学院）
        """
        # 导师通过后进入二级审核
        # status usually SUBMITTED or COLLEGE_AUDITING
        # If we use strict statuses: COLLEGE_AUDITING
        project.status = Project.ProjectStatus.COLLEGE_AUDITING
        project.save(update_fields=["status"])

        phase_instance = ProjectPhaseService.ensure_current(
            project, ProjectPhaseInstance.Phase.APPLICATION, step="COLLEGE_EXPERT_SCORING"
        )
        return ReviewService.create_review(
            project=project,
            review_type=Review.ReviewType.APPLICATION,
            review_level=Review.ReviewLevel.LEVEL2,
            phase_instance=phase_instance,
        )

    @staticmethod
    @transaction.atomic
    def create_level1_review(project):
        """
        创建一级审核记录
        """
        existing = Review.objects.filter(
            project=project,
            review_type=Review.ReviewType.APPLICATION,
            review_level=Review.ReviewLevel.LEVEL1,
            status=Review.ReviewStatus.PENDING,
        ).first()
        if existing:
            project.status = Project.ProjectStatus.LEVEL1_AUDITING
            project.save(update_fields=["status"])
            return existing

        phase_instance = ProjectPhaseService.ensure_current(
            project, ProjectPhaseInstance.Phase.APPLICATION, step="SCHOOL_EXPERT_SCORING"
        )
        project.status = Project.ProjectStatus.LEVEL1_AUDITING
        project.save(update_fields=["status"])
        return ReviewService.create_review(
            project=project,
            review_type=Review.ReviewType.APPLICATION,
            review_level=Review.ReviewLevel.LEVEL1,
            phase_instance=phase_instance,
        )

    @staticmethod
    @transaction.atomic
    def approve_review(review, reviewer, comments="", score=None, closure_rating=None):
        """
        审核通过
        """
        if reviewer.role == "EXPERT":
            review.status = Review.ReviewStatus.APPROVED
            review.reviewer = reviewer
            review.comments = comments
            review.score = score
            review.reviewed_at = timezone.now()
            if review.review_type == Review.ReviewType.CLOSURE and closure_rating:
                review.closure_rating = closure_rating
            review.save()
            return True

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
            if review.review_level == Review.ReviewLevel.TEACHER:
                # 导师通过，进入二级审核 (学院)
                project.status = Project.ProjectStatus.TEACHER_APPROVED
                ReviewService.create_level2_review(project)
            elif review.review_level == Review.ReviewLevel.LEVEL2:
                # 二级审核通过后，提交至校级审核
                if not Review.objects.filter(
                    project=project,
                    review_type=Review.ReviewType.APPLICATION,
                    review_level=Review.ReviewLevel.LEVEL1,
                    status=Review.ReviewStatus.PENDING,
                ).exists():
                    ReviewService.create_level1_review(project)
                else:
                    project.status = Project.ProjectStatus.LEVEL1_AUDITING
                    project.save(update_fields=["status"])
            elif review.review_level == Review.ReviewLevel.LEVEL1:
                project.status = Project.ProjectStatus.IN_PROGRESS
                if review.phase_instance:
                    ProjectPhaseService.mark_completed(review.phase_instance, step="PUBLISHED")

        # 中期审核
        elif review.review_type == Review.ReviewType.MID_TERM:
            if review.review_level == Review.ReviewLevel.TEACHER:
                # 导师通过后进入院级专家评审（由院级管理员分配专家任务）
                project.status = Project.ProjectStatus.MID_TERM_REVIEWING
                project.save(update_fields=["status"])
                phase_instance = ProjectPhaseService.ensure_current(
                    project, ProjectPhaseInstance.Phase.MID_TERM, step="COLLEGE_EXPERT_REVIEWING"
                )
                review.phase_instance = phase_instance
                review.save(update_fields=["phase_instance"])
            elif review.review_level == Review.ReviewLevel.LEVEL2:
                project.status = Project.ProjectStatus.READY_FOR_CLOSURE
                if review.phase_instance:
                    ProjectPhaseService.mark_completed(review.phase_instance, step="COMPLETED")

        # 结题审核
        elif review.review_type == Review.ReviewType.CLOSURE:
            if review.review_level == Review.ReviewLevel.TEACHER:
                # 导师通过后进入院级专家评审（由院级管理员分配专家任务）
                project.status = Project.ProjectStatus.CLOSURE_LEVEL2_REVIEWING
                project.save(update_fields=["status"])
                phase_instance = ProjectPhaseService.ensure_current(
                    project, ProjectPhaseInstance.Phase.CLOSURE, step="COLLEGE_EXPERT_SCORING"
                )
                review.phase_instance = phase_instance
                review.save(update_fields=["phase_instance"])
            elif review.review_level == Review.ReviewLevel.LEVEL2:
                # 二级管理员确认后进入校级专家评审（legacy admin-review 路径）
                project.status = Project.ProjectStatus.CLOSURE_LEVEL1_REVIEWING
                phase_instance = ProjectPhaseService.ensure_current(
                    project, ProjectPhaseInstance.Phase.CLOSURE, step="SCHOOL_EXPERT_SCORING"
                )
                review.phase_instance = phase_instance
                review.save(update_fields=["phase_instance"])
            elif review.review_level == Review.ReviewLevel.LEVEL1:
                project.status = Project.ProjectStatus.CLOSURE_LEVEL1_APPROVED
                # 一级审核通过后，项目结题
                project.status = Project.ProjectStatus.CLOSED
                from apps.projects.models import ProjectArchive
                if not hasattr(project, "archive"):
                    ProjectArchive.objects.create(
                        project=project,
                        snapshot={
                            "project_no": project.project_no,
                            "title": project.title,
                            "leader": project.leader_id,
                            "status": project.status,
                        },
                        attachments=[],
                    )
                if review.phase_instance:
                    ProjectPhaseService.mark_completed(review.phase_instance, step="COMPLETED")

        project.save()
        return True

    @staticmethod
    @transaction.atomic
    def reject_review(review, reviewer, comments="", reject_to=None):
        """
        审核不通过
        """
        if reviewer.role == "EXPERT":
            review.status = Review.ReviewStatus.REJECTED
            review.reviewer = reviewer
            review.comments = comments
            review.reviewed_at = timezone.now()
            review.save()
            return True

        review.status = Review.ReviewStatus.REJECTED
        review.reviewer = reviewer
        review.comments = comments
        review.reviewed_at = timezone.now()
        review.save()

        # 更新项目状态
        project = review.project

        # 申报审核
        if review.review_type == Review.ReviewType.APPLICATION:
            process_rules = SystemSettingService.get_setting(
                "PROCESS_RULES", batch=project.batch
            )
            reject_to_previous = bool(process_rules.get("reject_to_previous", False))

            if review.review_level == Review.ReviewLevel.TEACHER:
                project.status = Project.ProjectStatus.TEACHER_REJECTED
            elif review.review_level == Review.ReviewLevel.LEVEL2:
                project.status = (
                    Project.ProjectStatus.TEACHER_REJECTED
                    if reject_to_previous
                    else Project.ProjectStatus.APPLICATION_RETURNED
                )
                if not reject_to_previous and review.phase_instance:
                    ProjectPhaseService.mark_returned(
                        review.phase_instance,
                        return_to=ProjectPhaseInstance.ReturnTo.STUDENT,
                        reason=comments,
                    )
            elif review.review_level == Review.ReviewLevel.LEVEL1:
                project.status = (
                    Project.ProjectStatus.TEACHER_REJECTED
                    if reject_to_previous
                    else Project.ProjectStatus.APPLICATION_RETURNED
                )
                if not reject_to_previous and review.phase_instance:
                    ProjectPhaseService.mark_returned(
                        review.phase_instance,
                        return_to=ProjectPhaseInstance.ReturnTo.STUDENT,
                        reason=comments,
                    )

        # 中期审核
        elif review.review_type == Review.ReviewType.MID_TERM:
            project.status = Project.ProjectStatus.MID_TERM_REJECTED

        # 结题审核
        elif review.review_type == Review.ReviewType.CLOSURE:
            if review.review_level == Review.ReviewLevel.TEACHER:
                project.status = Project.ProjectStatus.CLOSURE_DRAFT
            elif review.review_level == Review.ReviewLevel.LEVEL2:
                project.status = Project.ProjectStatus.CLOSURE_LEVEL2_REJECTED
            elif review.review_level == Review.ReviewLevel.LEVEL1:
                if reject_to == "teacher":
                    project.status = Project.ProjectStatus.CLOSURE_SUBMITTED
                    ReviewService.create_closure_teacher_review(project)
                elif reject_to == "student":
                    project.status = Project.ProjectStatus.CLOSURE_DRAFT
                else:
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

        phase_instance = ProjectPhaseService.ensure_current(
            project, ProjectPhaseInstance.Phase.CLOSURE, step="COLLEGE_EXPERT_SCORING"
        )
        return ReviewService.create_review(
            project=project,
            review_type=Review.ReviewType.CLOSURE,
            review_level=Review.ReviewLevel.LEVEL2,
            phase_instance=phase_instance,
        )

    @staticmethod
    @transaction.atomic
    def create_closure_level1_review(project):
        """
        创建结题一级审核记录
        """
        existing = Review.objects.filter(
            project=project,
            review_type=Review.ReviewType.CLOSURE,
            review_level=Review.ReviewLevel.LEVEL1,
            status=Review.ReviewStatus.PENDING,
        ).first()
        if existing:
            project.status = Project.ProjectStatus.CLOSURE_LEVEL1_REVIEWING
            project.save(update_fields=["status"])
            return existing

        phase_instance = ProjectPhaseService.ensure_current(
            project, ProjectPhaseInstance.Phase.CLOSURE, step="SCHOOL_EXPERT_SCORING"
        )
        # 更新项目状态
        project.status = Project.ProjectStatus.CLOSURE_LEVEL1_REVIEWING
        project.save(update_fields=["status"])

        return ReviewService.create_review(
            project=project,
            review_type=Review.ReviewType.CLOSURE,
            review_level=Review.ReviewLevel.LEVEL1,
            phase_instance=phase_instance,
        )

    @staticmethod
    @transaction.atomic
    def create_mid_term_review(project):
        """
        创建中期审核记录（二级审核）
        """
        # 更新项目状态
        project.status = Project.ProjectStatus.MID_TERM_REVIEWING
        project.save(update_fields=["status"])

        phase_instance = ProjectPhaseService.ensure_current(
            project, ProjectPhaseInstance.Phase.MID_TERM, step="COLLEGE_EXPERT_REVIEWING"
        )
        return phase_instance

    @staticmethod
    @transaction.atomic
    def create_mid_term_teacher_review(project):
        """
        创建中期审核记录（导师审核）
        """
        phase_instance = ProjectPhaseService.ensure_current(
            project, ProjectPhaseInstance.Phase.MID_TERM, step="TEACHER_REVIEWING"
        )
        existing = Review.objects.filter(
            project=project,
            review_type=Review.ReviewType.MID_TERM,
            review_level=Review.ReviewLevel.TEACHER,
            status=Review.ReviewStatus.PENDING,
        ).first()
        if existing:
            return existing

        return ReviewService.create_review(
            project=project,
            review_type=Review.ReviewType.MID_TERM,
            review_level=Review.ReviewLevel.TEACHER,
            phase_instance=phase_instance,
        )

    @staticmethod
    @transaction.atomic
    def create_closure_teacher_review(project):
        """
        创建结题审核记录（导师审核）
        """
        existing = Review.objects.filter(
            project=project,
            review_type=Review.ReviewType.CLOSURE,
            review_level=Review.ReviewLevel.TEACHER,
            status=Review.ReviewStatus.PENDING,
        ).first()
        if existing:
            return existing

        phase_instance = ProjectPhaseService.ensure_current(
            project, ProjectPhaseInstance.Phase.CLOSURE, step="TEACHER_REVIEWING"
        )
        return ReviewService.create_review(
            project=project,
            review_type=Review.ReviewType.CLOSURE,
            review_level=Review.ReviewLevel.TEACHER,
            phase_instance=phase_instance,
        )


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
                reviewer__isnull=True,
            )
        elif admin_user.is_level1_admin:
            return Review.objects.filter(
                review_level=Review.ReviewLevel.LEVEL1,
                status=Review.ReviewStatus.PENDING,
                reviewer__isnull=True,
            )
        return Review.objects.none()

    @staticmethod
    def assign_project_to_group(project_ids, group_id, review_type=Review.ReviewType.APPLICATION, review_level=Review.ReviewLevel.LEVEL2, creator=None):
        """
        批量分配项目给专家组
        """
        group = ExpertGroup.objects.get(pk=group_id)
        experts = group.members.all()
        created_reviews = []

        with transaction.atomic():
            for pid in project_ids:
                try:
                    project = Project.objects.get(pk=pid)
                except Project.DoesNotExist:
                    continue

                step = "COLLEGE_EXPERT_SCORING"
                if review_type == Review.ReviewType.MID_TERM:
                    step = "COLLEGE_EXPERT_REVIEWING"
                if review_level == Review.ReviewLevel.LEVEL1:
                    step = "SCHOOL_EXPERT_SCORING"

                phase_instance = ProjectPhaseService.ensure_current(
                    project,
                    review_type,
                    created_by=creator,
                    step=step,
                )
                
                for expert in experts:
                    # Check duplication
                    if not Review.objects.filter(
                        project=project,
                        reviewer=expert,
                        review_type=review_type,
                        review_level=review_level,
                        phase_instance=phase_instance,
                    ).exists():
                        review = Review.objects.create(
                            project=project,
                            phase_instance=phase_instance,
                            review_type=review_type,
                            review_level=review_level,
                            reviewer=expert,
                            status=Review.ReviewStatus.PENDING
                        )
                        created_reviews.append(review)
                        
        return created_reviews

