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
    def _get_phase_from_review_type(review_type):
        """获取评审类型对应的阶段"""
        mapping = {
            Review.ReviewType.APPLICATION: ProjectPhaseInstance.Phase.APPLICATION,
            Review.ReviewType.MID_TERM: ProjectPhaseInstance.Phase.MID_TERM,
            Review.ReviewType.CLOSURE: ProjectPhaseInstance.Phase.CLOSURE,
        }
        return mapping.get(review_type)

    @staticmethod
    def _move_to_next_node(project, phase_instance, current_node_id):
        """
        移动到下一个工作流节点
        返回: (next_node, status_updated) - 下一节点定义和是否更新了状态
        """
        next_node = WorkflowService.get_next_node_by_id(current_node_id)

        if next_node:
            # 更新 phase_instance 的当前节点
            phase_instance.current_node_id = next_node.id
            phase_instance.step = next_node.code
            phase_instance.save(update_fields=["current_node_id", "step"])

            # 根据节点类型更新项目状态
            ReviewService._update_project_status_for_node(
                project, next_node, phase_instance.phase
            )
            return next_node, True
        else:
            # 已到达流程末尾，标记阶段完成
            phase = phase_instance.phase
            if phase == ProjectPhaseInstance.Phase.APPLICATION:
                project.status = Project.ProjectStatus.IN_PROGRESS
                ProjectPhaseService.mark_completed(phase_instance, step="PUBLISHED")
            elif phase == ProjectPhaseInstance.Phase.MID_TERM:
                project.status = Project.ProjectStatus.READY_FOR_CLOSURE
                ProjectPhaseService.mark_completed(phase_instance, step="COMPLETED")
            elif phase == ProjectPhaseInstance.Phase.CLOSURE:
                project.status = Project.ProjectStatus.CLOSED
                ensure_project_archive(project)
                ProjectPhaseService.mark_completed(phase_instance, step="COMPLETED")

            project.save(update_fields=["status"])
            return None, True

    @staticmethod
    def _move_to_target_node(project, phase_instance, target_node_id):
        """
        退回到指定的目标节点
        """
        target_node_obj = WorkflowService.get_node_by_id(target_node_id)
        if not target_node_obj:
            ReviewService.logger.error(f"Target node {target_node_id} not found")
            return False

        # 构造 WorkflowNodeDef（从数据库对象）
        from apps.system_settings.services.workflow_service import WorkflowNodeDef

        target_node = WorkflowNodeDef(
            id=target_node_obj.id,
            code=target_node_obj.code,
            name=target_node_obj.name,
            node_type=target_node_obj.node_type,
            role=target_node_obj.get_role_code() or target_node_obj.role,
            review_level=target_node_obj.review_level,
            scope=target_node_obj.scope,
            return_policy=target_node_obj.return_policy,
            allowed_reject_to=target_node_obj.allowed_reject_to or [],
            review_template_id=target_node_obj.review_template_id,
            role_fk_id=target_node_obj.role_fk_id,
        )

        # 更新 phase_instance
        phase_instance.current_node_id = target_node.id
        phase_instance.step = target_node.code
        phase_instance.save(update_fields=["current_node_id", "step"])

        # 如果退回到学生节点，标记为已退回
        if target_node.node_type == "SUBMIT":
            phase = phase_instance.phase
            if phase == ProjectPhaseInstance.Phase.APPLICATION:
                project.status = Project.ProjectStatus.APPLICATION_RETURNED
            elif phase == ProjectPhaseInstance.Phase.MID_TERM:
                project.status = Project.ProjectStatus.MID_TERM_REJECTED
            elif phase == ProjectPhaseInstance.Phase.CLOSURE:
                project.status = Project.ProjectStatus.CLOSURE_DRAFT

            ProjectPhaseService.mark_returned(
                phase_instance,
                return_to=ProjectPhaseInstance.ReturnTo.STUDENT,
                reason="审核退回",
            )
        else:
            # 退回到其他审核节点，更新项目状态
            ReviewService._update_project_status_for_node(
                project, target_node, phase_instance.phase
            )

        project.save(update_fields=["status"])
        return True

    @staticmethod
    def _update_project_status_for_node(project, node, phase):
        """
        根据节点类型和阶段更新项目状态
        """
        # 学生节点
        if node.node_type == "SUBMIT":
            if phase == ProjectPhaseInstance.Phase.APPLICATION:
                project.status = Project.ProjectStatus.DRAFT
            elif phase == ProjectPhaseInstance.Phase.MID_TERM:
                project.status = Project.ProjectStatus.IN_PROGRESS
            elif phase == ProjectPhaseInstance.Phase.CLOSURE:
                project.status = Project.ProjectStatus.READY_FOR_CLOSURE
            return

        # 审核节点 - 根据角色和阶段推断状态
        role_code = node.role

        if phase == ProjectPhaseInstance.Phase.APPLICATION:
            if role_code == "TEACHER":
                project.status = Project.ProjectStatus.TEACHER_AUDITING
            elif role_code == "LEVEL2_ADMIN" or node.scope == "COLLEGE":
                project.status = Project.ProjectStatus.COLLEGE_AUDITING
            elif role_code == "LEVEL1_ADMIN" or node.scope == "SCHOOL":
                project.status = Project.ProjectStatus.LEVEL1_AUDITING
        elif phase == ProjectPhaseInstance.Phase.MID_TERM:
            if role_code == "TEACHER":
                project.status = Project.ProjectStatus.MID_TERM_SUBMITTED
            else:
                project.status = Project.ProjectStatus.MID_TERM_REVIEWING
        elif phase == ProjectPhaseInstance.Phase.CLOSURE:
            if role_code == "TEACHER":
                project.status = Project.ProjectStatus.CLOSURE_SUBMITTED
            elif node.scope == "COLLEGE":
                project.status = Project.ProjectStatus.CLOSURE_LEVEL2_REVIEWING
            elif node.scope == "SCHOOL":
                project.status = Project.ProjectStatus.CLOSURE_LEVEL1_REVIEWING

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
        审核通过 - 使用动态工作流引擎
        """
        # 处理评分
        total_score, normalized_details = ReviewService._normalize_score_details(
            review, score, score_details
        )

        # 更新审核记录
        review.status = Review.ReviewStatus.APPROVED
        review.reviewer = reviewer
        review.comments = comments
        review.score = total_score
        review.score_details = normalized_details
        review.reviewed_at = timezone.now()

        if review.review_type == Review.ReviewType.CLOSURE and closure_rating:
            review.closure_rating = closure_rating

        review.save()

        # 专家评审只更新记录，不流转状态
        if reviewer.role == "EXPERT":
            return True

        # 使用动态流程引擎流转到下一节点
        project = review.project
        phase_instance = review.phase_instance

        if not phase_instance:
            # 向后兼容：如果没有 phase_instance，使用旧逻辑
            ReviewService.logger.warning(
                f"Review {review.id} has no phase_instance, using legacy approval logic"
            )
            return ReviewService._legacy_approve_review(review, project)

        current_node_id = phase_instance.current_node_id
        if not current_node_id:
            # 向后兼容：如果没有 current_node_id，根据 review_type 推断
            ReviewService.logger.warning(
                f"Phase instance {phase_instance.id} has no current_node_id, inferring from review"
            )
            return ReviewService._legacy_approve_review(review, project)

        # 移动到下一个节点
        next_node, status_updated = ReviewService._move_to_next_node(
            project, phase_instance, current_node_id
        )

        ReviewService.logger.info(
            f"Project {project.project_no} approved at node {current_node_id}, "
            f"moved to {'node ' + str(next_node.id) if next_node else 'completion'}"
        )

        return True

    @staticmethod
    @transaction.atomic
    def _legacy_approve_review(review, project):
        """
        旧的审核通过逻辑（向后兼容）
        """
        # 申报审核
        if review.review_type == Review.ReviewType.APPLICATION:
            if review.review_level == Review.ReviewLevel.TEACHER:
                project.status = Project.ProjectStatus.TEACHER_APPROVED
                ReviewService.create_level2_review(project)
            elif review.review_level == Review.ReviewLevel.LEVEL2:
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
                    ProjectPhaseService.mark_completed(
                        review.phase_instance, step="PUBLISHED"
                    )

        # 中期审核
        elif review.review_type == Review.ReviewType.MID_TERM:
            if review.review_level == Review.ReviewLevel.TEACHER:
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
                    ProjectPhaseService.mark_completed(
                        review.phase_instance, step="COMPLETED"
                    )

        # 结题审核
        elif review.review_type == Review.ReviewType.CLOSURE:
            if review.review_level == Review.ReviewLevel.TEACHER:
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
                project.status = Project.ProjectStatus.CLOSED
                ensure_project_archive(project)
                if review.phase_instance:
                    ProjectPhaseService.mark_completed(
                        review.phase_instance, step="COMPLETED"
                    )

        project.save()
        return True

    @staticmethod
    @transaction.atomic
    def reject_review(
        review, reviewer, comments="", reject_to=None, target_node_id=None
    ):
        """
        审核不通过 - 使用动态工作流引擎

        参数:
            review: 审核记录
            reviewer: 审核人
            comments: 审核意见
            reject_to: 旧参数，向后兼容 ("teacher", "student", None)
            target_node_id: 新参数，退回到指定节点ID
        """
        # 更新审核记录
        review.status = Review.ReviewStatus.REJECTED
        review.reviewer = reviewer
        review.comments = comments
        review.reviewed_at = timezone.now()
        review.save()

        # 专家评审只更新记录，不流转状态
        if reviewer.role == "EXPERT":
            return True

        project = review.project
        phase_instance = review.phase_instance

        # 使用动态流程引擎处理退回
        if phase_instance and phase_instance.current_node_id:
            current_node_id = phase_instance.current_node_id

            # 如果指定了 target_node_id，退回到指定节点
            if target_node_id:
                success = ReviewService._move_to_target_node(
                    project, phase_instance, target_node_id
                )
                if success:
                    ReviewService.logger.info(
                        f"Project {project.project_no} rejected from node {current_node_id}, "
                        f"returned to node {target_node_id}"
                    )
                    return True
                else:
                    ReviewService.logger.error(
                        f"Failed to return project {project.project_no} to node {target_node_id}"
                    )

            # 如果没有指定 target_node_id，获取当前节点的可退回节点列表
            reject_targets = WorkflowService.get_reject_target_nodes(current_node_id)

            if reject_targets and len(reject_targets) > 0:
                # 默认退回到第一个可退回节点（通常是学生节点）
                default_target = reject_targets[0]
                success = ReviewService._move_to_target_node(
                    project, phase_instance, default_target.id
                )
                if success:
                    ReviewService.logger.info(
                        f"Project {project.project_no} rejected from node {current_node_id}, "
                        f"auto-returned to node {default_target.id} ({default_target.name})"
                    )
                    return True
            else:
                # 没有配置退回规则，退回到学生节点
                ReviewService.logger.warning(
                    f"Node {current_node_id} has no reject targets configured, "
                    f"using legacy reject logic"
                )

        # 向后兼容：使用旧的退回逻辑
        return ReviewService._legacy_reject_review(review, project, reject_to)

    @staticmethod
    @transaction.atomic
    def _legacy_reject_review(review, project, reject_to=None):
        """
        旧的审核拒绝逻辑（向后兼容）
        """
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
                            reason=review.comments,
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
                            reason=review.comments,
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
            review_template_id=initial_node.review_template_id
            if initial_node
            else None,
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
            review_template_id=initial_node.review_template_id
            if initial_node
            else None,
        )

    @staticmethod
    def get_pending_reviews_for_admin(admin_user):
        """
        获取管理员的待审核列表
        """
        # 排除已结题、已完成、已终止的项目
        excluded_statuses = [
            Project.ProjectStatus.CLOSED,
            Project.ProjectStatus.COMPLETED,
            Project.ProjectStatus.TERMINATED,
        ]

        if admin_user.is_level2_admin:
            return Review.objects.filter(
                project__leader__college=admin_user.college,
                review_level=Review.ReviewLevel.LEVEL2,
                status=Review.ReviewStatus.PENDING,
                reviewer__isnull=True,
            ).exclude(project__status__in=excluded_statuses)
        elif admin_user.is_level1_admin:
            return Review.objects.filter(
                review_level=Review.ReviewLevel.LEVEL1,
                status=Review.ReviewStatus.PENDING,
                reviewer__isnull=True,
            ).exclude(project__status__in=excluded_statuses)
        return Review.objects.none()

    @staticmethod
    def assign_project_to_group(
        project_ids,
        group_id,
        review_type=Review.ReviewType.APPLICATION,
        review_level=Review.ReviewLevel.LEVEL2,
        creator=None,
    ):
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

                scope = (
                    "SCHOOL" if review_level == Review.ReviewLevel.LEVEL1 else "COLLEGE"
                )
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
                            review_template_id=node.review_template_id
                            if node
                            else None,
                            status=Review.ReviewStatus.PENDING,
                        )
                        created_reviews.append(review)
                        NotificationService.notify_review_assigned(review)

        return created_reviews
