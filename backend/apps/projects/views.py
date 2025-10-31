"""
项目视图
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .models import Project, ProjectMember, ProjectProgress
from .serializers import (
    ProjectSerializer,
    ProjectListSerializer,
    ProjectMemberSerializer,
    ProjectProgressSerializer,
    ProjectSubmitSerializer,
)
from .services import ProjectService


class ProjectViewSet(viewsets.ModelViewSet):
    """
    项目管理视图集
    """

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["status", "level", "college", "leader"]
    search_fields = ["project_no", "title", "advisor"]
    ordering_fields = ["created_at", "updated_at", "submitted_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return ProjectListSerializer
        return ProjectSerializer

    def get_queryset(self):
        """
        根据用户角色过滤项目
        """
        user = self.request.user
        queryset = super().get_queryset()

        # 学生只能看到自己参与的项目
        if user.is_student:
            queryset = queryset.filter(
                models.Q(leader=user) | models.Q(members=user)
            ).distinct()
        # 二级管理员只能看到自己学院的项目
        elif user.is_level2_admin:
            queryset = queryset.filter(college=user.college)

        return queryset

    def perform_create(self, serializer):
        """
        创建项目时设置负责人为当前用户
        """
        project = serializer.save(leader=self.request.user)
        # 自动将负责人添加为项目成员
        ProjectMember.objects.create(
            project=project,
            user=self.request.user,
            role=ProjectMember.MemberRole.LEADER,
        )

    @action(methods=["post"], detail=True)
    def submit(self, request, pk=None):
        """
        提交项目申报
        """
        project = self.get_object()

        # 检查权限
        if project.leader != request.user:
            return Response(
                {"code": 403, "message": "只有项目负责人可以提交项目"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # 检查项目状态
        if project.status != Project.ProjectStatus.DRAFT:
            return Response(
                {"code": 400, "message": "项目状态不允许提交"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 更新项目状态
        project.status = Project.ProjectStatus.SUBMITTED
        project.submitted_at = timezone.now()
        project.save()

        return Response({"code": 200, "message": "项目提交成功"})

    @action(methods=["post"], detail=True)
    def add_member(self, request, pk=None):
        """
        添加项目成员
        """
        project = self.get_object()

        # 检查权限
        if project.leader != request.user:
            return Response(
                {"code": 403, "message": "只有项目负责人可以添加成员"},
                status=status.HTTP_403_FORBIDDEN,
            )

        user_id = request.data.get("user_id")
        if not user_id:
            return Response(
                {"code": 400, "message": "请提供用户ID"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            from apps.users.models import User

            user = User.objects.get(id=user_id)

            # 检查是否已是成员
            if ProjectMember.objects.filter(project=project, user=user).exists():
                return Response(
                    {"code": 400, "message": "该用户已是项目成员"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 添加成员
            member = ProjectMember.objects.create(
                project=project, user=user, role=ProjectMember.MemberRole.MEMBER
            )

            serializer = ProjectMemberSerializer(member)
            return Response(
                {"code": 200, "message": "成员添加成功", "data": serializer.data}
            )
        except User.DoesNotExist:
            return Response(
                {"code": 404, "message": "用户不存在"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(
        methods=["delete"], detail=True, url_path="remove-member/(?P<member_id>[^/.]+)"
    )
    def remove_member(self, request, pk=None, member_id=None):
        """
        移除项目成员
        """
        project = self.get_object()

        # 检查权限
        if project.leader != request.user:
            return Response(
                {"code": 403, "message": "只有项目负责人可以移除成员"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            member = ProjectMember.objects.get(project=project, id=member_id)

            # 不能移除负责人
            if member.role == ProjectMember.MemberRole.LEADER:
                return Response(
                    {"code": 400, "message": "不能移除项目负责人"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            member.delete()
            return Response({"code": 200, "message": "成员移除成功"})
        except ProjectMember.DoesNotExist:
            return Response(
                {"code": 404, "message": "成员不存在"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(methods=["get"], detail=True)
    def progress(self, request, pk=None):
        """
        获取项目进度列表
        """
        project = self.get_object()
        progress_list = project.progress_records.all()
        serializer = ProjectProgressSerializer(progress_list, many=True)
        return Response({"code": 200, "data": serializer.data})

    @action(methods=["post"], detail=True, url_path="add-progress")
    def add_progress(self, request, pk=None):
        """
        添加项目进度
        """
        project = self.get_object()

        # 检查是否是项目成员
        if not ProjectMember.objects.filter(
            project=project, user=request.user
        ).exists():
            return Response(
                {"code": 403, "message": "只有项目成员可以添加进度"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ProjectProgressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(project=project, created_by=request.user)

        return Response(
            {"code": 200, "message": "进度添加成功", "data": serializer.data}
        )


class ProjectProgressViewSet(viewsets.ReadOnlyModelViewSet):
    """
    项目进度视图集（只读）
    """

    queryset = ProjectProgress.objects.all()
    serializer_class = ProjectProgressSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["project"]
    ordering_fields = ["created_at"]
