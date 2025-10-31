"""
项目管理相关视图（管理员）
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from .models import Project
from .serializers import ProjectSerializer


class ProjectManagementViewSet(viewsets.ModelViewSet):
    """
    项目管理视图集（管理员）
    """

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        获取项目列表，支持筛选
        """
        queryset = Project.objects.all().order_by("-created_at")

        # 搜索
        search = self.request.query_params.get("search", "")
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(project_no__icontains=search)
                | Q(leader_name__icontains=search)
            )

        # 按级别筛选
        level = self.request.query_params.get("level", "")
        if level:
            queryset = queryset.filter(level=level)

        # 按类别筛选
        category = self.request.query_params.get("category", "")
        if category:
            queryset = queryset.filter(category=category)

        # 按状态筛选
        project_status = self.request.query_params.get("status", "")
        if project_status:
            queryset = queryset.filter(status=project_status)

        return queryset

    def list(self, request, *args, **kwargs):
        """
        获取项目列表（分页）
        """
        queryset = self.get_queryset()

        # 分页
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))

        total = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size
        projects = queryset[start:end]

        serializer = self.get_serializer(projects, many=True)

        return Response(
            {
                "code": 200,
                "message": "获取成功",
                "data": {
                    "results": serializer.data,
                    "total": total,
                    "page": page,
                    "page_size": page_size,
                },
            }
        )

    def retrieve(self, request, *args, **kwargs):
        """
        获取项目详情
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"code": 200, "message": "获取成功", "data": serializer.data})

    def update(self, request, *args, **kwargs):
        """
        更新项目信息
        """
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({"code": 200, "message": "更新成功", "data": serializer.data})

    def destroy(self, request, *args, **kwargs):
        """
        删除项目
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"code": 200, "message": "删除成功"})

    @action(methods=["get"], detail=False, url_path="statistics")
    def get_statistics(self, request):
        """
        获取项目统计数据
        """
        total_projects = Project.objects.count()
        approved_projects = Project.objects.filter(
            status__in=["IN_PROGRESS", "COMPLETED"]
        ).count()
        pending_review = Project.objects.filter(
            status__in=["SUBMITTED", "MIDTERM_SUBMITTED", "CLOSURE_SUBMITTED"]
        ).count()

        return Response(
            {
                "code": 200,
                "message": "获取成功",
                "data": {
                    "total_projects": total_projects,
                    "approved_projects": approved_projects,
                    "pending_review": pending_review,
                },
            }
        )
