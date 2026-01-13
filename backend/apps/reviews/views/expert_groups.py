"""
专家组管理视图
"""

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
        
        if user.is_level1_admin:
            # 校级管理员管理校级专家组
            return queryset.filter(scope="SCHOOL")
        elif user.is_level2_admin:
             # 院级管理员管理本院专家组 (created_by handles college implication usually, or we filter by creator)
             # Better: Filter by scope COLLEGE and created_by college (if we had college field, but created_by is proxy)
             return queryset.filter(scope="COLLEGE", created_by__college=user.college)
        elif user.is_expert:
            # 专家只能看自己在的组? Or generic access? Let's say experts only see groups they are in if needed.
             return queryset.filter(members=user)
        return queryset.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_level1_admin:
            scope = "SCHOOL"
        elif user.is_level2_admin:
            scope = "COLLEGE"
        else:
            raise PermissionDenied("无权限创建专家组")
        serializer.save(created_by=user, scope=scope)

    def perform_update(self, serializer):
        user = self.request.user
        if not (user.is_level1_admin or user.is_level2_admin):
            raise PermissionDenied("无权限修改专家组")
        if user.is_level1_admin and serializer.instance.scope != "SCHOOL":
            raise PermissionDenied("无权限修改该专家组")
        if user.is_level2_admin and serializer.instance.scope != "COLLEGE":
            raise PermissionDenied("无权限修改该专家组")
        serializer.save()

