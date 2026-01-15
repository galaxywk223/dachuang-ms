"""
Endpoints for the current user's own projects.
"""

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from ...models import Project
from ...serializers import ProjectSerializer


class ProjectSelfMixin:
    @action(detail=False, methods=["get"], url_path="my-projects")
    def my_projects(self, request):
        """
        获取我的项目列表（支持分页和筛选）
        """
        user = request.user

        title = request.query_params.get("title")
        level = request.query_params.get("level")
        category = request.query_params.get("category")
        status_filter = request.query_params.get("status")

        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))

        from django.db.models import Q

        projects = Project.objects.filter(Q(leader=user) | Q(members=user)).distinct()

        if title:
            projects = projects.filter(title__icontains=title)
        if level:
            projects = projects.filter(level=level)
        if category:
            projects = projects.filter(category=category)
        if status_filter:
            projects = projects.filter(status=status_filter)

        projects = projects.order_by("-created_at")

        total = projects.count()
        start = (page - 1) * page_size
        end = start + page_size
        projects = projects[start:end]

        serializer = ProjectSerializer(projects, many=True)
        return Response(
            {
                "code": 200,
                "message": "获取成功",
                "data": serializer.data,
                "total": total,
                "page": page,
                "page_size": page_size,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="my-drafts")
    def my_drafts(self, request):
        """
        获取我的草稿箱（支持分页和筛选）
        """
        user = request.user

        title = request.query_params.get("title")

        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))

        drafts = Project.objects.filter(leader=user, status=Project.ProjectStatus.DRAFT)

        if title:
            drafts = drafts.filter(title__icontains=title)

        drafts = drafts.order_by("-updated_at")

        total = drafts.count()
        start = (page - 1) * page_size
        end = start + page_size
        drafts = drafts[start:end]

        serializer = ProjectSerializer(drafts, many=True)
        return Response(
            {
                "code": 200,
                "message": "获取成功",
                "data": serializer.data,
                "total": total,
                "page": page,
                "page_size": page_size,
            },
            status=status.HTTP_200_OK,
        )
