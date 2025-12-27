"""
项目成果视图
"""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from ...models import ProjectAchievement
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
        # 二级管理员只能看到本学院项目的成果
        elif user.is_level2_admin:
            queryset = queryset.filter(project__leader__college=user.college)

        return queryset
