"""
审核业务逻辑层
"""

from django.utils import timezone
import logging
from django.db import transaction
from ..models import (
    Review,
    ExpertGroup,
)
from apps.projects.models import Project
from apps.projects.models import ProjectPhaseInstance
from apps.projects.services.phase_service import ProjectPhaseService
from apps.projects.services.archive_service import ensure_project_archive
from apps.system_settings.services import SystemSettingService, WorkflowService
from apps.notifications.services import NotificationService


class ReviewService:
    """
    审核服务类
    """
    logger = logging.getLogger(__name__)

    @staticmethod
    def _normalize_score_details(review, score, score_details):
        """
        根据评审模板计算总分，并规范评分明细
        """
        if not review.review_template:
            return score, []

        items = list(review.review_template.items.all())
        if not items:
            return score, score_details or []

        detail_map = {}
        for item in score_details or []:
            try:
                item_id = int(item.get("item_id"))
                detail_map[item_id] = item
            except (TypeError, ValueError, AttributeError) as exc:
                ReviewService.logger.debug("Skip invalid score detail: %s", exc)
                continue

        total = 0
        normalized = []
        for item in items:
            detail = detail_map.get(item.id, {})
            raw_score = detail.get("score")
            if raw_score is None or raw_score == "":
                if item.is_required:
                    raise ValueError(f"评分项“{item.title}”不能为空")
                raw_score = 0
            try:
                raw_score = int(raw_score)
            except (TypeError, ValueError):
                raise ValueError(f"评分项“{item.title}”分值格式错误")
            if raw_score < 0 or raw_score > item.max_score:
                raise ValueError(f"评分项“{item.title}”超出范围")

            weighted = raw_score
            if item.weight:
                weighted = int(round(raw_score * float(item.weight) / 100))
            total += weighted
            normalized.append(
                {
                    "item_id": item.id,
                    "title": item.title,
                    "score": raw_score,
                    "weight": float(item.weight),
                    "weighted_score": weighted,
                    "max_score": item.max_score,
                }
            )

        return total, normalized

    @staticmethod
    @transaction.atomic
    def create_review(
        project,
        review_type,
        review_level,
        *,
        phase_instance: ProjectPhaseInstance | None = None,
        review_template_id=None,
    ):
        """
        创建审核记录
        """
        return Review.objects.create(
            project=project,
            phase_instance=phase_instance,
            review_type=review_type,
            review_level=review_level,
            review_template_id=review_template_id,
            status=Review.ReviewStatus.PENDING,
        )

    @staticmethod
    @transaction.atomic
    def create_teacher_review(project):
        """
        创建导师审核记录（申报审核）
        """
        initial_node = WorkflowService.get_initial_node(
            ProjectPhaseInstance.Phase.APPLICATION, project.batch
        )
        step = initial_node.code if initial_node else "TEACHER_REVIEW"
        review_level = (
            initial_node.review_level if initial_node else Review.ReviewLevel.TEACHER
        )
        template = None
        if initial_node and initial_node.review_template_id:
            template = initial_node.review_template_id
        phase_instance = ProjectPhaseService.ensure_current(
            project, ProjectPhaseInstance.Phase.APPLICATION, step=step
        )
        project.status = Project.ProjectStatus.TEACHER_AUDITING
        project.save(update_fields=["status"])

        return ReviewService.create_review(
            project=project,
            review_type=Review.ReviewType.APPLICATION,
            review_level=review_level or Review.ReviewLevel.TEACHER,
            phase_instance=phase_instance,
            review_template_id=template if template else None,
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

        node = WorkflowService.find_expert_node(
            ProjectPhaseInstance.Phase.APPLICATION,
            Review.ReviewLevel.LEVEL2,
            "COLLEGE",
            project.batch,
        )
        step = node.code if node else "COLLEGE_EXPERT"
        phase_instance = ProjectPhaseService.ensure_current(
            project, ProjectPhaseInstance.Phase.APPLICATION, step=step
        )
        return ReviewService.create_review(
            project=project,
            review_type=Review.ReviewType.APPLICATION,
            review_level=Review.ReviewLevel.LEVEL2,
            phase_instance=phase_instance,
            review_template_id=node.review_template_id if node else None,
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

        node = WorkflowService.find_expert_node(
            ProjectPhaseInstance.Phase.APPLICATION,
            Review.ReviewLevel.LEVEL1,
            "SCHOOL",
            project.batch,
        )
        step = node.code if node else "SCHOOL_EXPERT"
        phase_instance = ProjectPhaseService.ensure_current(
            project, ProjectPhaseInstance.Phase.APPLICATION, step=step
        )
        project.status = Project.ProjectStatus.LEVEL1_AUDITING
        project.save(update_fields=["status"])
        return ReviewService.create_review(
            project=project,
            review_type=Review.ReviewType.APPLICATION,
            review_level=Review.ReviewLevel.LEVEL1,
            phase_instance=phase_instance,
            review_template_id=node.review_template_id if node else None,
        )

    @staticmethod
    @transaction.atomic
    def approve_review(
        review,
        reviewer,
        comments="",
        score=None,
        closure_rating=None,
        score_details=None,
    ):
        """
        审核通过
        """
        if reviewer.role == "EXPERT":
            total_score, normalized_details = ReviewService._normalize_score_details(
                review, score, score_details
            )
            review.status = Review.ReviewStatus.APPROVED
            review.reviewer = reviewer
            review.comments = comments
            review.score = total_score
            review.score_details = normalized_details
            review.reviewed_at = timezone.now()
            if review.review_type == Review.ReviewType.CLOSURE and closure_rating:
                review.closure_rating = closure_rating
            review.save()
            return True

        review.status = Review.ReviewStatus.APPROVED
        review.reviewer = reviewer
        review.comments = comments
        total_score, normalized_details = ReviewService._normalize_score_details(
            review, score, score_details
        )
        review.score = total_score
        review.score_details = normalized_details
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
                node = WorkflowService.find_expert_node(
                    ProjectPhaseInstance.Phase.MID_TERM,
                    Review.ReviewLevel.LEVEL2,
                    "COLLEGE",
                    project.batch,
                )
                step = node.code if node else "COLLEGE_EXPERT"
                phase_instance = ProjectPhaseService.ensure_current(
                    project, ProjectPhaseInstance.Phase.MID_TERM, step=step
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
                node = WorkflowService.find_expert_node(
                    ProjectPhaseInstance.Phase.CLOSURE,
                    Review.ReviewLevel.LEVEL2,
                    "COLLEGE",
                    project.batch,
                )
                step = node.code if node else "COLLEGE_EXPERT"
                phase_instance = ProjectPhaseService.ensure_current(
                    project, ProjectPhaseInstance.Phase.CLOSURE, step=step
                )
                review.phase_instance = phase_instance
                review.save(update_fields=["phase_instance"])
            elif review.review_level == Review.ReviewLevel.LEVEL2:
                # 二级管理员确认后进入校级专家评审（legacy admin-review 路径）
                project.status = Project.ProjectStatus.CLOSURE_LEVEL1_REVIEWING
                node = WorkflowService.find_expert_node(
                    ProjectPhaseInstance.Phase.CLOSURE,
                    Review.ReviewLevel.LEVEL1,
                    "SCHOOL",
                    project.batch,
                )
                step = node.code if node else "SCHOOL_EXPERT"
                phase_instance = ProjectPhaseService.ensure_current(
                    project, ProjectPhaseInstance.Phase.CLOSURE, step=step
                )
                review.phase_instance = phase_instance
                review.save(update_fields=["phase_instance"])
            elif review.review_level == Review.ReviewLevel.LEVEL1:
                project.status = Project.ProjectStatus.CLOSURE_LEVEL1_APPROVED
                # 一级审核通过后，项目结题
                project.status = Project.ProjectStatus.CLOSED
                ensure_project_archive(project)
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

        process_rules = SystemSettingService.get_setting(
            "PROCESS_RULES", batch=project.batch
        )
        reject_to_previous = bool(process_rules.get("reject_to_previous", False))

        # 申报审核
        if review.review_type == Review.ReviewType.APPLICATION:
            if review.review_level == Review.ReviewLevel.TEACHER:
                project.status = Project.ProjectStatus.TEACHER_REJECTED
            elif review.review_level == Review.ReviewLevel.LEVEL2:
                if reject_to_previous:
                    existing = Review.objects.filter(
                        project=project,
                        review_type=Review.ReviewType.APPLICATION,
                        review_level=Review.ReviewLevel.TEACHER,
                        status=Review.ReviewStatus.PENDING,
                    ).exists()
                    if not existing:
                        ReviewService.create_teacher_review(project)
                    project.status = Project.ProjectStatus.TEACHER_AUDITING
                else:
                    project.status = Project.ProjectStatus.APPLICATION_RETURNED
                    if review.phase_instance:
                        ProjectPhaseService.mark_returned(
                            review.phase_instance,
                            return_to=ProjectPhaseInstance.ReturnTo.STUDENT,
                            reason=comments,
                        )
            elif review.review_level == Review.ReviewLevel.LEVEL1:
                if reject_to_previous:
                    existing = Review.objects.filter(
                        project=project,
                        review_type=Review.ReviewType.APPLICATION,
                        review_level=Review.ReviewLevel.LEVEL2,
                        status=Review.ReviewStatus.PENDING,
                    ).exists()
                    if not existing:
                        ReviewService.create_level2_review(project)
                    project.status = Project.ProjectStatus.COLLEGE_AUDITING
                else:
                    project.status = Project.ProjectStatus.APPLICATION_RETURNED
                    if review.phase_instance:
                        ProjectPhaseService.mark_returned(
                            review.phase_instance,
                            return_to=ProjectPhaseInstance.ReturnTo.STUDENT,
                            reason=comments,
                        )

        # 中期审核
        elif review.review_type == Review.ReviewType.MID_TERM:
            if review.review_level == Review.ReviewLevel.LEVEL2 and reject_to_previous:
                existing = Review.objects.filter(
                    project=project,
                    review_type=Review.ReviewType.MID_TERM,
                    review_level=Review.ReviewLevel.TEACHER,
                    status=Review.ReviewStatus.PENDING,
                ).exists()
                if not existing:
                    ReviewService.create_mid_term_teacher_review(project)
                project.status = Project.ProjectStatus.MID_TERM_SUBMITTED
            else:
                project.status = Project.ProjectStatus.MID_TERM_REJECTED

        # 结题审核
        elif review.review_type == Review.ReviewType.CLOSURE:
            if review.review_level == Review.ReviewLevel.TEACHER:
                project.status = Project.ProjectStatus.CLOSURE_DRAFT
            elif review.review_level == Review.ReviewLevel.LEVEL2:
                if reject_to_previous:
                    existing = Review.objects.filter(
                        project=project,
                        review_type=Review.ReviewType.CLOSURE,
                        review_level=Review.ReviewLevel.TEACHER,
                        status=Review.ReviewStatus.PENDING,
                    ).exists()
                    if not existing:
                        ReviewService.create_closure_teacher_review(project)
                    project.status = Project.ProjectStatus.CLOSURE_SUBMITTED
                else:
                    project.status = Project.ProjectStatus.CLOSURE_LEVEL2_REJECTED
            elif review.review_level == Review.ReviewLevel.LEVEL1:
                if reject_to == "teacher":
                    project.status = Project.ProjectStatus.CLOSURE_SUBMITTED
                    ReviewService.create_closure_teacher_review(project)
                elif reject_to == "student":
                    project.status = Project.ProjectStatus.CLOSURE_DRAFT
                elif reject_to_previous:
                    existing = Review.objects.filter(
                        project=project,
                        review_type=Review.ReviewType.CLOSURE,
                        review_level=Review.ReviewLevel.LEVEL2,
                        status=Review.ReviewStatus.PENDING,
                    ).exists()
                    if not existing:
                        ReviewService.create_closure_level2_review(project)
                    project.status = Project.ProjectStatus.CLOSURE_LEVEL2_REVIEWING
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
        node = WorkflowService.find_expert_node(
            ProjectPhaseInstance.Phase.CLOSURE,
            Review.ReviewLevel.LEVEL2,
            "COLLEGE",
            project.batch,
        )
        step = node.code if node else "COLLEGE_EXPERT"
        phase_instance = ProjectPhaseService.ensure_current(
            project, ProjectPhaseInstance.Phase.CLOSURE, step=step
        )
        return ReviewService.create_review(
            project=project,
            review_type=Review.ReviewType.CLOSURE,
            review_level=Review.ReviewLevel.LEVEL2,
            phase_instance=phase_instance,
            review_template_id=node.review_template_id if node else None,
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

        node = WorkflowService.find_expert_node(
            ProjectPhaseInstance.Phase.CLOSURE,
            Review.ReviewLevel.LEVEL1,
            "SCHOOL",
            project.batch,
        )
        step = node.code if node else "SCHOOL_EXPERT"
        phase_instance = ProjectPhaseService.ensure_current(
            project, ProjectPhaseInstance.Phase.CLOSURE, step=step
        )
        # 更新项目状态
        project.status = Project.ProjectStatus.CLOSURE_LEVEL1_REVIEWING
        project.save(update_fields=["status"])

        return ReviewService.create_review(
            project=project,
            review_type=Review.ReviewType.CLOSURE,
            review_level=Review.ReviewLevel.LEVEL1,
            phase_instance=phase_instance,
            review_template_id=node.review_template_id if node else None,
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

        node = WorkflowService.find_expert_node(
            ProjectPhaseInstance.Phase.MID_TERM,
            Review.ReviewLevel.LEVEL2,
            "COLLEGE",
            project.batch,
        )
        step = node.code if node else "COLLEGE_EXPERT"
        phase_instance = ProjectPhaseService.ensure_current(
            project, ProjectPhaseInstance.Phase.MID_TERM, step=step
        )
        return phase_instance

    @staticmethod
    @transaction.atomic
    def create_mid_term_teacher_review(project):
        """
        创建中期审核记录（导师审核）
        """
        initial_node = WorkflowService.get_initial_node(
            ProjectPhaseInstance.Phase.MID_TERM, project.batch
        )
        step = initial_node.code if initial_node else "TEACHER_REVIEW"
        phase_instance = ProjectPhaseService.ensure_current(
            project, ProjectPhaseInstance.Phase.MID_TERM, step=step
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
            review_template_id=initial_node.review_template_id if initial_node else None,
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

        initial_node = WorkflowService.get_initial_node(
            ProjectPhaseInstance.Phase.CLOSURE, project.batch
        )
        step = initial_node.code if initial_node else "TEACHER_REVIEW"
        phase_instance = ProjectPhaseService.ensure_current(
            project, ProjectPhaseInstance.Phase.CLOSURE, step=step
        )
        return ReviewService.create_review(
            project=project,
            review_type=Review.ReviewType.CLOSURE,
            review_level=Review.ReviewLevel.TEACHER,
            phase_instance=phase_instance,
            review_template_id=initial_node.review_template_id if initial_node else None,
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

                scope = "SCHOOL" if review_level == Review.ReviewLevel.LEVEL1 else "COLLEGE"
                node = WorkflowService.find_expert_node(
                    review_type, review_level, scope, project.batch
                )
                step = node.code if node else "COLLEGE_EXPERT"

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
                            review_template_id=node.review_template_id if node else None,
                            status=Review.ReviewStatus.PENDING
                        )
                        created_reviews.append(review)
                        NotificationService.notify_review_assigned(review)
                        
        return created_reviews
