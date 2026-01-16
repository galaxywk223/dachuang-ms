"""
角色查询视图（只读）
提供角色列表查询功能，用于前端下拉选择等场景
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q

from apps.users.models import Role
from apps.users.permissions import IsLevel1Admin


class RoleSimpleSerializer:
    """角色简化序列化（不使用DRF serializer，直接返回字典）"""

    @staticmethod
    def to_dict(role):
        return {
            "id": role.id,
            "code": role.code,
            "name": role.name,
            "default_route": role.default_route,
            "scope_dimension": role.scope_dimension,
        }


class RoleViewSet(viewsets.ViewSet):
    """
    角色查询视图集（只读）
    只提供角色列表查询，不提供增删改功能
    """

    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"], url_path="simple")
    def simple_list(self, request):
        """
        获取角色简化列表（用于下拉选择）
        GET /api/auth/roles/simple/
        """
        roles = Role.objects.filter(is_active=True).order_by("sort_order")
        data = [RoleSimpleSerializer.to_dict(role) for role in roles]
        return Response(data)

    def list(self, request):
        """
        获取角色列表（带统计信息）
        GET /api/auth/roles/
        仅校级管理员可访问
        """
        # 检查权限
        if not (
            hasattr(request.user, "role_fk")
            and request.user.role_fk
            and request.user.role_fk.code == "LEVEL1_ADMIN"
        ):
            return Response({"detail": "权限不足"}, status=status.HTTP_403_FORBIDDEN)

        # 获取角色列表并统计用户数
        roles = Role.objects.annotate(
            user_count=Count("users", filter=Q(users__is_active=True))
        ).order_by("sort_order")

        # 搜索过滤
        search = request.query_params.get("search", "")
        if search:
            roles = roles.filter(Q(code__icontains=search) | Q(name__icontains=search))

        # 状态过滤
        is_active = request.query_params.get("is_active", "")
        if is_active:
            roles = roles.filter(is_active=is_active.lower() == "true")

        data = [
            {
                "id": role.id,
                "code": role.code,
                "name": role.name,
                "is_system": role.is_system,
                "is_active": role.is_active,
                "user_count": role.user_count,
                "scope_dimension": role.scope_dimension,
                "created_at": role.created_at.isoformat() if role.created_at else None,
            }
            for role in roles
        ]

        return Response(data)
