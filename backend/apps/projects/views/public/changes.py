"""
项目异动（变更/延期/终止）视图
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ...models import Project, ProjectChangeRequest, ProjectChangeReview
from ...serializers import (
    ProjectChangeRequestSerializer,
    ProjectChangeReviewActionSerializer,
)
from ...services import ProjectChangeService
from apps.notifications.services import NotificationService
from apps.system_settings.services import AdminAssignmentService


class ProjectChangeRequestViewSet(viewsets.ModelViewSet):
    """
    项目异动申请管理
    """

    queryset = ProjectChangeRequest.objects.all()
    serializer_class = ProjectChangeRequestSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["status", "request_type", "project"]

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        teacher_scope = self.request.query_params.get("teacher_scope")

        if user.is_student:
            return queryset.filter(created_by=user)
        if (
            teacher_scope
            and str(teacher_scope).lower() in ("true", "1", "yes")
            and (user.is_teacher or user.is_admin)
        ):
            return queryset.filter(project__advisors__user=user).distinct()
        if user.is_admin and not user.is_level1_admin:
            return queryset.filter(project__leader__college=user.college)
        if user.is_level1_admin:
            return queryset
        if user.is_teacher:
            return queryset.filter(project__advisors__user=user).distinct()
        return queryset.none()

    def create(self, request, *args, **kwargs):
        project_id = request.data.get("project")
        if not project_id:
            return Response(
                {"code": 400, "message": "请指定项目"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response(
                {"code": 404, "message": "项目不存在"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if project.leader != request.user:
            return Response(
                {"code": 403, "message": "只有项目负责人可以提交异动申请"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if project.status in [
            Project.ProjectStatus.CLOSED,
            Project.ProjectStatus.COMPLETED,
            Project.ProjectStatus.TERMINATED,
        ]:
            return Response(
                {"code": 400, "message": "项目已结题或终止，无法申请异动"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save(created_by=request.user)
        return Response(
            {"code": 200, "message": "创建成功", "data": serializer.data},
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.created_by != request.user:
            return Response(
                {"code": 403, "message": "无权限修改"},
                status=status.HTTP_403_FORBIDDEN,
            )
        if instance.status != ProjectChangeRequest.ChangeStatus.DRAFT:
            return Response(
                {"code": 400, "message": "只有草稿状态可修改"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(
            instance, data=request.data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"code": 200, "message": "更新成功", "data": serializer.data})

    @action(methods=["post"], detail=True)
    def submit(self, request, pk=None):
        change_request = self.get_object()
        if change_request.created_by != request.user:
            return Response(
                {"code": 403, "message": "无权限提交"},
                status=status.HTTP_403_FORBIDDEN,
            )
        if change_request.status != ProjectChangeRequest.ChangeStatus.DRAFT:
            return Response(
                {"code": 400, "message": "当前状态不允许提交"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if (
            change_request.request_type == ProjectChangeRequest.ChangeType.EXTENSION
            and not change_request.requested_end_date
        ):
            return Response(
                {"code": 400, "message": "延期申请必须填写延期日期"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            ProjectChangeService.submit_request(change_request)
        except ValueError as exc:
            return Response(
                {"code": 400, "message": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"code": 200, "message": "提交成功"})

    @action(methods=["post"], detail=True)
    def review(self, request, pk=None):
        change_request = self.get_object()
        user = request.user

        review = self._get_pending_review(change_request, user)
        if not review:
            return Response(
                {"code": 403, "message": "无权限审核或已审核"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ProjectChangeReviewActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        action_type = serializer.validated_data["action"]
        comments = serializer.validated_data.get("comments", "")

        try:
            if action_type == "approve":
                ProjectChangeService.approve_review(review, user, comments)
                NotificationService.notify_review_result(
                    change_request.project, True, comments
                )
                return Response({"code": 200, "message": "审核通过"})

            ProjectChangeService.reject_review(review, user, comments)
        except ValueError as exc:
            return Response(
                {"code": 400, "message": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        NotificationService.notify_review_result(change_request.project, False, comments)
        return Response({"code": 200, "message": "已驳回"})

    def _get_pending_review(self, change_request, user):
        pending_reviews = (
            ProjectChangeReview.objects.filter(
                change_request=change_request,
                status=ProjectChangeReview.ReviewStatus.PENDING,
            )
            .select_related("workflow_node", "workflow_node__role_fk")
            .order_by("id")
        )
        if not pending_reviews.exists():
            return None

        phase = ProjectChangeService._resolve_phase(change_request)
        project = change_request.project

        for review in pending_reviews:
            node = review.workflow_node
            if not node:
                continue
            role_code = node.get_role_code()
            if role_code == "TEACHER":
                if (user.is_teacher or user.is_admin) and project.advisors.filter(
                    user=user
                ).exists():
                    return review
                continue
            try:
                admin_user = AdminAssignmentService.resolve_admin_user(
                    project, phase, node
                )
            except ValueError:
                continue
            if admin_user.id == user.id:
                return review
        return None
