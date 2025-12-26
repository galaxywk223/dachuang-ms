"""
项目管理相关视图（管理员）
"""

from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ...models import Project
from ...serializers import ProjectSerializer
from ..mixins.batch_mixin import ProjectBatchMixin
from ..mixins.export_mixin import ProjectExportMixin


class ProjectManagementViewSet(
    ProjectExportMixin, ProjectBatchMixin, viewsets.ModelViewSet
):
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

        # 权限控制：二级管理员只能看到本学院的项目
        user = self.request.user
        if user.is_level2_admin:
            queryset = queryset.filter(leader__college=user.college)
        elif not user.is_level1_admin:
            return Project.objects.none()

        # 搜索
        search = self.request.query_params.get("search", "")
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(project_no__icontains=search)
                | Q(leader__real_name__icontains=search)
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

        batch_id = self.request.query_params.get("batch_id", "")
        if batch_id:
            queryset = queryset.filter(batch_id=batch_id)

        year = self.request.query_params.get("year", "")
        if year:
            queryset = queryset.filter(year=year)

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
        from django.db import transaction
        import json
        from ...models import ProjectAdvisor, ProjectMember
        from apps.users.models import User
        import logging

        logger = logging.getLogger(__name__)

        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        # Extract nested data
        advisors_data = request.data.get("advisors")
        members_data = request.data.get("members")

        with transaction.atomic():
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            if not serializer.is_valid():
                # Debug: 打印本次更新请求的数据与校验错误，方便前后端联调
                logger.warning(
                    "Project admin manage update validation failed: project_id=%s user_id=%s partial=%s data=%s errors=%s",
                    instance.id,
                    getattr(request.user, "id", None),
                    partial,
                    dict(request.data),
                    serializer.errors,
                )
                return Response(
                    {"code": 400, "message": "数据验证失败", "errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            self.perform_update(serializer)

            # Update Advisors if provided
            if advisors_data is not None:
                if isinstance(advisors_data, str):
                    try:
                        advisors_data = json.loads(advisors_data)
                    except json.JSONDecodeError:
                        advisors_data = []

                # Clear existing advisors
                instance.advisors.all().delete()

                for idx, advisor_data in enumerate(advisors_data):
                    user_id = (
                        advisor_data.get("user")
                        or advisor_data.get("user_id")
                        or advisor_data.get("id")
                    )
                    job_number = advisor_data.get("job_number") or advisor_data.get(
                        "employee_id"
                    )

                    # Try to find user if no ID
                    if not user_id and job_number:
                        u = User.objects.filter(employee_id=job_number).first()
                        if u:
                            user_id = u.id

                    if user_id:
                        ProjectAdvisor.objects.create(
                            project=instance,
                            user_id=user_id,
                            order=idx,
                        )

            # Update Members if provided
            if members_data is not None:
                if isinstance(members_data, str):
                    try:
                        members_data = json.loads(members_data)
                    except json.JSONDecodeError:
                        members_data = []

                # Clear existing members (except leader)
                ProjectMember.objects.filter(project=instance).exclude(
                    role=ProjectMember.MemberRole.LEADER
                ).delete()

                for idx, member_data in enumerate(members_data):
                    user_id = member_data.get("user") or member_data.get("user_id")
                    student_id = member_data.get("student_id") or member_data.get(
                        "employee_id"
                    )

                    if not user_id and student_id:
                        u = User.objects.filter(employee_id=student_id).first()
                        if u:
                            user_id = u.id

                    if user_id:
                        ProjectMember.objects.create(
                            project=instance,
                            user_id=user_id,
                            role=ProjectMember.MemberRole.MEMBER,
                            order=idx,
                            contribution=member_data.get("contribution", ""),
                        )

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
        # 基础查询集（已包含权限过滤）
        base_queryset = self.get_queryset()

        total_projects = base_queryset.count()
        approved_projects = base_queryset.filter(
            status__in=["IN_PROGRESS", "COMPLETED"]
        ).count()
        pending_review = base_queryset.filter(
            status__in=[
                "SUBMITTED",
                "TEACHER_AUDITING",
                "COLLEGE_AUDITING",
                "LEVEL1_AUDITING",
                "MID_TERM_SUBMITTED",
                "MID_TERM_REVIEWING",
                "CLOSURE_SUBMITTED",
                "CLOSURE_LEVEL2_REVIEWING",
                "CLOSURE_LEVEL1_REVIEWING",
            ]
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
