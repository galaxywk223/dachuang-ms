"""
Project workflow/expert-summary actions.

Keep `ProjectViewSet` smaller by extracting workflow-heavy endpoints here.
"""

from django.db import transaction
from django.db.models import Avg
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from apps.projects.models import ProjectPhaseInstance
from apps.projects.services.archive_service import ensure_project_archive
from apps.projects.services.phase_service import ProjectPhaseService
from apps.system_settings.services import WorkflowService
from apps.reviews.models import Review
from apps.reviews.services import ReviewService

from ...models import Project


class ProjectWorkflowMixin:
    def _get_current_phase_instance(
        self, project: Project, phase: str
    ) -> ProjectPhaseInstance | None:
        return ProjectPhaseService.get_current(project, phase)

    def _get_expert_reviews_qs(
        self,
        *,
        project: Project,
        review_type: str,
        review_level: str,
        phase_instance: ProjectPhaseInstance | None,
    ):
        qs = Review.objects.filter(
            project=project,
            review_type=review_type,
            review_level=review_level,
            reviewer__role="EXPERT",
        )
        if phase_instance:
            qs = qs.filter(phase_instance=phase_instance)
        return qs

    @action(detail=True, methods=["get"], url_path="expert-summary")
    def expert_summary(self, request, pk=None):
        """
        获取当前阶段专家评审进度/统计（不改变流程）
        query: review_type=APPLICATION|MID_TERM|CLOSURE, scope=COLLEGE|SCHOOL(optional)
        """
        project = self.get_object()
        review_type = (
            request.query_params.get("review_type") or Review.ReviewType.APPLICATION
        )
        scope = (request.query_params.get("scope") or "COLLEGE").upper()
        review_level = (
            Review.ReviewLevel.LEVEL2
            if scope == "COLLEGE"
            else Review.ReviewLevel.LEVEL1
        )

        phase_instance = self._get_current_phase_instance(project, review_type)
        qs = self._get_expert_reviews_qs(
            project=project,
            review_type=review_type,
            review_level=review_level,
            phase_instance=phase_instance,
        )
        assigned = qs.count()
        pending = qs.filter(status=Review.ReviewStatus.PENDING).count()
        submitted = assigned - pending
        approved_count = qs.filter(status=Review.ReviewStatus.APPROVED).count()
        rejected_count = qs.filter(status=Review.ReviewStatus.REJECTED).count()
        avg_score = qs.exclude(status=Review.ReviewStatus.PENDING).aggregate(avg=Avg("score")).get("avg")

        return Response(
            {
                "code": 200,
                "message": "获取成功",
                "data": {
                    "phase_instance_id": phase_instance.id if phase_instance else None,
                    "attempt_no": phase_instance.attempt_no if phase_instance else None,
                    "step": phase_instance.step if phase_instance else "",
                    "state": phase_instance.state if phase_instance else "",
                    "assigned": assigned,
                    "submitted": submitted,
                    "pending": pending,
                    "approved": approved_count,
                    "rejected": rejected_count,
                    "all_submitted": assigned > 0 and pending == 0,
                    "avg_score": avg_score,
                },
            }
        )

    @action(detail=True, methods=["post"], url_path="workflow/return-to-student")
    def workflow_return_to_student(self, request, pk=None):
        """
        管理员退回学生修改（创建新一轮由学生重新提交触发）
        body: { phase: APPLICATION|MID_TERM|CLOSURE, reason?: str }
        """
        project = self.get_object()
        user = request.user
        phase = request.data.get("phase") or ProjectPhaseInstance.Phase.APPLICATION
        reason = request.data.get("reason", "")

        if phase == ProjectPhaseInstance.Phase.APPLICATION and not (
            user.is_level2_admin or user.is_level1_admin
        ):
            raise PermissionDenied("无权限退回该阶段")
        if phase == ProjectPhaseInstance.Phase.MID_TERM and not (
            user.is_level2_admin or user.is_level1_admin
        ):
            raise PermissionDenied("无权限退回该阶段")
        if phase == ProjectPhaseInstance.Phase.CLOSURE:
            phase_instance_for_perm = self._get_current_phase_instance(
                project, ProjectPhaseInstance.Phase.CLOSURE
            )
            if user.is_level1_admin:
                pass
            elif (
                user.is_level2_admin
                and phase_instance_for_perm
                and str(phase_instance_for_perm.step).startswith("COLLEGE_")
            ):
                pass
            else:
                raise PermissionDenied("无权限退回该阶段")

        status_map = {
            ProjectPhaseInstance.Phase.APPLICATION: Project.ProjectStatus.APPLICATION_RETURNED,
            ProjectPhaseInstance.Phase.MID_TERM: Project.ProjectStatus.MID_TERM_RETURNED,
            ProjectPhaseInstance.Phase.CLOSURE: Project.ProjectStatus.CLOSURE_RETURNED,
        }
        new_status = status_map.get(phase, Project.ProjectStatus.DRAFT)

        with transaction.atomic():
            phase_instance = self._get_current_phase_instance(project, phase)
            if phase_instance:
                ProjectPhaseService.mark_returned(
                    phase_instance,
                    return_to=ProjectPhaseInstance.ReturnTo.STUDENT,
                    reason=reason,
                )
                Review.objects.filter(
                    project=project,
                    phase_instance=phase_instance,
                    reviewer__role="EXPERT",
                    status=Review.ReviewStatus.PENDING,
                ).update(
                    status=Review.ReviewStatus.REJECTED,
                    comments="管理员退回，评审任务作废",
                    reviewed_at=timezone.now(),
                )

            project.status = new_status
            project.save(update_fields=["status", "updated_at"])

        return Response({"code": 200, "message": "已退回学生修改"})

    @action(detail=True, methods=["post"], url_path="workflow/report-to-school")
    def workflow_report_to_school(self, request, pk=None):
        """
        学院管理员上报校级（立项流程）
        要求：院级专家评审任务已全部提交
        """
        project = self.get_object()
        user = request.user
        if not user.is_level2_admin:
            raise PermissionDenied("只有二级管理员可以上报校级")

        phase_instance = self._get_current_phase_instance(
            project, ProjectPhaseInstance.Phase.APPLICATION
        )
        qs = self._get_expert_reviews_qs(
            project=project,
            review_type=Review.ReviewType.APPLICATION,
            review_level=Review.ReviewLevel.LEVEL2,
            phase_instance=phase_instance,
        )
        if not qs.exists():
            return Response(
                {"code": 400, "message": "请先分配专家评审"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if qs.filter(status=Review.ReviewStatus.PENDING).exists():
            return Response(
                {"code": 400, "message": "院级专家评审尚未全部提交"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            if phase_instance:
                school_node = WorkflowService.find_expert_node(
                    ProjectPhaseInstance.Phase.APPLICATION,
                    Review.ReviewLevel.LEVEL1,
                    "SCHOOL",
                    project.batch,
                )
                update_fields = ["updated_at"]
                if school_node:
                    phase_instance.step = school_node.code
                    phase_instance.current_node_id = school_node.id
                    update_fields.extend(["step", "current_node_id"])
                phase_instance.save(update_fields=update_fields)
            project.status = Project.ProjectStatus.LEVEL1_AUDITING
            project.save(update_fields=["status", "updated_at"])

        return Response({"code": 200, "message": "已上报校级"})

    @action(detail=True, methods=["post"], url_path="workflow/report-to-school-closure")
    def workflow_report_to_school_closure(self, request, pk=None):
        """
        学院管理员上报校级（结题流程）
        要求：院级专家评审任务已全部提交
        """
        project = self.get_object()
        user = request.user
        if not user.is_level2_admin:
            raise PermissionDenied("只有二级管理员可以上报校级")

        phase_instance = self._get_current_phase_instance(
            project, ProjectPhaseInstance.Phase.CLOSURE
        )
        if phase_instance is None:
            return Response(
                {
                    "code": 400,
                    "message": "流程状态异常：缺少结题阶段轮次，请重新上报或联系管理员",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        qs = self._get_expert_reviews_qs(
            project=project,
            review_type=Review.ReviewType.CLOSURE,
            review_level=Review.ReviewLevel.LEVEL2,
            phase_instance=phase_instance,
        )
        if not qs.exists():
            return Response(
                {"code": 400, "message": "请先分配专家评审"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if qs.filter(status=Review.ReviewStatus.PENDING).exists():
            return Response(
                {"code": 400, "message": "院级专家评审尚未全部提交"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            school_node = WorkflowService.find_expert_node(
                ProjectPhaseInstance.Phase.CLOSURE,
                Review.ReviewLevel.LEVEL1,
                "SCHOOL",
                project.batch,
            )
            update_fields = ["updated_at"]
            if school_node:
                phase_instance.step = school_node.code
                phase_instance.current_node_id = school_node.id
                update_fields.extend(["step", "current_node_id"])
            phase_instance.save(update_fields=update_fields)
            project.status = Project.ProjectStatus.CLOSURE_LEVEL1_REVIEWING
            project.save(update_fields=["status", "updated_at"])

        return Response({"code": 200, "message": "已上报校级"})

    @action(detail=True, methods=["post"], url_path="workflow/publish-establishment")
    def workflow_publish_establishment(self, request, pk=None):
        """
        校级管理员发布立项（录入批准金额）
        body: { approved_budget?: number }
        """
        project = self.get_object()
        user = request.user
        if not user.is_level1_admin:
            raise PermissionDenied("只有一级管理员可以发布立项")

        approved_budget = request.data.get("approved_budget")
        try:
            approved_budget_val = (
                float(approved_budget)
                if approved_budget is not None and approved_budget != ""
                else None
            )
        except Exception:
            return Response(
                {"code": 400, "message": "approved_budget格式错误"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        phase_instance = self._get_current_phase_instance(
            project, ProjectPhaseInstance.Phase.APPLICATION
        )
        qs = self._get_expert_reviews_qs(
            project=project,
            review_type=Review.ReviewType.APPLICATION,
            review_level=Review.ReviewLevel.LEVEL1,
            phase_instance=phase_instance,
        )
        if qs.exists() and qs.filter(status=Review.ReviewStatus.PENDING).exists():
            return Response(
                {"code": 400, "message": "校级专家评审尚未全部提交"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            if approved_budget_val is not None:
                project.approved_budget = approved_budget_val
            project.status = Project.ProjectStatus.IN_PROGRESS
            project.save(update_fields=["approved_budget", "status", "updated_at"])
            if phase_instance:
                ProjectPhaseService.mark_completed(phase_instance, step="PUBLISHED")

        return Response({"code": 200, "message": "立项已发布"})

    @action(detail=True, methods=["post"], url_path="workflow/finalize-midterm")
    def workflow_finalize_midterm(self, request, pk=None):
        """
        中期阶段管理员最终处理（通过/退回）
        body: { action: pass|return, reason?: str }
        """
        project = self.get_object()
        user = request.user
        if not (user.is_level2_admin or user.is_level1_admin):
            raise PermissionDenied("无权限操作")

        action_type = request.data.get("action")
        reason = request.data.get("reason", "")
        if action_type not in ("pass", "return"):
            return Response(
                {"code": 400, "message": "action必须为pass或return"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        phase_instance = self._get_current_phase_instance(
            project, ProjectPhaseInstance.Phase.MID_TERM
        )
        qs = self._get_expert_reviews_qs(
            project=project,
            review_type=Review.ReviewType.MID_TERM,
            review_level=Review.ReviewLevel.LEVEL2,
            phase_instance=phase_instance,
        )
        if qs.exists() and qs.filter(status=Review.ReviewStatus.PENDING).exists():
            return Response(
                {"code": 400, "message": "中期专家审核尚未全部提交"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            if action_type == "pass":
                project.status = Project.ProjectStatus.READY_FOR_CLOSURE
                project.save(update_fields=["status", "updated_at"])
                if phase_instance:
                    ProjectPhaseService.mark_completed(phase_instance, step="COMPLETED")
            else:
                project.status = Project.ProjectStatus.MID_TERM_RETURNED
                project.save(update_fields=["status", "updated_at"])
                if phase_instance:
                    ProjectPhaseService.mark_returned(
                        phase_instance,
                        return_to=ProjectPhaseInstance.ReturnTo.STUDENT,
                        reason=reason,
                    )
                    Review.objects.filter(
                        project=project,
                        phase_instance=phase_instance,
                        reviewer__role="EXPERT",
                        status=Review.ReviewStatus.PENDING,
                    ).update(
                        status=Review.ReviewStatus.REJECTED,
                        comments="管理员退回，评审任务作废",
                        reviewed_at=timezone.now(),
                    )

        return Response({"code": 200, "message": "处理中期完成"})

    @action(detail=True, methods=["post"], url_path="workflow/finalize-closure")
    def workflow_finalize_closure(self, request, pk=None):
        """
        结题阶段校级管理员最终处理（通过/退回）
        body: { action: approve|return, reason?: str, return_to?: student|teacher }
        """
        project = self.get_object()
        user = request.user
        if not user.is_level1_admin:
            raise PermissionDenied("只有一级管理员可以操作结题")

        action_type = request.data.get("action")
        reason = request.data.get("reason", "")
        return_to = (request.data.get("return_to") or "student").lower()
        if action_type not in ("approve", "return"):
            return Response(
                {"code": 400, "message": "action必须为approve或return"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if action_type == "return" and return_to not in ("student", "teacher"):
            return Response(
                {"code": 400, "message": "return_to必须为student或teacher"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        phase_instance = self._get_current_phase_instance(
            project, ProjectPhaseInstance.Phase.CLOSURE
        )
        if phase_instance is None:
            return Response(
                {"code": 400, "message": "请先分配校级专家评审"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        qs = self._get_expert_reviews_qs(
            project=project,
            review_type=Review.ReviewType.CLOSURE,
            review_level=Review.ReviewLevel.LEVEL1,
            phase_instance=phase_instance,
        )
        if not qs.exists():
            return Response(
                {"code": 400, "message": "请先分配专家评审"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if qs.filter(status=Review.ReviewStatus.PENDING).exists():
            return Response(
                {"code": 400, "message": "结题专家评审尚未全部提交"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            if action_type == "approve":
                project.status = Project.ProjectStatus.CLOSED
                project.save(update_fields=["status", "updated_at"])
                ensure_project_archive(project)
                if phase_instance:
                    ProjectPhaseService.mark_completed(phase_instance, step="COMPLETED")
            else:
                if return_to == "teacher":
                    project.status = Project.ProjectStatus.CLOSURE_SUBMITTED
                else:
                    project.status = Project.ProjectStatus.CLOSURE_RETURNED
                project.save(update_fields=["status", "updated_at"])
                if phase_instance:
                    ProjectPhaseService.mark_returned(
                        phase_instance,
                        return_to=ProjectPhaseInstance.ReturnTo.TEACHER
                        if return_to == "teacher"
                        else ProjectPhaseInstance.ReturnTo.STUDENT,
                        reason=reason,
                    )
                    Review.objects.filter(
                        project=project,
                        phase_instance=phase_instance,
                        reviewer__role="EXPERT",
                        status=Review.ReviewStatus.PENDING,
                    ).update(
                        status=Review.ReviewStatus.REJECTED,
                        comments="管理员退回，评审任务作废",
                        reviewed_at=timezone.now(),
                    )
                if return_to == "teacher":
                    ReviewService.create_closure_teacher_review(project)

        return Response({"code": 200, "message": "处理完成"})
