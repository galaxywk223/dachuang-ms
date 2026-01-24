"""
项目成果视图
"""

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from ...models import Project, ProjectAchievement
from ...serializers import ProjectAchievementSerializer


class ProjectAchievementViewSet(viewsets.ModelViewSet):
    """
    项目成果视图集
    """

    queryset = ProjectAchievement.objects.all()
    serializer_class = ProjectAchievementSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["project", "achievement_type"]
    ordering_fields = ["created_at"]

    def _can_write(self, user, project):
        if getattr(user, "is_admin", False):
            return True
        if getattr(user, "is_student", False) and project.leader_id == user.id:
            return True
        return False

    def get_queryset(self):
        """
        根据用户角色过滤成果
        """
        from django.db.models import Q

        user = self.request.user
        queryset = super().get_queryset()

        # 学生只能看到自己参与项目的成果
        if user.is_student:
            queryset = queryset.filter(
                Q(project__leader=user) | Q(project__members=user)
            ).distinct()
        # 非校级管理员只能看到本学院项目的成果
        elif user.is_admin and not user.is_level1_admin:
            queryset = queryset.filter(project__leader__college=user.college)

        return queryset

    def create(self, request, *args, **kwargs):
        project_id = request.data.get("project")
        if project_id:
            project = Project.objects.filter(id=project_id).only("id", "leader_id").first()
            if project and not self._can_write(request.user, project):
                raise PermissionDenied("只有项目负责人可以操作项目成果")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if not self._can_write(request.user, instance.project):
            raise PermissionDenied("只有项目负责人可以操作项目成果")
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if not self._can_write(request.user, instance.project):
            raise PermissionDenied("只有项目负责人可以操作项目成果")
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not self._can_write(request.user, instance.project):
            raise PermissionDenied("只有项目负责人可以操作项目成果")
        self.perform_destroy(instance)
        return Response({"code": 200, "message": "删除成功"}, status=status.HTTP_200_OK)
