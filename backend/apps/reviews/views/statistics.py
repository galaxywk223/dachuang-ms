"""
审核统计相关视图
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.projects.models import Project, ProjectChangeRequest
from apps.users.models import User


class ReviewStatisticsViewSet(viewsets.ViewSet):
    """
    审核统计视图集
    """

    permission_classes = [IsAuthenticated]

    @action(methods=["get"], detail=False, url_path="pending-counts")
    def pending_counts(self, request):
        """
        获取各类审核的待审核数量
        """
        user = request.user

        # 验证用户是管理员
        if not (user.is_level1_admin or user.is_level2_admin):
            return Response(
                {"code": 403, "message": "无权限访问"},
                status=status.HTTP_403_FORBIDDEN,
            )

        result = {
            "establishment": 0,  # 立项审核
            "midterm": 0,  # 中期审核（仅level2）
            "closure": 0,  # 结题审核
            "change": 0,  # 异动审核
        }

        # 立项审核待审数量
        if user.is_level1_admin:
            establishment_status = [Project.ProjectStatus.LEVEL1_AUDITING]
        else:  # level2_admin
            establishment_status = [Project.ProjectStatus.COLLEGE_AUDITING]

        establishment_queryset = Project.objects.filter(status__in=establishment_status)
        if user.is_level2_admin and user.college:
            establishment_queryset = establishment_queryset.filter(
                leader__college=user.college
            )
        result["establishment"] = establishment_queryset.count()

        # 中期审核待审数量（仅level2）
        if user.is_level2_admin:
            midterm_queryset = Project.objects.filter(
                status=Project.ProjectStatus.MID_TERM_REVIEWING
            )
            if user.college:
                midterm_queryset = midterm_queryset.filter(leader__college=user.college)
            result["midterm"] = midterm_queryset.count()

        # 结题审核待审数量
        if user.is_level1_admin:
            closure_status = [Project.ProjectStatus.CLOSURE_LEVEL1_REVIEWING]
        else:  # level2_admin
            closure_status = [Project.ProjectStatus.CLOSURE_LEVEL2_REVIEWING]

        closure_queryset = Project.objects.filter(status__in=closure_status)
        if user.is_level2_admin and user.college:
            closure_queryset = closure_queryset.filter(leader__college=user.college)
        result["closure"] = closure_queryset.count()

        # 异动审核待审数量
        if user.is_level1_admin:
            change_status = "LEVEL1_REVIEWING"
        else:  # level2_admin
            change_status = "LEVEL2_REVIEWING"

        change_queryset = ProjectChangeRequest.objects.filter(status=change_status)
        if user.is_level2_admin and user.college:
            change_queryset = change_queryset.filter(
                project__leader__college=user.college
            )
        result["change"] = change_queryset.count()

        return Response({"code": 200, "message": "获取成功", "data": result})
