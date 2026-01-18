"""
项目经费视图
"""

from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action

from ...models import Project, ProjectExpenditure
from ...serializers import (
    ProjectExpenditureSerializer,
    ProjectExpenditureReviewActionSerializer,
)
from ...services import ProjectService
from ...services.expenditure_workflow_service import ExpenditureWorkflowService
from apps.system_settings.services import SystemSettingService


class ProjectExpenditureViewSet(viewsets.ModelViewSet):
    """
    项目经费视图集
    """

    queryset = ProjectExpenditure.objects.all()
    serializer_class = ProjectExpenditureSerializer
    permission_classes = [IsAuthenticated]

    filterset_fields = ["project"]

    def _can_manage_expenditure(self, user, project):
        if user.is_admin:
            return True
        if user.is_student:
            return (
                project.leader_id == user.id
                or project.members.filter(id=user.id).exists()
            )
        if user.is_teacher:
            return project.advisors.filter(user=user).exists()
        return False

    def _ensure_project_status(self, project):
        allowed_statuses = {
            Project.ProjectStatus.IN_PROGRESS,
            Project.ProjectStatus.MID_TERM_DRAFT,
            Project.ProjectStatus.MID_TERM_SUBMITTED,
            Project.ProjectStatus.MID_TERM_REVIEWING,
            Project.ProjectStatus.READY_FOR_CLOSURE,
            Project.ProjectStatus.MID_TERM_REJECTED,
            Project.ProjectStatus.MID_TERM_RETURNED,
            Project.ProjectStatus.CLOSURE_DRAFT,
            Project.ProjectStatus.CLOSURE_SUBMITTED,
            Project.ProjectStatus.CLOSURE_LEVEL2_REVIEWING,
            Project.ProjectStatus.CLOSURE_LEVEL2_APPROVED,
            Project.ProjectStatus.CLOSURE_LEVEL2_REJECTED,
            Project.ProjectStatus.CLOSURE_LEVEL1_REVIEWING,
            Project.ProjectStatus.CLOSURE_LEVEL1_APPROVED,
            Project.ProjectStatus.CLOSURE_LEVEL1_REJECTED,
            Project.ProjectStatus.CLOSURE_RETURNED,
        }
        return project.status in allowed_statuses

    def perform_create(self, serializer):
        project = serializer.validated_data["project"]
        amount = serializer.validated_data["amount"]
        current_batch = SystemSettingService.get_current_batch()
        if not current_batch or project.batch_id != current_batch.id:
            raise serializers.ValidationError("当前批次不允许操作该项目经费")

        if not self._can_manage_expenditure(self.request.user, project):
            raise PermissionDenied("无权限录入该项目经费")

        if not self._ensure_project_status(project):
            raise serializers.ValidationError("当前项目状态不允许录入经费")

        # 验证余额
        stats = ProjectService.get_budget_stats(project)
        if amount > stats["remaining_amount"]:
            raise serializers.ValidationError(
                f"余额不足！当前剩余经费：{stats['remaining_amount']}元，本次申请：{amount}元"
            )

        serializer.save(created_by=self.request.user)

    def list(self, request, *args, **kwargs):
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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        project = serializer.validated_data["project"]
        amount = serializer.validated_data["amount"]

        current_batch = SystemSettingService.get_current_batch()
        if not current_batch or project.batch_id != current_batch.id:
            raise serializers.ValidationError("当前批次不允许操作该项目经费")

        if not self._can_manage_expenditure(request.user, project):
            raise PermissionDenied("无权限录入该项目经费")

        if not self._ensure_project_status(project):
            raise serializers.ValidationError("当前项目状态不允许录入经费")

        stats = ProjectService.get_budget_stats(project)
        if amount > stats["remaining_amount"]:
            raise serializers.ValidationError(
                f"余额不足！当前剩余经费：{stats['remaining_amount']}元，本次申请：{amount}元"
            )

        try:
            expenditure = ProjectExpenditure.objects.create(
                project=project,
                title=serializer.validated_data["title"],
                amount=amount,
                expenditure_date=serializer.validated_data["expenditure_date"],
                proof_file=serializer.validated_data.get("proof_file"),
                status=ProjectExpenditure.ExpenditureStatus.PENDING,
                created_by=request.user,
                leader_review_status=ProjectExpenditure.LeaderReviewStatus.PENDING
                if project.leader_id != request.user.id
                else ProjectExpenditure.LeaderReviewStatus.SKIPPED,
            )
        except ValueError as e:
            return Response(
                {"code": 400, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            expenditure.leader_review_status
            == ProjectExpenditure.LeaderReviewStatus.SKIPPED
        ):
            ExpenditureWorkflowService.start_workflow(expenditure)

        output = self.get_serializer(expenditure)
        return Response(output.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        user = self.request.user
        current_batch = SystemSettingService.get_current_batch()
        if not current_batch:
            return ProjectExpenditure.objects.none()
        base_queryset = ProjectExpenditure.objects.select_related(
            "project", "project__leader"
        ).prefetch_related(
            "reviews",
            "reviews__workflow_node",
            "reviews__workflow_node__role_fk",
        )

        if hasattr(user, "is_student") and user.is_student:
            from django.db.models import Q

            queryset = base_queryset.filter(
                Q(project__leader=user) | Q(project__members=user),
                project__batch=current_batch,
            ).distinct()
        elif user.is_admin:
            if not user.is_level1_admin:
                queryset = base_queryset.filter(
                    project__leader__college=user.college, project__batch=current_batch
                )
            else:
                queryset = base_queryset.filter(project__batch=current_batch)
        elif user.is_teacher:
            queryset = base_queryset.filter(
                project__advisors__user=user, project__batch=current_batch
            ).distinct()
        else:
            queryset = base_queryset.filter(project__batch=current_batch)

        review_scope = self.request.query_params.get("review_scope")
        if review_scope and str(review_scope).lower() in ("self", "me", "pending"):
            pending_ids = []
            for expenditure in queryset:
                pending = ExpenditureWorkflowService.get_pending_review_for_user(
                    expenditure, user
                )
                if pending and pending.get("type") == "NODE":
                    pending_ids.append(expenditure.id)
            if not pending_ids:
                return queryset.none()
            return queryset.filter(id__in=pending_ids)

        return queryset

    @action(detail=True, methods=["post"], url_path="leader-review")
    def leader_review(self, request, pk=None):
        expenditure = self.get_object()
        if expenditure.project.leader_id != request.user.id:
            return Response(
                {"code": 403, "message": "只有负责人可以审核"},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = ProjectExpenditureReviewActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        action_type = serializer.validated_data["action"]
        comments = serializer.validated_data.get("comments", "")
        try:
            ExpenditureWorkflowService.apply_leader_review(
                expenditure, request.user, action_type == "approve", comments
            )
        except ValueError as exc:
            return Response(
                {"code": 400, "message": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"code": 200, "message": "审核成功"})

    @action(detail=True, methods=["post"], url_path="review")
    def review(self, request, pk=None):
        expenditure = self.get_object()
        pending = ExpenditureWorkflowService.get_pending_review_for_user(
            expenditure, request.user
        )
        if not pending or pending.get("type") != "NODE":
            return Response(
                {"code": 403, "message": "无权限审核或已审核"},
                status=status.HTTP_403_FORBIDDEN,
            )

        review = pending.get("review")
        serializer = ProjectExpenditureReviewActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        action_type = serializer.validated_data["action"]
        comments = serializer.validated_data.get("comments", "")

        try:
            if action_type == "approve":
                ExpenditureWorkflowService.approve_review(review, request.user, comments)
            else:
                ExpenditureWorkflowService.reject_review(review, request.user, comments)
        except ValueError as exc:
            return Response(
                {"code": 400, "message": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"code": 200, "message": "审核成功"})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        project = instance.project
        if request.user.is_student and project.leader_id != request.user.id:
            return Response(
                {"code": 403, "message": "成员无权删除经费记录"},
                status=status.HTTP_403_FORBIDDEN,
            )
        self.perform_destroy(instance)
        return Response({"code": 200, "message": "删除成功"})
