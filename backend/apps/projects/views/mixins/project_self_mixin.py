"""
Endpoints for the current user's own projects.
"""

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from ...models import Project
from apps.system_settings.services import SystemSettingService
from apps.utils.pagination import optional_positive_int, positive_int_query
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

        page = positive_int_query(request.query_params, "page", 1)
        page_size = positive_int_query(request.query_params, "page_size", 10, 100)

        from django.db.models import Q

        include_archived = request.query_params.get("include_archived")
        include_archived = str(include_archived).lower() in ("true", "1", "yes")

        projects = Project.objects.filter(Q(leader=user) | Q(members=user)).distinct()
        projects = projects.filter(batch__is_deleted=False)
        if not include_archived:
            current_batch = SystemSettingService.get_current_batch()
            if not current_batch:
                return Response(
                    {"code": 200, "message": "获取成功", "data": [], "total": 0},
                    status=status.HTTP_200_OK,
                )
            projects = projects.filter(batch=current_batch)

        if title:
            projects = projects.filter(title__icontains=title)
        if level:
            parsed_level = optional_positive_int(level)
            if parsed_level is None:
                projects = projects.none()
            else:
                projects = projects.filter(level_id=parsed_level)
        if category:
            parsed_category = optional_positive_int(category)
            if parsed_category is None:
                projects = projects.none()
            else:
                projects = projects.filter(category_id=parsed_category)
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

        page = positive_int_query(request.query_params, "page", 1)
        page_size = positive_int_query(request.query_params, "page_size", 10, 100)

        current_batch = SystemSettingService.get_current_batch()
        if not current_batch:
            return Response(
                {"code": 200, "message": "获取成功", "data": [], "total": 0},
                status=status.HTTP_200_OK,
            )

        drafts = Project.objects.filter(
            leader=user, status=Project.ProjectStatus.DRAFT, batch=current_batch
        )

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
