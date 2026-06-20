"""
项目成果视图
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from ...models import Project, ProjectAchievement
from ...serializers import ProjectAchievementSerializer
from apps.system_settings.services import SystemSettingService
from apps.utils.downloads import file_field_download_response
from apps.utils.pagination import optional_positive_int


def _has_school_admin_scope(user):
    return user.is_school_admin or user.is_level1_admin


class ProjectAchievementViewSet(viewsets.ModelViewSet):
    """
    项目成果视图集
    """

    queryset = ProjectAchievement.objects.all()
    serializer_class = ProjectAchievementSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = []
    ordering_fields = ["created_at"]

    def _can_write(self, user, project):
        if getattr(user, "is_admin", False):
            return True
        if getattr(user, "is_student", False) and project.leader_id == user.id:
            return True
        return False

    def _validate_project_write_target(self, request, message):
        project_id = request.data.get("project")
        if project_id in (None, ""):
            return

        project_id = optional_positive_int(project_id)
        if project_id is None:
            return Response(
                {"code": 400, "message": "项目ID不合法"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        project = (
            self._visible_project_queryset()
            .filter(id=project_id)
            .only("id", "leader_id", "batch_id")
            .first()
        )
        if not project:
            return Response(
                {"code": 404, "message": "项目不存在"},
                status=status.HTTP_404_NOT_FOUND,
            )
        current_batch = SystemSettingService.get_current_batch()
        if not current_batch or project.batch_id != current_batch.id:
            return Response(
                {"code": 400, "message": "当前批次不允许操作该项目成果"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if project and not self._can_write(request.user, project):
            raise PermissionDenied(message)
        return None

    def _visible_project_queryset(self):
        from django.db.models import Q

        user = self.request.user
        queryset = Project.objects.all()
        if user.is_student:
            return queryset.filter(Q(leader=user) | Q(members=user)).distinct()
        if user.is_admin:
            if _has_school_admin_scope(user):
                return queryset
            return queryset.filter(leader__college=user.college)
        if user.is_teacher:
            return queryset.filter(
                Q(advisors__user=user) | Q(reviews__reviewer=user)
            ).distinct()
        return queryset.none()

    def get_queryset(self):
        """
        根据用户角色过滤成果
        """
        from django.db.models import Q

        user = self.request.user
        queryset = super().get_queryset()
        current_batch = SystemSettingService.get_current_batch()
        if not current_batch:
            return queryset.none()
        queryset = queryset.filter(project__batch=current_batch)

        # 学生只能看到自己参与项目的成果
        if user.is_student:
            queryset = queryset.filter(
                Q(project__leader=user) | Q(project__members=user)
            ).distinct()
        # 非校级管理员只能看到本学院项目的成果
        elif user.is_admin and not _has_school_admin_scope(user):
            queryset = queryset.filter(project__leader__college=user.college)
        elif _has_school_admin_scope(user):
            pass
        elif user.is_teacher:
            queryset = queryset.filter(
                Q(project__advisors__user=user) | Q(project__reviews__reviewer=user)
            ).distinct()
        elif getattr(user, "is_expert", False):
            queryset = queryset.filter(project__reviews__reviewer=user).distinct()
        else:
            queryset = queryset.none()

        project_id = self.request.query_params.get("project")
        if project_id:
            parsed_project_id = optional_positive_int(project_id)
            if parsed_project_id is None:
                return queryset.none()
            queryset = queryset.filter(project_id=parsed_project_id)

        achievement_type = self.request.query_params.get("achievement_type")
        if achievement_type:
            parsed_achievement_type = optional_positive_int(achievement_type)
            if parsed_achievement_type is None:
                return queryset.none()
            queryset = queryset.filter(achievement_type_id=parsed_achievement_type)

        return queryset

    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        achievement = self.get_object()
        if not achievement.attachment:
            return Response(
                {"code": 404, "message": "成果附件不存在"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return file_field_download_response(
            achievement.attachment,
            missing_message="成果附件不存在",
        )

    def create(self, request, *args, **kwargs):
        response = self._validate_project_write_target(
            request, "只有项目负责人可以操作项目成果"
        )
        if response is not None:
            return response

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if not self._can_write(request.user, instance.project):
            raise PermissionDenied("只有项目负责人可以操作项目成果")
        response = self._validate_project_write_target(
            request, "只有项目负责人可以操作项目成果"
        )
        if response is not None:
            return response
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if not self._can_write(request.user, instance.project):
            raise PermissionDenied("只有项目负责人可以操作项目成果")
        response = self._validate_project_write_target(
            request, "只有项目负责人可以操作项目成果"
        )
        if response is not None:
            return response
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not self._can_write(request.user, instance.project):
            raise PermissionDenied("只有项目负责人可以操作项目成果")
        self.perform_destroy(instance)
        return Response({"code": 200, "message": "删除成功"}, status=status.HTTP_200_OK)
