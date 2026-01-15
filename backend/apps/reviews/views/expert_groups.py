"""
专家组管理视图
"""

from django.db.models import Q
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied

from ..models import ExpertGroup
from ..serializers import ExpertGroupSerializer
from .permissions import ExpertGroupPermission


class ExpertGroupViewSet(viewsets.ModelViewSet):
    """
    专家组管理视图集
    """

    queryset = ExpertGroup.objects.all()
    serializer_class = ExpertGroupSerializer
    permission_classes = [ExpertGroupPermission]

    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()

        if user.is_admin:
            return queryset.filter(Q(created_by=user) | Q(members=user)).distinct()
        elif user.is_teacher:
            # 教师（作为专家）只能看自己在的组
            return queryset.filter(members=user)
        return queryset.none()

    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_admin:
            raise PermissionDenied("无权限创建专家组")
        scope = "SCHOOL" if user.is_level1_admin else "COLLEGE"
        serializer.save(created_by=user, scope=scope)

    def perform_update(self, serializer):
        user = self.request.user
        if not user.is_admin:
            raise PermissionDenied("无权限修改专家组")
        if serializer.instance.created_by_id != user.id:
            raise PermissionDenied("无权限修改该专家组")
        serializer.save()
