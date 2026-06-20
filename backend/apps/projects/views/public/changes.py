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
from apps.system_settings.services import AdminAssignmentService, SystemSettingService
from apps.utils.downloads import file_field_download_response
from apps.utils.pagination import optional_positive_int


def _has_school_admin_scope(user):
    return user.is_school_admin or user.is_level1_admin


class ProjectChangeRequestViewSet(viewsets.ModelViewSet):
    """
    项目异动申请管理
    """

    queryset = ProjectChangeRequest.objects.all()
    serializer_class = ProjectChangeRequestSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["status", "request_type"]

    def _validate_project_write_target(self, request):
        project_id = request.data.get("project")
        if project_id in (None, ""):
            return None

        project_id = optional_positive_int(project_id)
        if project_id is None:
            return Response(
                {"code": 400, "message": "项目ID不合法"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        current_batch = SystemSettingService.get_current_batch()
        if not current_batch:
            return Response(
                {"code": 400, "message": "当前没有可用批次"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            project = Project.objects.get(id=project_id, batch=current_batch)
        except Project.DoesNotExist:
            return Response(
                {"code": 404, "message": "项目不存在"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if project.leader_id != request.user.id:
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
        return None

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        current_batch = SystemSettingService.get_current_batch()
        if not current_batch:
            return queryset.none()
        queryset = queryset.filter(project__batch=current_batch)
        teacher_scope = self.request.query_params.get("teacher_scope")

        if user.is_student:
            queryset = queryset.filter(created_by=user)
        elif (
            teacher_scope
            and str(teacher_scope).lower() in ("true", "1", "yes")
            and (user.is_teacher or user.is_admin)
        ):
            queryset = queryset.filter(project__advisors__user=user).distinct()
        elif user.is_admin and not _has_school_admin_scope(user):
            queryset = queryset.filter(project__leader__college=user.college)
        elif _has_school_admin_scope(user):
            pass
        elif user.is_teacher:
            queryset = queryset.filter(project__advisors__user=user).distinct()
        else:
            queryset = queryset.none()

        project_id = self.request.query_params.get("project")
        if project_id:
            parsed_project_id = optional_positive_int(project_id)
            if parsed_project_id is None:
                return queryset.none()
            queryset = queryset.filter(project_id=parsed_project_id)

        return queryset

    @action(methods=["get"], detail=True)
    def download(self, request, pk=None):
        change_request = self.get_object()
        if not change_request.attachment:
            return Response(
                {"code": 404, "message": "异动附件不存在"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return file_field_download_response(
            change_request.attachment,
            missing_message="异动附件不存在",
        )

    def create(self, request, *args, **kwargs):
        project_id = request.data.get("project")
        if not project_id:
            return Response(
                {"code": 400, "message": "请指定项目"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        response = self._validate_project_write_target(request)
        if response is not None:
            return response

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
        response = self._validate_project_write_target(request)
        if response is not None:
            return response
        serializer = self.get_serializer(
            instance, data=request.data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"code": 200, "message": "更新成功", "data": serializer.data})

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

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

        phase = "CHANGE"
        project = change_request.project

        for review in pending_reviews:
            node = review.workflow_node
            if not node:
                continue
            try:
                expected_status = ProjectChangeService._status_for_workflow_node(node)
            except ValueError:
                continue
            if change_request.status != expected_status:
                continue
            role_code = node.get_role_code()
            if role_code == "TEACHER":
                if (user.is_teacher or user.is_admin) and project.advisors.filter(
                    user=user
                ).exists():
                    return review
                continue
            role = node.role_fk
            if role and user.is_active and user.role_fk_id == role.id:
                scope_dimension = role.scope_dimension
                if not scope_dimension or scope_dimension == "SCHOOL":
                    return review
                try:
                    scope_value_id = AdminAssignmentService.get_scope_value_id(
                        project, scope_dimension
                    )
                    scope_value = AdminAssignmentService.get_scope_value(
                        project, scope_dimension
                    )
                except ValueError:
                    pass
                else:
                    if (
                        user.managed_scope_value_id == scope_value_id
                        or user.college == scope_value
                    ):
                        return review
            try:
                admin_user = AdminAssignmentService.resolve_admin_user(
                    project, phase, node
                )
            except ValueError:
                continue
            if admin_user.id == user.id:
                return review
        return None
