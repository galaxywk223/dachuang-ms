"""
Project member actions (add/remove members).
"""

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.users.models import User

from ...models import ProjectMember
from ...serializers import ProjectMemberSerializer


class ProjectMembersMixin:
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
            return Response({"code": 200, "message": "成员添加成功", "data": serializer.data})
        except User.DoesNotExist:
            return Response(
                {"code": 404, "message": "用户不存在"},
                status=status.HTTP_404_NOT_FOUND,
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
                {"code": 404, "message": "成员不存在"},
                status=status.HTTP_404_NOT_FOUND,
            )

