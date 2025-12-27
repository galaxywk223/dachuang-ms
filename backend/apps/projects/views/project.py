"""
项目视图
"""

from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone
from django.http import HttpResponse
from django.db import transaction
from django.db.models import Avg
import openpyxl
from io import BytesIO
import zipfile

from ..models import Project, ProjectMember, ProjectProgress, ProjectAchievement, ProjectExpenditure
from ..serializers import (
    ProjectSerializer,
    ProjectListSerializer,
    ProjectMemberSerializer,
    ProjectProgressSerializer,
    ProjectSubmitSerializer,
    ProjectAchievementSerializer,
    ProjectClosureSerializer,
    ProjectExpenditureSerializer,
)
from ..serializers.midterm import ProjectMidTermSerializer
from ..services import ProjectService
from ..certificates import render_certificate_html
from apps.reviews.services import ReviewService
from apps.reviews.models import Review
from apps.projects.models import ProjectPhaseInstance, ProjectArchive
from apps.projects.services.phase_service import ProjectPhaseService
from apps.system_settings.services import SystemSettingService



class ProjectViewSet(viewsets.ModelViewSet):
    """
    项目管理视图集
    """

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["status", "level", "leader__college", "leader", "batch", "year"]
    search_fields = ["project_no", "title", "advisors__user__real_name"]
    ordering_fields = ["created_at", "updated_at", "submitted_at"]

    @action(detail=True, methods=["get"], url_path="budget-stats")
    def budget_stats(self, request, pk=None):
        """
        获取项目经费统计
        """
        project = self.get_object()
        stats = ProjectService.get_budget_stats(project)
        return Response({"code": 200, "message": "获取成功", "data": stats})

    @action(detail=True, methods=["get"], url_path="certificate")
    def certificate(self, request, pk=None):
        """
        获取结题证书（HTML）
        """
        project = self.get_object()
        user = request.user

        if project.status != Project.ProjectStatus.CLOSED:
            return Response(
                {"code": 400, "message": "项目未结题，无法生成证书"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not (
            user.is_level1_admin
            or user.is_level2_admin
            or (user.is_student and project.leader_id == user.id)
        ):
            return Response(
                {"code": 403, "message": "无权限访问"},
                status=status.HTTP_403_FORBIDDEN,
            )

        html = render_certificate_html(project)
        return HttpResponse(html, content_type="text/html")

    def get_serializer_class(self):
        if self.action == "list":
            return ProjectListSerializer
        return ProjectSerializer

    def get_queryset(self):
        """
        根据用户角色过滤项目
        """
        from django.db.models import Q, OuterRef, Subquery, Exists

        user = self.request.user
        queryset = super().get_queryset()

        # 学生只能看到自己参与的项目
        if user.is_student:
            queryset = queryset.filter(Q(leader=user) | Q(members=user)).distinct()
        # 二级管理员只能看到自己学院的项目
        elif user.is_level2_admin:
            queryset = queryset.filter(leader__college=user.college)
        # 一级管理员可以看到所有项目
        elif user.is_level1_admin:
            pass
        # 指导教师只能看到自己指导的项目
        elif user.role == "TEACHER":
            queryset = queryset.filter(advisors__user=user).distinct()

        status_in = self.request.query_params.get("status_in")
        if status_in:
            status_list = [s.strip() for s in status_in.split(",") if s.strip()]
            queryset = queryset.filter(status__in=status_list)

        exclude_review_type = self.request.query_params.get("exclude_assigned_review_type")
        exclude_review_level = self.request.query_params.get("exclude_assigned_review_level")
        if exclude_review_type:
            current_phase_qs = ProjectPhaseInstance.objects.filter(
                project_id=OuterRef("pk"),
                phase=exclude_review_type,
            ).order_by("-attempt_no", "-id")
            queryset = queryset.annotate(
                _current_phase_instance_id=Subquery(current_phase_qs.values("id")[:1])
            )
            assigned_reviews = Review.objects.filter(
                project_id=OuterRef("pk"),
                review_type=exclude_review_type,
                reviewer__isnull=False,
                phase_instance_id=OuterRef("_current_phase_instance_id"),
            )
            if exclude_review_level:
                assigned_reviews = assigned_reviews.filter(review_level=exclude_review_level)
            queryset = queryset.annotate(_has_assigned=Exists(assigned_reviews)).filter(_has_assigned=False)

        phase = self.request.query_params.get("phase")
        phase_step = self.request.query_params.get("phase_step")
        phase_state = self.request.query_params.get("phase_state")
        if phase:
            current_phase_qs = ProjectPhaseInstance.objects.filter(
                project_id=OuterRef("pk"),
                phase=phase,
            ).order_by("-attempt_no", "-id")
            queryset = queryset.annotate(
                _phase_step=Subquery(current_phase_qs.values("step")[:1]),
                _phase_state=Subquery(current_phase_qs.values("state")[:1]),
            )
            if phase_step:
                queryset = queryset.filter(_phase_step=phase_step)
            if phase_state:
                queryset = queryset.filter(_phase_state=phase_state)

        return queryset

    def list(self, request, *args, **kwargs):
        """
        统一返回结构，方便前端处理
        """
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return Response(
                {
                    "code": 200,
                    "message": "获取成功",
                    "data": {
                        "results": serializer.data,
                        "count": self.paginator.page.paginator.count,
                    },
                }
            )

        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "code": 200,
                "message": "获取成功",
                "data": {"results": serializer.data, "count": len(serializer.data)},
            }
        )

    def retrieve(self, request, *args, **kwargs):
        """
        项目详情统一返回结构
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"code": 200, "message": "获取成功", "data": serializer.data})

    def perform_create(self, serializer):
        """
        创建项目时设置负责人为当前用户
        """
        project = serializer.save(leader=self.request.user)
        # 自动将负责人添加为项目成员
        ProjectMember.objects.create(
            project=project,
            user=self.request.user,
            role=ProjectMember.MemberRole.LEADER,
        )

    @action(methods=["post"], detail=True)
    def submit(self, request, pk=None):
        """
        提交项目申报
        """
        project = self.get_object()

        # 检查权限
        if project.leader != request.user:
            return Response(
                {"code": 403, "message": "只有项目负责人可以提交项目"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # 检查项目状态
        if project.status not in [
            Project.ProjectStatus.DRAFT,
            Project.ProjectStatus.APPLICATION_RETURNED,
        ]:
            return Response(
                {"code": 400, "message": "项目状态不允许提交"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 更新项目状态
        # 更新项目状态并创建导师审核
        from apps.reviews.services import ReviewService
        from apps.projects.models import ProjectPhaseInstance
        from apps.projects.services.phase_service import ProjectPhaseService

        current_phase = ProjectPhaseService.get_current(
            project, ProjectPhaseInstance.Phase.APPLICATION
        )
        if current_phase and current_phase.state == ProjectPhaseInstance.State.RETURNED:
            ProjectPhaseService.start_new_attempt(
                project,
                ProjectPhaseInstance.Phase.APPLICATION,
                created_by=request.user,
                step="TEACHER_REVIEWING",
            )
        # This will set status to TEACHER_AUDITING
        ReviewService.create_teacher_review(project)
        
        project.submitted_at = timezone.now()
        project.save(update_fields=["submitted_at"])

        return Response({"code": 200, "message": "项目提交成功，等待导师审核"})

    def _get_current_phase_instance(self, project: Project, phase: str) -> ProjectPhaseInstance | None:
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
        review_type = request.query_params.get("review_type") or Review.ReviewType.APPLICATION
        scope = (request.query_params.get("scope") or "COLLEGE").upper()
        review_level = Review.ReviewLevel.LEVEL2 if scope == "COLLEGE" else Review.ReviewLevel.LEVEL1

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

        if phase == ProjectPhaseInstance.Phase.APPLICATION and not (user.is_level2_admin or user.is_level1_admin):
            raise PermissionDenied("无权限退回该阶段")
        if phase == ProjectPhaseInstance.Phase.MID_TERM and not (user.is_level2_admin or user.is_level1_admin):
            raise PermissionDenied("无权限退回该阶段")
        if phase == ProjectPhaseInstance.Phase.CLOSURE:
            phase_instance_for_perm = self._get_current_phase_instance(project, ProjectPhaseInstance.Phase.CLOSURE)
            if user.is_level1_admin:
                pass
            elif user.is_level2_admin and phase_instance_for_perm and str(phase_instance_for_perm.step).startswith("COLLEGE_"):
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
                    phase_instance, return_to=ProjectPhaseInstance.ReturnTo.STUDENT, reason=reason
                )
                # 作废该轮未完成的专家评审任务（避免专家端长期挂着待评审）
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

        phase_instance = self._get_current_phase_instance(project, ProjectPhaseInstance.Phase.APPLICATION)
        qs = self._get_expert_reviews_qs(
            project=project,
            review_type=Review.ReviewType.APPLICATION,
            review_level=Review.ReviewLevel.LEVEL2,
            phase_instance=phase_instance,
        )
        if not qs.exists():
            return Response({"code": 400, "message": "请先分配专家评审"}, status=status.HTTP_400_BAD_REQUEST)
        if qs.filter(status=Review.ReviewStatus.PENDING).exists():
            return Response({"code": 400, "message": "院级专家评审尚未全部提交"}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            if phase_instance:
                phase_instance.step = "SCHOOL_EXPERT_SCORING"
                phase_instance.save(update_fields=["step", "updated_at"])
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

        phase_instance = self._get_current_phase_instance(project, ProjectPhaseInstance.Phase.CLOSURE)

        if phase_instance is None:
            return Response({"code": 400, "message": "流程状态异常：缺少结题阶段轮次，请重新上报或联系管理员"}, status=status.HTTP_400_BAD_REQUEST)
        qs = self._get_expert_reviews_qs(
            project=project,
            review_type=Review.ReviewType.CLOSURE,
            review_level=Review.ReviewLevel.LEVEL2,
            phase_instance=phase_instance,
        )
        if not qs.exists():
            return Response({"code": 400, "message": "请先分配专家评审"}, status=status.HTTP_400_BAD_REQUEST)
        if qs.filter(status=Review.ReviewStatus.PENDING).exists():
            return Response({"code": 400, "message": "院级专家评审尚未全部提交"}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            if phase_instance:
                phase_instance.step = "SCHOOL_EXPERT_SCORING"
                phase_instance.save(update_fields=["step", "updated_at"])
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
            approved_budget_val = float(approved_budget) if approved_budget is not None and approved_budget != "" else None
        except Exception:
            return Response({"code": 400, "message": "approved_budget格式错误"}, status=status.HTTP_400_BAD_REQUEST)

        phase_instance = self._get_current_phase_instance(project, ProjectPhaseInstance.Phase.APPLICATION)
        qs = self._get_expert_reviews_qs(
            project=project,
            review_type=Review.ReviewType.APPLICATION,
            review_level=Review.ReviewLevel.LEVEL1,
            phase_instance=phase_instance,
        )
        if qs.exists() and qs.filter(status=Review.ReviewStatus.PENDING).exists():
            return Response({"code": 400, "message": "校级专家评审尚未全部提交"}, status=status.HTTP_400_BAD_REQUEST)

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
            return Response({"code": 400, "message": "action必须为pass或return"}, status=status.HTTP_400_BAD_REQUEST)

        phase_instance = self._get_current_phase_instance(project, ProjectPhaseInstance.Phase.MID_TERM)
        qs = self._get_expert_reviews_qs(
            project=project,
            review_type=Review.ReviewType.MID_TERM,
            review_level=Review.ReviewLevel.LEVEL2,
            phase_instance=phase_instance,
        )
        if qs.exists() and qs.filter(status=Review.ReviewStatus.PENDING).exists():
            return Response({"code": 400, "message": "中期专家审核尚未全部提交"}, status=status.HTTP_400_BAD_REQUEST)

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
        body: { action: approve|return, reason?: str }
        """
        project = self.get_object()
        user = request.user
        if not user.is_level1_admin:
            raise PermissionDenied("只有一级管理员可以操作结题")

        action_type = request.data.get("action")
        reason = request.data.get("reason", "")
        if action_type not in ("approve", "return"):
            return Response({"code": 400, "message": "action必须为approve或return"}, status=status.HTTP_400_BAD_REQUEST)

        phase_instance = self._get_current_phase_instance(project, ProjectPhaseInstance.Phase.CLOSURE)

        if phase_instance is None:
            return Response({"code": 400, "message": "请先分配校级专家评审"}, status=status.HTTP_400_BAD_REQUEST)
        qs = self._get_expert_reviews_qs(
            project=project,
            review_type=Review.ReviewType.CLOSURE,
            review_level=Review.ReviewLevel.LEVEL1,
            phase_instance=phase_instance,
        )
        if not qs.exists():
            return Response({"code": 400, "message": "请先分配专家评审"}, status=status.HTTP_400_BAD_REQUEST)
        if qs.filter(status=Review.ReviewStatus.PENDING).exists():
            return Response({"code": 400, "message": "结题专家评审尚未全部提交"}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            if action_type == "approve":
                project.status = Project.ProjectStatus.CLOSED
                project.save(update_fields=["status", "updated_at"])
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
                if phase_instance:
                    ProjectPhaseService.mark_completed(phase_instance, step="COMPLETED")
            else:
                project.status = Project.ProjectStatus.CLOSURE_RETURNED
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

        return Response({"code": 200, "message": "处理完成"})

    @action(methods=["post"], detail=True)
    def add_member(self, request, pk=None):
        """
        添加项目成员
        """
        project = self.get_object()

        # 检查权限
        if project.leader != request.user:
            return Response(
                {"code": 403, "message": "只有项目负责人可以添加成员"},
                status=status.HTTP_403_FORBIDDEN,
            )

        user_id = request.data.get("user_id")
        if not user_id:
            return Response(
                {"code": 400, "message": "请提供用户ID"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            from apps.users.models import User

            user = User.objects.get(id=user_id)

            # 检查是否已是成员
            if ProjectMember.objects.filter(project=project, user=user).exists():
                return Response(
                    {"code": 400, "message": "该用户已是项目成员"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 添加成员
            member = ProjectMember.objects.create(
                project=project, user=user, role=ProjectMember.MemberRole.MEMBER
            )

            serializer = ProjectMemberSerializer(member)
            return Response(
                {"code": 200, "message": "成员添加成功", "data": serializer.data}
            )
        except User.DoesNotExist:
            return Response(
                {"code": 404, "message": "用户不存在"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(
        methods=["delete"], detail=True, url_path="remove-member/(?P<member_id>[^/.]+)"
    )
    def remove_member(self, request, pk=None, member_id=None):
        """
        移除项目成员
        """
        project = self.get_object()

        # 检查权限
        if project.leader != request.user:
            return Response(
                {"code": 403, "message": "只有项目负责人可以移除成员"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            member = ProjectMember.objects.get(project=project, id=member_id)

            # 不能移除负责人
            if member.role == ProjectMember.MemberRole.LEADER:
                return Response(
                    {"code": 400, "message": "不能移除项目负责人"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            member.delete()
            return Response({"code": 200, "message": "成员移除成功"})
        except ProjectMember.DoesNotExist:
            return Response(
                {"code": 404, "message": "成员不存在"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(methods=["get"], detail=True)
    def progress(self, request, pk=None):
        """
        获取项目进度列表
        """
        project = self.get_object()
        progress_list = project.progress_records.all()
        serializer = ProjectProgressSerializer(progress_list, many=True)
        return Response({"code": 200, "data": serializer.data})

    @action(methods=["post"], detail=True, url_path="add-progress")
    def add_progress(self, request, pk=None):
        """
        添加项目进度
        """
        project = self.get_object()

        # 检查是否是项目成员
        if not ProjectMember.objects.filter(
            project=project, user=request.user
        ).exists():
            return Response(
                {"code": 403, "message": "只有项目成员可以添加进度"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ProjectProgressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(project=project, created_by=request.user)

        return Response(
            {"code": 200, "message": "进度添加成功", "data": serializer.data}
        )

    @action(methods=["post"], detail=True, url_path="apply-mid-term")
    def apply_mid_term(self, request, pk=None):
        """
        申请中期检查
        """
        project = self.get_object()

        # 检查权限
        if project.leader != request.user:
            return Response(
                {"code": 403, "message": "只有项目负责人可以申请中期检查"},
                status=status.HTTP_403_FORBIDDEN,
            )

        data = request.data.copy()
        data["project_id"] = project.id
        serializer = ProjectMidTermSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        mid_term_report = serializer.validated_data.get("mid_term_report")
        is_draft = serializer.validated_data.get("is_draft", False)

        try:
            if not is_draft:
                ok, msg = SystemSettingService.check_window(
                    "MIDTERM_WINDOW", timezone.now().date(), batch=project.batch
                )
                if not ok:
                    return Response(
                        {"code": 400, "message": msg or "当前不在中期提交时间范围内"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            ProjectService.apply_mid_term(project, mid_term_report, is_draft)
            message = "中期检查已保存为草稿" if is_draft else "中期检查申请提交成功"
            
            # 如果是正式提交，创建导师审核任务
            if not is_draft:
                 current_phase = ProjectPhaseService.get_current(
                     project, ProjectPhaseInstance.Phase.MID_TERM
                 )
                 if current_phase and current_phase.state == ProjectPhaseInstance.State.RETURNED:
                     ProjectPhaseService.start_new_attempt(
                         project,
                         ProjectPhaseInstance.Phase.MID_TERM,
                         created_by=request.user,
                         step="TEACHER_REVIEWING",
                     )
                 ReviewService.create_mid_term_teacher_review(project)
                 
            return Response({"code": 200, "message": message})
        except ValueError as e:
            return Response(
                {"code": 400, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(methods=["post"], detail=True, url_path="submit-mid-term")
    def submit_mid_term(self, request, pk=None):
        """
        提交中期检查（从草稿状态）
        """
        project = self.get_object()

        # 检查权限
        if project.leader != request.user:
            return Response(
                {"code": 403, "message": "只有项目负责人可以提交中期检查"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            ok, msg = SystemSettingService.check_window(
                "MIDTERM_WINDOW", timezone.now().date(), batch=project.batch
            )
            if not ok:
                return Response(
                    {"code": 400, "message": msg or "当前不在中期提交时间范围内"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if ProjectService.submit_mid_term(project):
                # 创建导师审核任务
                current_phase = ProjectPhaseService.get_current(
                    project, ProjectPhaseInstance.Phase.MID_TERM
                )
                if current_phase and current_phase.state == ProjectPhaseInstance.State.RETURNED:
                    ProjectPhaseService.start_new_attempt(
                        project,
                        ProjectPhaseInstance.Phase.MID_TERM,
                        created_by=request.user,
                        step="TEACHER_REVIEWING",
                    )
                ReviewService.create_mid_term_teacher_review(project)
                return Response({"code": 200, "message": "中期检查申请提交成功"})
            else:
                return Response(
                    {"code": 400, "message": "项目状态不允许提交"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except ValueError as e:
            return Response(
                {"code": 400, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(methods=["post"], detail=True, url_path="apply-closure")
    def apply_closure(self, request, pk=None):
        """
        申请项目结题
        """
        project = self.get_object()

        # 检查权限
        if project.leader != request.user:
            return Response(
                {"code": 403, "message": "只有项目负责人可以申请结题"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ProjectClosureSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        is_draft = serializer.validated_data.get("is_draft", False)
        final_report = serializer.validated_data.get("final_report")

        try:
            if not is_draft:
                ok, msg = SystemSettingService.check_window(
                    "CLOSURE_WINDOW", timezone.now().date(), batch=project.batch
                )
                if not ok:
                    return Response(
                        {"code": 400, "message": msg or "当前不在结题提交时间范围内"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            ProjectService.apply_closure(project, final_report, is_draft)
            if not is_draft:
                current_phase = ProjectPhaseService.get_current(
                    project, ProjectPhaseInstance.Phase.CLOSURE
                )
                if current_phase and current_phase.state == ProjectPhaseInstance.State.RETURNED:
                    ProjectPhaseService.start_new_attempt(
                        project,
                        ProjectPhaseInstance.Phase.CLOSURE,
                        created_by=request.user,
                        step="TEACHER_REVIEWING",
                    )
                ReviewService.create_closure_teacher_review(project)
            message = "结题申请已保存为草稿" if is_draft else "结题申请提交成功"
            return Response({"code": 200, "message": message})
        except ValueError as e:
            return Response(
                {"code": 400, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(methods=["post"], detail=True, url_path="submit-closure")
    def submit_closure(self, request, pk=None):
        """
        提交结题申请（从草稿状态）
        """
        project = self.get_object()

        # 检查权限
        if project.leader != request.user:
            return Response(
                {"code": 403, "message": "只有项目负责人可以提交结题"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            ok, msg = SystemSettingService.check_window(
                "CLOSURE_WINDOW", timezone.now().date(), batch=project.batch
            )
            if not ok:
                return Response(
                    {"code": 400, "message": msg or "当前不在结题提交时间范围内"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if ProjectService.submit_closure(project):
                # 创建导师审核记录
                current_phase = ProjectPhaseService.get_current(
                    project, ProjectPhaseInstance.Phase.CLOSURE
                )
                if current_phase and current_phase.state == ProjectPhaseInstance.State.RETURNED:
                    ProjectPhaseService.start_new_attempt(
                        project,
                        ProjectPhaseInstance.Phase.CLOSURE,
                        created_by=request.user,
                        step="TEACHER_REVIEWING",
                    )
                ReviewService.create_closure_teacher_review(project)
                return Response({"code": 200, "message": "结题申请提交成功"})
            else:
                return Response(
                    {"code": 400, "message": "项目状态不允许提交"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except ValueError as e:
            return Response(
                {"code": 400, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(methods=["post"], detail=True, url_path="revoke-closure")
    def revoke_closure(self, request, pk=None):
        """
        撤销结题申请
        """
        project = self.get_object()

        # 检查权限
        if project.leader != request.user:
            return Response(
                {"code": 403, "message": "只有项目负责人可以撤销申请"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if ProjectService.revoke_closure(project):
            return Response({"code": 200, "message": "结题申请已撤销"})
        else:
            return Response(
                {"code": 400, "message": "项目状态不允许撤销"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(methods=["get"], detail=True)
    def achievements(self, request, pk=None):
        """
        获取项目成果列表
        """
        project = self.get_object()
        achievements = project.achievements.all()
        serializer = ProjectAchievementSerializer(achievements, many=True)
        return Response({"code": 200, "data": serializer.data})

    @action(methods=["post"], detail=True, url_path="add-achievement")
    def add_achievement(self, request, pk=None):
        """
        添加项目成果
        """
        project = self.get_object()

        # 检查权限
        if project.leader != request.user:
            return Response(
                {"code": 403, "message": "只有项目负责人可以添加成果"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # 检查项目状态
        allowed_statuses = [
            Project.ProjectStatus.IN_PROGRESS,
            Project.ProjectStatus.CLOSURE_DRAFT,
            Project.ProjectStatus.CLOSURE_SUBMITTED,
        ]
        if project.status not in allowed_statuses:
            return Response(
                {"code": 400, "message": "当前项目状态不允许添加成果"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ProjectAchievementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(project=project)

        return Response(
            {"code": 200, "message": "成果添加成功", "data": serializer.data}
        )

    @action(
        methods=["delete"],
        detail=True,
        url_path="remove-achievement/(?P<achievement_id>[^/.]+)",
    )
    def remove_achievement(self, request, pk=None, achievement_id=None):
        """
        删除项目成果
        """
        project = self.get_object()

        # 检查权限
        if project.leader != request.user:
            return Response(
                {"code": 403, "message": "只有项目负责人可以删除成果"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            achievement = ProjectAchievement.objects.get(
                project=project, id=achievement_id
            )
            achievement.delete()
            return Response({"code": 200, "message": "成果删除成功"})
        except ProjectAchievement.DoesNotExist:
            return Response(
                {"code": 404, "message": "成果不存在"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(methods=["post"], detail=True, url_path="update-ranking")
    def update_ranking(self, request, pk=None):
        """
        更新项目排名（仅二级管理员）
        """
        project = self.get_object()
        user = request.user

        # 检查权限
        if not user.is_level2_admin or project.leader.college != user.college:
            return Response(
                {"code": 403, "message": "无权限修改此项目排名"},
                status=status.HTTP_403_FORBIDDEN,
            )

        ranking = request.data.get("ranking")
        if ranking is None:
            return Response(
                {"code": 400, "message": "请提供排名"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        project.ranking = ranking
        project.save()

        return Response({"code": 200, "message": "排名更新成功"})

    @action(methods=["get"], detail=False, url_path="export-excel")
    def export_excel(self, request):
        """
        批量导出项目数据为Excel（仅二级管理员）
        """
        user = request.user
        if not user.is_level2_admin:
            return Response(
                {"code": 403, "message": "无权限导出数据"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # 获取本学院的项目
        projects = Project.objects.filter(leader__college=user.college)

        # 应用筛选条件
        status_filter = request.query_params.get("status")
        if status_filter:
            projects = projects.filter(status=status_filter)

        # 创建Excel工作簿
        import openpyxl
        from django.http import HttpResponse

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "项目列表"

        # 写入表头
        headers = [
            "项目编号",
            "项目名称",
            "项目级别",
            "负责人",
            "指导教师",
            "项目类别",
            "研究领域",
            "项目状态",
            "排名",
            "创建时间",
            "提交时间",
        ]
        ws.append(headers)

        # 写入数据
        for project in projects:
            level_label = project.level.label if project.level else ""
            category_label = project.category.label if project.category else ""
            advisor_names = ", ".join(
                [advisor.user.real_name for advisor in project.advisors.all()]
            )
            research_field = project.key_domain_code if project.is_key_field else ""
            ws.append(
                [
                    project.project_no,
                    project.title,
                    level_label,
                    project.leader.real_name,
                    advisor_names,
                    category_label,
                    research_field,
                    project.get_status_display(),
                    project.ranking or "",
                    project.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    (
                        project.submitted_at.strftime("%Y-%m-%d %H:%M:%S")
                        if project.submitted_at
                        else ""
                    ),
                ]
            )

        # 调整列宽
        for column in ws.columns:
            max_length = 0
            column = [cell for cell in column]
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2) * 1.2
            ws.column_dimensions[column[0].column_letter].width = adjusted_width

        # 返回Excel文件
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = (
            f'attachment; filename="projects_{user.college}.xlsx"'
        )
        wb.save(response)
        return response

    @action(methods=["get"], detail=False, url_path="export-attachments")
    def export_attachments(self, request):
        """
        批量下载项目附件为ZIP（仅二级管理员）
        """
        user = request.user
        if not user.is_level2_admin:
            return Response(
                {"code": 403, "message": "无权限下载附件"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # 获取本学院的项目
        projects = Project.objects.filter(leader__college=user.college)

        # 应用筛选条件
        status_filter = request.query_params.get("status")
        if status_filter:
            projects = projects.filter(status=status_filter)

        # 创建ZIP文件
        from io import BytesIO
        import zipfile
        from django.http import HttpResponse

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for project in projects:
                # 添加申报书
                if project.proposal_file:
                    try:
                        file_path = project.proposal_file.path
                        zip_file.write(
                            file_path,
                            f"{project.project_no}/申报书_{project.proposal_file.name.split('/')[-1]}",
                        )
                    except Exception as e:
                        pass

                # 添加中期报告
                if project.mid_term_report:
                    try:
                        file_path = project.mid_term_report.path
                        zip_file.write(
                            file_path,
                            f"{project.project_no}/中期报告_{project.mid_term_report.name.split('/')[-1]}",
                        )
                    except Exception:
                        pass

                # 添加结题报告
                if project.final_report:
                    try:
                        file_path = project.final_report.path
                        zip_file.write(
                            file_path,
                            f"{project.project_no}/结题报告_{project.final_report.name.split('/')[-1]}",
                        )
                    except Exception as e:
                        pass

                # 添加成果附件
                for achievement in project.achievements.all():
                    if achievement.attachment:
                        try:
                            file_path = achievement.attachment.path
                            zip_file.write(
                                file_path,
                                f"{project.project_no}/成果_{achievement.title}_{achievement.attachment.name.split('/')[-1]}",
                            )
                        except Exception as e:
                            pass

        # 返回ZIP文件
        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer.read(), content_type="application/zip")
        response["Content-Disposition"] = (
            f'attachment; filename="attachments_{user.college}.zip"'
        )
        return response

