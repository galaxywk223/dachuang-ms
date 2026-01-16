"""
项目成果视图
"""

from rest_framework import viewsets
from rest_framework.response import Response
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
        # 非校级管理员只能看到本学院项目的成果
        elif user.is_admin and not user.is_level1_admin:
            queryset = queryset.filter(project__leader__college=user.college)

        return queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        project = instance.project
        payload = {
            "achievement_type": instance.achievement_type_id,
            "title": instance.title,
            "description": instance.description,
            "authors": instance.authors,
            "journal": instance.journal,
            "publication_date": instance.publication_date,
            "doi": instance.doi,
            "patent_no": instance.patent_no,
            "patent_type": instance.patent_type,
            "applicant": instance.applicant,
            "copyright_no": instance.copyright_no,
            "copyright_owner": instance.copyright_owner,
            "competition_name": instance.competition_name,
            "award_level": instance.award_level,
            "award_date": instance.award_date,
            "extra_data": instance.extra_data,
            "attachment": instance.attachment.name if instance.attachment else "",
        }
        self.perform_destroy(instance)
        return Response({"code": 200, "message": "删除成功"})
