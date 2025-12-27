"""
Project achievements actions.
"""

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from ...models import Project
from ...models import ProjectAchievement
from ...serializers import ProjectAchievementSerializer


class ProjectAchievementsMixin:
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

        if project.leader != request.user:
            return Response(
                {"code": 403, "message": "只有项目负责人可以添加成果"},
                status=status.HTTP_403_FORBIDDEN,
            )

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

        return Response({"code": 200, "message": "成果添加成功", "data": serializer.data})

    @action(methods=["delete"], detail=True, url_path="remove-achievement/(?P<achievement_id>[^/.]+)")
    def remove_achievement(self, request, pk=None, achievement_id=None):
        """
        删除项目成果
        """
        project = self.get_object()

        if project.leader != request.user:
            return Response(
                {"code": 403, "message": "只有项目负责人可以删除成果"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            achievement = ProjectAchievement.objects.get(project=project, id=achievement_id)
            achievement.delete()
            return Response({"code": 200, "message": "成果删除成功"})
        except ProjectAchievement.DoesNotExist:
            return Response(
                {"code": 404, "message": "成果不存在"},
                status=status.HTTP_404_NOT_FOUND,
            )

