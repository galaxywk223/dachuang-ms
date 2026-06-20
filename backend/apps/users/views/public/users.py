"""
用户视图
"""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from ...serializers import PublicUserLookupSerializer
from ...models import User
from ...services.user_service import UserService


def has_school_admin_scope(user):
    return user.is_school_admin or user.is_level1_admin


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    用户视图集
    """

    permission_classes = [IsAuthenticated]
    public_lookup_roles = {User.UserRole.STUDENT, User.UserRole.TEACHER}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_service = UserService()

    def get_serializer_class(self):
        """根据操作类型返回相应的序列化器"""
        return PublicUserLookupSerializer

    def get_queryset(self):
        """获取查询集"""
        filters = {}
        current_user = self.request.user
        employee_id = self.request.query_params.get("employee_id", "").strip()

        # 根据角色过滤
        role = self.request.query_params.get("role", "").strip()
        if not current_user.is_admin:
            if not employee_id or role not in self.public_lookup_roles:
                return User.objects.none()
            return self.user_service.get_user_list(
                {
                    "employee_id": employee_id,
                    "role": role,
                    "is_active": True,
                }
            )

        if role:
            filters["role"] = role

        expert_scope = self.request.query_params.get("expert_scope")
        if expert_scope:
            filters["expert_scope"] = expert_scope

        is_expert = self.request.query_params.get("is_expert")
        if is_expert in ("true", "false"):
            filters["is_expert"] = is_expert == "true"

        # 根据激活状态过滤
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            filters["is_active"] = is_active.lower() == "true"

        # 搜索
        search = self.request.query_params.get("search")
        if search:
            filters["search"] = search

        if employee_id:
            filters["employee_id"] = employee_id

        if current_user.is_admin and not has_school_admin_scope(current_user):
            filters["role"] = User.UserRole.TEACHER
            if current_user.college:
                filters["college"] = current_user.college
            else:
                return User.objects.none()
        queryset = self.user_service.get_user_list(filters)
        if current_user.is_admin and not has_school_admin_scope(current_user):
            queryset = queryset.filter(
                Q(is_expert=False) | Q(expert_assigned_by=current_user)
            )
        return queryset
