"""
审核业务逻辑层
"""

from django.utils import timezone
import logging
from django.db import transaction
from django.db.models import Q
from ..models import (
    Review,
    ExpertGroup,
)
from apps.projects.models import Project
from apps.projects.models import ProjectPhaseInstance
from apps.projects.services.phase_service import ProjectPhaseService
from apps.projects.services.archive_service import ensure_project_archive
from apps.system_settings.services import SystemSettingService, WorkflowService
from apps.system_settings.services import AdminAssignmentService
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

            # 如果是审核节点，自动创建 Review 记录
            if next_node.node_type in ["REVIEW", "APPROVAL"]:
                ReviewService._create_review_for_node(
                    project, phase_instance, next_node
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
    def _move_to_target_node(project, phase_instance, target_node_id, reason=""):
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
            require_expert_review=target_node_obj.require_expert_review,
            return_policy=target_node_obj.return_policy,
            allowed_reject_to=target_node_obj.allowed_reject_to,
            role_fk_id=target_node_obj.role_fk_id,
        )

        nodes = WorkflowService.get_nodes(phase_instance.phase, project.batch)
        node_order = {node.id: idx for idx, node in enumerate(nodes)}
        target_index = node_order.get(target_node.id)
        if target_index is not None:
            later_node_ids = [
                node.id for idx, node in enumerate(nodes) if idx > target_index
            ]
            if later_node_ids:
                Review.objects.filter(
                    project=project,
                    phase_instance=phase_instance,
                    workflow_node_id__in=later_node_ids,
                ).delete()

        Review.objects.filter(
            project=project,
            phase_instance=phase_instance,
            workflow_node_id=target_node.id,
            status=Review.ReviewStatus.PENDING,
        ).update(
            status=Review.ReviewStatus.REJECTED,
            comments="退回重新开始",
            reviewed_at=timezone.now(),
        )

        return_to = (
            ProjectPhaseInstance.ReturnTo.STUDENT
            if target_node.node_type == "SUBMIT"
            else ProjectPhaseInstance.ReturnTo.TEACHER
        )
        ProjectPhaseService.mark_returned(
            phase_instance,
            return_to=return_to,
            reason=reason or "审核退回",
        )
        new_instance = ProjectPhaseService.start_new_attempt(
            project,
            phase_instance.phase,
            step=target_node.code,
        )
        if target_node.node_type != "SUBMIT":
            ReviewService._create_review_for_node(project, new_instance, target_node)

        if target_node.node_type == "SUBMIT":
            phase = phase_instance.phase
            if phase == ProjectPhaseInstance.Phase.APPLICATION:
                project.status = Project.ProjectStatus.APPLICATION_RETURNED
            elif phase == ProjectPhaseInstance.Phase.MID_TERM:
                project.status = Project.ProjectStatus.MID_TERM_RETURNED
            elif phase == ProjectPhaseInstance.Phase.CLOSURE:
                project.status = Project.ProjectStatus.CLOSURE_DRAFT
        else:
            ReviewService._update_project_status_for_node(
                project, target_node, phase_instance.phase
            )

        project.save(update_fields=["status", "updated_at"])
        return True

    @staticmethod
    def _create_review_for_node(project, phase_instance, node):
        """
        为审核节点自动创建 Review 记录 - 完全动态，不硬编码角色
        """
        from apps.reviews.models import Review

        # 确定 review_type
        review_type_map = {
            "APPLICATION": Review.ReviewType.APPLICATION,
            "MID_TERM": Review.ReviewType.MID_TERM,
            "CLOSURE": Review.ReviewType.CLOSURE,
        }
        review_type = review_type_map.get(phase_instance.phase)
        if not review_type:
            ReviewService.logger.warning(
                f"Unknown phase {phase_instance.phase} for project {project.id}"
            )
            return

        # 从节点直接读取 review_level，不再硬编码映射
        # 如果节点有 review_level，使用它
        # 否则使用节点的 role 作为 review_level
        review_level = node.review_level or node.role or "UNKNOWN"

        # 检查是否已存在该节点的待审核记录
        workflow_node_id = ReviewService._resolve_workflow_node_id(node)
        existing_qs = Review.objects.filter(
            project=project,
            review_type=review_type,
            review_level=review_level,
            status=Review.ReviewStatus.PENDING,
            phase_instance=phase_instance,
            is_expert_review=False,
        )
        if workflow_node_id:
            existing_qs = existing_qs.filter(workflow_node_id=workflow_node_id)
        existing = existing_qs.exists()

        if existing:
            ReviewService.logger.info(
                f"Review already exists for project {project.id} at node {node.id}"
            )
            return

        # 创建新的 Review 记录
        ReviewService.create_review(
            project=project,
            review_type=review_type,
            review_level=review_level,
            phase_instance=phase_instance,
            workflow_node=workflow_node_id,
            is_expert_review=False,
        )

        ReviewService.logger.info(
            f"Created review for project {project.id} at node {node.id} ({node.name}) with level {review_level}"
        )

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
            project.save(update_fields=["status", "updated_at"])
            return

        # 审核节点 - 根据节点配置动态设置状态
        # 不再硬编码角色到状态的映射

        # 优先使用节点配置的 project_status
        if hasattr(node, "project_status") and node.project_status:
            try:
                project.status = node.project_status
                project.save(update_fields=["status", "updated_at"])
                return
            except Exception as e:
                ReviewService.logger.warning(
                    f"Invalid project_status {node.project_status} in node {node.id}: {e}"
                )

        # 备用方案：根据阶段和节点属性推断（保持向后兼容）
        role_code = node.role or node.get_role_code()

        if phase == ProjectPhaseInstance.Phase.APPLICATION:
            if role_code == "TEACHER":
                project.status = Project.ProjectStatus.TEACHER_AUDITING
            elif role_code == "LEVEL2_ADMIN":
                project.status = Project.ProjectStatus.COLLEGE_AUDITING
            elif role_code == "LEVEL1_ADMIN":
                project.status = Project.ProjectStatus.LEVEL1_AUDITING
            else:
                # 其他角色：使用通用审核状态
                project.status = Project.ProjectStatus.TEACHER_AUDITING
        elif phase == ProjectPhaseInstance.Phase.MID_TERM:
            if role_code == "TEACHER":
                project.status = Project.ProjectStatus.MID_TERM_SUBMITTED
            else:
                project.status = Project.ProjectStatus.MID_TERM_REVIEWING
        elif phase == ProjectPhaseInstance.Phase.CLOSURE:
            if role_code == "TEACHER":
                project.status = Project.ProjectStatus.CLOSURE_SUBMITTED
            elif role_code == "LEVEL2_ADMIN":
                project.status = Project.ProjectStatus.CLOSURE_LEVEL2_REVIEWING
            elif role_code == "LEVEL1_ADMIN":
                project.status = Project.ProjectStatus.CLOSURE_LEVEL1_REVIEWING
            else:
                # 其他角色：使用通用审核状态
                project.status = Project.ProjectStatus.CLOSURE_SUBMITTED

        # 保存项目状态
        project.save(update_fields=["status", "updated_at"])

    @staticmethod
    def _normalize_score_details(review, score, score_details):
        """
        规范评分明细
        """
        if score_details is None:
            return score, []

        if not isinstance(score_details, list):
            raise ValueError("评分明细格式错误")

        total = 0
        normalized = []
        for item in score_details:
            if not isinstance(item, dict):
                raise ValueError("评分明细格式错误")
            title = item.get("title") or ""
            item_id = item.get("item_id")
            raw_score = item.get("score")
            if raw_score is None or raw_score == "":
                display_name = title or f"#{item_id}" if item_id else "评分项"
                raise ValueError(f"评分项“{display_name}”不能为空")
            try:
                raw_score = int(raw_score)
            except (TypeError, ValueError):
                display_name = title or f"#{item_id}" if item_id else "评分项"
                raise ValueError(f"评分项“{display_name}”分值格式错误")
            if raw_score < 0:
                display_name = title or f"#{item_id}" if item_id else "评分项"
                raise ValueError(f"评分项“{display_name}”超出范围")

            max_score = item.get("max_score")
            if max_score not in (None, ""):
                try:
                    max_score_int = int(max_score)
                except (TypeError, ValueError):
                    raise ValueError("评分明细最大分值格式错误")
                if raw_score > max_score_int:
                    display_name = title or f"#{item_id}" if item_id else "评分项"
                    raise ValueError(f"评分项“{display_name}”超出范围")
            else:
                max_score_int = None

            weight = item.get("weight")
            if weight in (None, ""):
                weight_value = 100.0
            else:
                try:
                    weight_value = float(weight)
                except (TypeError, ValueError):
                    raise ValueError("评分明细权重格式错误")

            weighted = int(round(raw_score * weight_value / 100))
            total += weighted
            normalized.append(
                {
                    "item_id": item_id,
                    "title": title,
                    "score": raw_score,
                    "weight": weight_value,
                    "weighted_score": weighted,
                    "max_score": max_score_int,
                }
            )

        final_score = total if score is None else score
        return final_score, normalized

    @staticmethod
    def _ensure_expert_reviews_completed(review):
        if review.is_expert_review:
            return

        node = review.workflow_node
        expert_required = False
        if node:
            expert_required = node.require_expert_review

        if review.workflow_node_id:
            expert_qs = Review.objects.filter(
                project=review.project,
                phase_instance=review.phase_instance,
                workflow_node_id=review.workflow_node_id,
                is_expert_review=True,
            )
        else:
            expert_qs = Review.objects.filter(
                project=review.project,
                phase_instance=review.phase_instance,
                review_type=review.review_type,
                review_level=review.review_level,
                is_expert_review=True,
            )

        if node and not expert_required:
            return

        if expert_qs.exists():
            if expert_qs.filter(status=Review.ReviewStatus.PENDING).exists():
                raise ValueError("专家评审尚未全部提交")
            return

        if expert_required:
            raise ValueError("请先分配专家评审")

    @staticmethod
    def _find_teacher_node(phase, batch):
        nodes = WorkflowService.get_nodes(phase, batch)
        for node in nodes:
            if node.node_type != "SUBMIT" and node.role == "TEACHER":
                return node
        for node in nodes:
            if node.node_type != "SUBMIT":
                return node
        return nodes[0] if nodes else None

    @staticmethod
    def _resolve_workflow_node_id(node):
        if not node:
            return None
        node_id = node.id if hasattr(node, "id") else node
        return node_id if WorkflowService.get_node_by_id(node_id) else None

    @staticmethod
    @transaction.atomic
    def create_review(
        project,
        review_type,
        review_level,
        *,
        phase_instance: ProjectPhaseInstance | None = None,
        workflow_node=None,
        is_expert_review: bool = False,
        reviewer=None,
    ):
        """
        创建审核记录
        """
        payload = {
            "project": project,
            "phase_instance": phase_instance,
            "review_type": review_type,
            "review_level": review_level,
            "status": Review.ReviewStatus.PENDING,
            "is_expert_review": is_expert_review,
            "reviewer": reviewer,
        }
        if workflow_node is not None:
            if isinstance(workflow_node, int):
                if WorkflowService.get_node_by_id(workflow_node):
                    payload["workflow_node_id"] = workflow_node
            else:
                payload["workflow_node"] = workflow_node
        return Review.objects.create(**payload)

    @staticmethod
    @transaction.atomic
    def create_teacher_review(project):
        """
        创建导师审核记录（申报审核）
        """
        teacher_node = ReviewService._find_teacher_node(
            ProjectPhaseInstance.Phase.APPLICATION, project.batch
        )
        step = teacher_node.code if teacher_node else "TEACHER_REVIEW"
        review_level = teacher_node.review_level if teacher_node else "TEACHER"
        phase_instance = ProjectPhaseService.ensure_current(
            project, ProjectPhaseInstance.Phase.APPLICATION, step=step
        )
        project.status = Project.ProjectStatus.TEACHER_AUDITING
        project.save(update_fields=["status"])

        return ReviewService.create_review(
            project=project,
            review_type=Review.ReviewType.APPLICATION,
            review_level=review_level or "TEACHER",
            phase_instance=phase_instance,
            workflow_node=teacher_node.id if teacher_node else None,
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
            "LEVEL2",
            project.batch,
        )
        step = node.code if node else "COLLEGE_REVIEW"
        phase_instance = ProjectPhaseService.ensure_current(
            project, ProjectPhaseInstance.Phase.APPLICATION, step=step
        )
        return ReviewService.create_review(
            project=project,
            review_type=Review.ReviewType.APPLICATION,
            review_level="LEVEL2",
            phase_instance=phase_instance,
            workflow_node=node.id if node else None,
        )

    @staticmethod
    @transaction.atomic
    def create_level1_review(project):
        """
        创建一级审核记录
        """
        node = WorkflowService.find_expert_node(
            ProjectPhaseInstance.Phase.APPLICATION,
            "LEVEL1",
            project.batch,
        )
        existing_qs = Review.objects.filter(
            project=project,
            review_type=Review.ReviewType.APPLICATION,
            review_level="LEVEL1",
            status=Review.ReviewStatus.PENDING,
        )
        workflow_node_id = ReviewService._resolve_workflow_node_id(node)
        if workflow_node_id:
            existing_qs = existing_qs.filter(workflow_node_id=workflow_node_id)
        existing = existing_qs.first()
        if existing:
            project.status = Project.ProjectStatus.LEVEL1_AUDITING
            project.save(update_fields=["status"])
            return existing

        step = node.code if node else "SCHOOL_PUBLISH"
        phase_instance = ProjectPhaseService.ensure_current(
            project, ProjectPhaseInstance.Phase.APPLICATION, step=step
        )
        project.status = Project.ProjectStatus.LEVEL1_AUDITING
        project.save(update_fields=["status"])
        return ReviewService.create_review(
            project=project,
            review_type=Review.ReviewType.APPLICATION,
            review_level="LEVEL1",
            phase_instance=phase_instance,
            workflow_node=workflow_node_id,
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
        ReviewService._ensure_expert_reviews_completed(review)

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
        if review.is_expert_review:
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

        if (
            review.workflow_node_id
            and review.workflow_node_id != phase_instance.current_node_id
        ):
            node_obj = WorkflowService.get_node_by_id(review.workflow_node_id)
            update_fields = ["current_node_id"]
            phase_instance.current_node_id = review.workflow_node_id
            if node_obj:
                phase_instance.step = node_obj.code
                update_fields.append("step")
            update_fields.append("updated_at")
            phase_instance.save(update_fields=update_fields)

        current_node_id = phase_instance.current_node_id or review.workflow_node_id
        if not current_node_id:
            inferred_node = WorkflowService.get_node_by_code(
                phase_instance.phase, phase_instance.step, project.batch
            )
            if inferred_node:
                phase_instance.current_node_id = inferred_node.id
                phase_instance.save(update_fields=["current_node_id", "updated_at"])
                current_node_id = inferred_node.id
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
            if review.review_level == "TEACHER":
                project.status = Project.ProjectStatus.TEACHER_APPROVED
                ReviewService.create_level2_review(project)
            elif review.review_level == "LEVEL2":
                if not Review.objects.filter(
                    project=project,
                    review_type=Review.ReviewType.APPLICATION,
                    review_level="LEVEL1",
                    status=Review.ReviewStatus.PENDING,
                ).exists():
                    ReviewService.create_level1_review(project)
                else:
                    project.status = Project.ProjectStatus.LEVEL1_AUDITING
                    project.save(update_fields=["status"])
            elif review.review_level == "LEVEL1":
                project.status = Project.ProjectStatus.IN_PROGRESS
                if review.phase_instance:
                    ProjectPhaseService.mark_completed(
                        review.phase_instance, step="PUBLISHED"
                    )

        # 中期审核
        elif review.review_type == Review.ReviewType.MID_TERM:
            if review.review_level == "TEACHER":
                project.status = Project.ProjectStatus.MID_TERM_REVIEWING
                project.save(update_fields=["status"])
                node = WorkflowService.find_expert_node(
                    ProjectPhaseInstance.Phase.MID_TERM,
                    "LEVEL2",
                    "COLLEGE",
                    project.batch,
                )
                step = node.code if node else "COLLEGE_FINALIZE"
                phase_instance = ProjectPhaseService.ensure_current(
                    project, ProjectPhaseInstance.Phase.MID_TERM, step=step
                )
                review.phase_instance = phase_instance
                review.save(update_fields=["phase_instance"])
            elif review.review_level == "LEVEL2":
                project.status = Project.ProjectStatus.READY_FOR_CLOSURE
                if review.phase_instance:
                    ProjectPhaseService.mark_completed(
                        review.phase_instance, step="COMPLETED"
                    )

        # 结题审核
        elif review.review_type == Review.ReviewType.CLOSURE:
            if review.review_level == "TEACHER":
                project.status = Project.ProjectStatus.CLOSURE_LEVEL2_REVIEWING
                project.save(update_fields=["status"])
                node = WorkflowService.find_expert_node(
                    ProjectPhaseInstance.Phase.CLOSURE,
                    "LEVEL2",
                    "COLLEGE",
                    project.batch,
                )
                step = node.code if node else "COLLEGE_REVIEW"
                phase_instance = ProjectPhaseService.ensure_current(
                    project, ProjectPhaseInstance.Phase.CLOSURE, step=step
                )
                review.phase_instance = phase_instance
                review.save(update_fields=["phase_instance"])
            elif review.review_level == "LEVEL2":
                project.status = Project.ProjectStatus.CLOSURE_LEVEL1_REVIEWING
                node = WorkflowService.find_expert_node(
                    ProjectPhaseInstance.Phase.CLOSURE,
                    "LEVEL1",
                    "SCHOOL",
                    project.batch,
                )
                step = node.code if node else "SCHOOL_FINALIZE"
                phase_instance = ProjectPhaseService.ensure_current(
                    project, ProjectPhaseInstance.Phase.CLOSURE, step=step
                )
                review.phase_instance = phase_instance
                review.save(update_fields=["phase_instance"])
            elif review.review_level == "LEVEL1":
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
        ReviewService._ensure_expert_reviews_completed(review)

        # 更新审核记录
        review.status = Review.ReviewStatus.REJECTED
        review.reviewer = reviewer
        review.comments = comments
        review.reviewed_at = timezone.now()
        review.save()

        # 专家评审不允许驳回
        if review.is_expert_review:
            raise ValueError("专家评审不能驳回项目")

        project = review.project
        phase_instance = review.phase_instance

        # 使用动态流程引擎处理退回
        if (
            phase_instance
            and review.workflow_node_id
            and review.workflow_node_id != phase_instance.current_node_id
        ):
            node_obj = WorkflowService.get_node_by_id(review.workflow_node_id)
            update_fields = ["current_node_id"]
            phase_instance.current_node_id = review.workflow_node_id
            if node_obj:
                phase_instance.step = node_obj.code
                update_fields.append("step")
            update_fields.append("updated_at")
            phase_instance.save(update_fields=update_fields)

        if phase_instance and not phase_instance.current_node_id:
            inferred_node = WorkflowService.get_node_by_code(
                phase_instance.phase, phase_instance.step, project.batch
            )
            if inferred_node:
                phase_instance.current_node_id = inferred_node.id
                phase_instance.save(update_fields=["current_node_id", "updated_at"])

        if phase_instance and phase_instance.current_node_id:
            current_node_id = phase_instance.current_node_id

            # 如果指定了 target_node_id，退回到指定节点
            if target_node_id:
                success = ReviewService._move_to_target_node(
                    project, phase_instance, target_node_id, comments
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
                    project, phase_instance, default_target.id, comments
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
            if review.review_level == "TEACHER":
                project.status = Project.ProjectStatus.TEACHER_REJECTED
            elif review.review_level == "LEVEL2":
                if reject_to_previous:
                    existing = Review.objects.filter(
                        project=project,
                        review_type=Review.ReviewType.APPLICATION,
                        review_level="TEACHER",
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
            elif review.review_level == "LEVEL1":
                if reject_to_previous:
                    existing = Review.objects.filter(
                        project=project,
                        review_type=Review.ReviewType.APPLICATION,
                        review_level="LEVEL2",
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
            if review.review_level == "LEVEL2" and reject_to_previous:
                existing = Review.objects.filter(
                    project=project,
                    review_type=Review.ReviewType.MID_TERM,
                    review_level="TEACHER",
                    status=Review.ReviewStatus.PENDING,
                ).exists()
                if not existing:
                    ReviewService.create_mid_term_teacher_review(project)
                project.status = Project.ProjectStatus.MID_TERM_SUBMITTED
            else:
                project.status = Project.ProjectStatus.MID_TERM_REJECTED

        # 结题审核
        elif review.review_type == Review.ReviewType.CLOSURE:
            if review.review_level == "TEACHER":
                project.status = Project.ProjectStatus.CLOSURE_DRAFT
            elif review.review_level == "LEVEL2":
                if reject_to_previous:
                    existing = Review.objects.filter(
                        project=project,
                        review_type=Review.ReviewType.CLOSURE,
                        review_level="TEACHER",
                        status=Review.ReviewStatus.PENDING,
                    ).exists()
                    if not existing:
                        ReviewService.create_closure_teacher_review(project)
                    project.status = Project.ProjectStatus.CLOSURE_SUBMITTED
                else:
                    project.status = Project.ProjectStatus.CLOSURE_LEVEL2_REJECTED
            elif review.review_level == "LEVEL1":
                if reject_to == "teacher":
                    project.status = Project.ProjectStatus.CLOSURE_SUBMITTED
                    ReviewService.create_closure_teacher_review(project)
                elif reject_to == "student":
                    project.status = Project.ProjectStatus.CLOSURE_DRAFT
                elif reject_to_previous:
                    existing = Review.objects.filter(
                        project=project,
                        review_type=Review.ReviewType.CLOSURE,
                        review_level="LEVEL2",
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
            "LEVEL2",
            "COLLEGE",
            project.batch,
        )
        step = node.code if node else "COLLEGE_REVIEW"
        phase_instance = ProjectPhaseService.ensure_current(
            project, ProjectPhaseInstance.Phase.CLOSURE, step=step
        )
        return ReviewService.create_review(
            project=project,
            review_type=Review.ReviewType.CLOSURE,
            review_level="LEVEL2",
            phase_instance=phase_instance,
            workflow_node=node.id if node else None,
        )

    @staticmethod
    @transaction.atomic
    def create_closure_level1_review(project):
        """
        创建结题一级审核记录
        """
        node = WorkflowService.find_expert_node(
            ProjectPhaseInstance.Phase.CLOSURE,
            "LEVEL1",
            "SCHOOL",
            project.batch,
        )
        existing_qs = Review.objects.filter(
            project=project,
            review_type=Review.ReviewType.CLOSURE,
            review_level="LEVEL1",
            status=Review.ReviewStatus.PENDING,
        )
        workflow_node_id = ReviewService._resolve_workflow_node_id(node)
        if workflow_node_id:
            existing_qs = existing_qs.filter(workflow_node_id=workflow_node_id)
        existing = existing_qs.first()
        if existing:
            project.status = Project.ProjectStatus.CLOSURE_LEVEL1_REVIEWING
            project.save(update_fields=["status"])
            return existing
        step = node.code if node else "SCHOOL_FINALIZE"
        phase_instance = ProjectPhaseService.ensure_current(
            project, ProjectPhaseInstance.Phase.CLOSURE, step=step
        )
        # 更新项目状态
        project.status = Project.ProjectStatus.CLOSURE_LEVEL1_REVIEWING
        project.save(update_fields=["status"])

        return ReviewService.create_review(
            project=project,
            review_type=Review.ReviewType.CLOSURE,
            review_level="LEVEL1",
            phase_instance=phase_instance,
            workflow_node=workflow_node_id,
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
            "LEVEL2",
            "COLLEGE",
            project.batch,
        )
        step = node.code if node else "COLLEGE_FINALIZE"
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
        teacher_node = ReviewService._find_teacher_node(
            ProjectPhaseInstance.Phase.MID_TERM, project.batch
        )
        step = teacher_node.code if teacher_node else "TEACHER_REVIEW"
        phase_instance = ProjectPhaseService.ensure_current(
            project, ProjectPhaseInstance.Phase.MID_TERM, step=step
        )
        existing_qs = Review.objects.filter(
            project=project,
            review_type=Review.ReviewType.MID_TERM,
            review_level="TEACHER",
            status=Review.ReviewStatus.PENDING,
        )
        workflow_node_id = ReviewService._resolve_workflow_node_id(teacher_node)
        if workflow_node_id:
            existing_qs = existing_qs.filter(workflow_node_id=workflow_node_id)
        existing = existing_qs.first()
        if existing:
            return existing

        return ReviewService.create_review(
            project=project,
            review_type=Review.ReviewType.MID_TERM,
            review_level="TEACHER",
            phase_instance=phase_instance,
            workflow_node=workflow_node_id,
        )

    @staticmethod
    @transaction.atomic
    def create_closure_teacher_review(project):
        """
        创建结题审核记录（导师审核）
        """
        teacher_node = ReviewService._find_teacher_node(
            ProjectPhaseInstance.Phase.CLOSURE, project.batch
        )
        existing_qs = Review.objects.filter(
            project=project,
            review_type=Review.ReviewType.CLOSURE,
            review_level="TEACHER",
            status=Review.ReviewStatus.PENDING,
        )
        workflow_node_id = ReviewService._resolve_workflow_node_id(teacher_node)
        if workflow_node_id:
            existing_qs = existing_qs.filter(workflow_node_id=workflow_node_id)
        existing = existing_qs.first()
        if existing:
            return existing
        step = teacher_node.code if teacher_node else "TEACHER_REVIEW"
        phase_instance = ProjectPhaseService.ensure_current(
            project, ProjectPhaseInstance.Phase.CLOSURE, step=step
        )
        return ReviewService.create_review(
            project=project,
            review_type=Review.ReviewType.CLOSURE,
            review_level="TEACHER",
            phase_instance=phase_instance,
            workflow_node=workflow_node_id,
        )

    @staticmethod
    def _build_admin_review_filter(admin_user):
        """
        根据管理员角色和工作流节点配置构建审核过滤条件
        不再依赖AdminAssignment表，直接通过工作流节点的角色匹配
        """
        from apps.system_settings.models import WorkflowNode

        # 获取管理员角色
        role_code = admin_user.get_role_code()
        if not role_code:
            return None

        # 查找所有该角色负责的工作流节点
        nodes = WorkflowNode.objects.filter(
            role=role_code, is_active=True
        ).select_related("workflow")

        if not nodes.exists():
            return None

        # 构建查询条件
        query = Q()
        for node in nodes:
            # 基础条件：匹配工作流节点
            cond = Q(workflow_node_id=node.id)

            # 如果是学院管理员，还要匹配学院
            if role_code == "LEVEL2_ADMIN" and admin_user.college:
                cond &= Q(project__leader__college=admin_user.college)

            # 如果管理员有其他管理范围限制，也可以在这里添加
            # 例如：managed_scope_value

            query |= cond

        return query

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

        base_qs = Review.objects.filter(
            status=Review.ReviewStatus.PENDING,
            reviewer__isnull=True,
            is_expert_review=False,
        ).exclude(project__status__in=excluded_statuses)

        query = ReviewService._build_admin_review_filter(admin_user)
        if not query:
            return Review.objects.none()
        return base_qs.filter(query)

    @staticmethod
    def assign_project_to_group(
        project_ids,
        group_id,
        review_type=Review.ReviewType.APPLICATION,
        review_level="LEVEL2",
        creator=None,
        target_node_id=None,
    ):
        """
        批量分配项目给专家组
        增加了学院限制检查和指导老师排除检查
        """
        group = ExpertGroup.objects.get(pk=group_id)
        experts = group.members.all()
        if experts.filter(is_expert=False).exists():
            raise ValueError("专家组包含未设置为专家的教师")

        # ===== 新增：学院限制检查 =====
        if creator and creator.role_fk and creator.role_fk.scope_dimension == "COLLEGE":
            # 学院级管理员，检查成员是否都是本学院
            creator_college_item = creator.managed_scope_value
            if not creator_college_item:
                raise ValueError("学院级管理员未配置管理范围")

            creator_college = creator_college_item.value
            for member in experts:
                if member.college != creator_college:
                    raise ValueError(
                        f"学院级管理员只能选择本学院教师作为专家。"
                        f"专家 {member.real_name}({member.employee_id}) 不属于 {creator_college}"
                    )

        created_reviews = []
        phase = ReviewService._get_phase_from_review_type(review_type)
        if not phase:
            raise ValueError("不支持该评审类型的专家分配")

        with transaction.atomic():
            for pid in project_ids:
                try:
                    project = Project.objects.get(pk=pid)
                except Project.DoesNotExist:
                    continue

                # ===== 新增：指导老师排除检查 =====
                advisor_ids = set(project.advisors.values_list("user_id", flat=True))
                member_ids = set(experts.values_list("id", flat=True))
                intersection = advisor_ids & member_ids
                if intersection:
                    from apps.users.models import User

                    advisor_names = list(
                        User.objects.filter(id__in=intersection).values_list(
                            "real_name", flat=True
                        )
                    )
                    raise ValueError(
                        f"项目 {project.project_no} 的专家组成员包含项目指导老师（{', '.join(advisor_names)}），"
                        f"请重新选择专家组"
                    )

                phase_instance = ProjectPhaseService.get_current(project, phase)
                if not phase_instance:
                    ReviewService.logger.warning(
                        "Project %s has no phase instance for expert assignment",
                        project.id,
                    )
                    continue
                if (
                    target_node_id
                    and phase_instance.current_node_id
                    and target_node_id != phase_instance.current_node_id
                ):
                    ReviewService.logger.warning(
                        "Project %s current node mismatch for expert assignment",
                        project.id,
                    )
                    continue
                node_id = target_node_id or phase_instance.current_node_id
                if not node_id:
                    ReviewService.logger.warning(
                        "Project %s has no current node for expert assignment",
                        project.id,
                    )
                    continue
                node_obj = WorkflowService.get_node_by_id(node_id)
                if not node_obj:
                    ReviewService.logger.warning(
                        "Node %s not found for expert assignment", node_id
                    )
                    continue
                if not node_obj.require_expert_review:
                    ReviewService.logger.warning(
                        "Node %s does not require expert review", node_id
                    )
                    continue
                assigned_user = AdminAssignmentService.resolve_admin_user(
                    project, phase, node_obj
                )
                if creator and assigned_user.id != creator.id:
                    raise ValueError("无权限分配该节点的专家评审任务")
                review_level_value = (
                    node_obj.review_level or node_obj.get_role_code() or review_level
                )
                if not review_level_value:
                    raise ValueError("审核节点未配置审核级别或角色")

                for expert in experts:
                    # Check duplication
                    if not Review.objects.filter(
                        project=project,
                        reviewer=expert,
                        review_type=review_type,
                        review_level=review_level_value,
                        phase_instance=phase_instance,
                        workflow_node_id=node_id,
                        is_expert_review=True,
                    ).exists():
                        review = ReviewService.create_review(
                            project=project,
                            phase_instance=phase_instance,
                            review_type=review_type,
                            review_level=review_level_value,
                            reviewer=expert,
                            workflow_node=node_id,
                            is_expert_review=True,
                        )
                        created_reviews.append(review)
                        NotificationService.notify_review_assigned(review)

        return created_reviews
