"""
Project admin actions.
"""

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response


class ProjectRankingMixin:
    @action(methods=["post"], detail=True, url_path="update-ranking")
    def update_ranking(self, request, pk=None):
        """
        更新项目排名（仅管理员）
        """
        project = self.get_object()
        user = request.user

        if not user.is_admin:
            return Response(
                {"code": 403, "message": "无权限修改此项目排名"},
                status=status.HTTP_403_FORBIDDEN,
            )
        if not user.is_level1_admin and project.leader.college != user.college:
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
