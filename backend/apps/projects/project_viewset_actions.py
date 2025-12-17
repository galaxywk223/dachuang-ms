"""
ProjectViewSet action mixins (keep views.py small).
"""

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone

from .models import Project, ProjectMember, ProjectProgress, ProjectAchievement
from .serializers import (
    ProjectMemberSerializer,
    ProjectProgressSerializer,
    ProjectAchievementSerializer,
    ProjectClosureSerializer,
)
from .services import ProjectService
from apps.reviews.services import ReviewService


class ProjectMemberActionsMixin:
    permission_classes = [IsAuthenticated]

    @action(methods=["post"], detail=True)
    def submit(self, request, pk=None):
        """
        提交项目申报
        """
        project = self.get_object()

        if project.leader != request.user:
            return Response(
                {"code": 403, "message": "只有项目负责人可以提交项目"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if project.status != Project.ProjectStatus.DRAFT:
            return Response(
                {"code": 400, "message": "项目状态不允许提交"},
                status=status.HTTP_400_BAD_REQUEST,
            )

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

            if ProjectMember.objects.filter(project=project, user=user).exists():
                return Response(
                    {"code": 400, "message": "该用户已是项目成员"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

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

    @action(methods=["delete"], detail=True, url_path="remove-member/(?P<member_id>[^/.]+)")
    def remove_member(self, request, pk=None, member_id=None):
        """
        移除项目成员
        """
        project = self.get_object()

        if project.leader != request.user:
            return Response(
                {"code": 403, "message": "只有项目负责人可以移除成员"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            member = ProjectMember.objects.get(project=project, id=member_id)

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


class ProjectProgressActionsMixin:
    permission_classes = [IsAuthenticated]

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

        if not ProjectMember.objects.filter(project=project, user=request.user).exists():
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


class ProjectClosureActionsMixin:
    permission_classes = [IsAuthenticated]

    @action(methods=["post"], detail=True, url_path="apply-closure")
    def apply_closure(self, request, pk=None):
        """
        申请项目结题
        """
        project = self.get_object()

        if project.leader != request.user:
            return Response(
                {"code": 403, "message": "只有项目负责人可以申请结题"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ProjectClosureSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        is_draft = serializer.validated_data.get("is_draft", False)
        final_report = serializer.validated_data.get("final_report")

        try:
            ProjectService.apply_closure(project, final_report, is_draft)
            message = "结题申请已保存为草稿" if is_draft else "结题申请提交成功"
            return Response({"code": 200, "message": message})
        except ValueError as e:
            return Response(
                {"code": 400, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(methods=["post"], detail=True, url_path="submit-closure")
    def submit_closure(self, request, pk=None):
        """
        提交结题申请（从草稿状态）
        """
        project = self.get_object()

        if project.leader != request.user:
            return Response(
                {"code": 403, "message": "只有项目负责人可以提交结题"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            if ProjectService.submit_closure(project):
                ReviewService.create_closure_level2_review(project)
                return Response({"code": 200, "message": "结题申请提交成功"})
            return Response(
                {"code": 400, "message": "项目状态不允许提交"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ValueError as e:
            return Response(
                {"code": 400, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(methods=["post"], detail=True, url_path="revoke-closure")
    def revoke_closure(self, request, pk=None):
        """
        撤销结题申请
        """
        project = self.get_object()

        if project.leader != request.user:
            return Response(
                {"code": 403, "message": "只有项目负责人可以撤销申请"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if ProjectService.revoke_closure(project):
            return Response({"code": 200, "message": "结题申请已撤销"})
        return Response(
            {"code": 400, "message": "项目状态不允许撤销"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class ProjectAchievementActionsMixin:
    permission_classes = [IsAuthenticated]

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

        return Response(
            {"code": 200, "message": "成果添加成功", "data": serializer.data}
        )

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
                {"code": 404, "message": "成果不存在"}, status=status.HTTP_404_NOT_FOUND
            )


class ProjectRankingActionsMixin:
    permission_classes = [IsAuthenticated]

    @action(methods=["post"], detail=True, url_path="update-ranking")
    def update_ranking(self, request, pk=None):
        """
        更新项目排名（仅二级管理员）
        """
        project = self.get_object()
        user = request.user

        if not user.is_level2_admin or project.leader.college != user.college:
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

