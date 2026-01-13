"""
角色和权限管理视图
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count
from itertools import groupby

from apps.users.models import Role, Permission
from apps.users.permissions import IsLevel1Admin
from apps.users.serializers.role_serializers import (
    RoleListSerializer,
    RoleDetailSerializer,
    RoleSimpleSerializer,
    PermissionSerializer,
    PermissionCategorySerializer,
)


class RoleViewSet(viewsets.ModelViewSet):
    """
    角色管理视图集
    仅校级管理员可以管理角色
    """

    queryset = Role.objects.all()
    permission_classes = [IsAuthenticated, IsLevel1Admin]

    def get_serializer_class(self):
        """根据操作类型返回不同的序列化器"""
        if self.action == "list":
            return RoleListSerializer
        elif self.action == "simple_list":
            return RoleSimpleSerializer
        return RoleDetailSerializer

    def get_queryset(self):
        """获取角色列表"""
        queryset = Role.objects.all()

        # 搜索过滤
        search = self.request.query_params.get("search", "")
        if search:
            queryset = queryset.filter(
                Q(code__icontains=search)
                | Q(name__icontains=search)
                | Q(description__icontains=search)
            )

        # 状态过滤
        is_active = self.request.query_params.get("is_active", "")
        if is_active:
            queryset = queryset.filter(is_active=is_active.lower() == "true")

        # 是否系统内置过滤
        is_system = self.request.query_params.get("is_system", "")
        if is_system:
            queryset = queryset.filter(is_system=is_system.lower() == "true")

        # 排序
        ordering = self.request.query_params.get("ordering", "sort_order")
        queryset = queryset.order_by(ordering)

        return queryset

    def destroy(self, request, *args, **kwargs):
        """删除角色"""
        role = self.get_object()

        # 系统内置角色不能删除
        if role.is_system:
            return Response(
                {"detail": "系统内置角色不能删除"}, status=status.HTTP_400_BAD_REQUEST
            )

        # 检查是否有用户使用该角色
        user_count = role.users.count()
        if user_count > 0:
            return Response(
                {"detail": f"该角色被 {user_count} 个用户使用，无法删除"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=["get"])
    def simple_list(self, request):
        """
        获取角色简化列表（用于下拉选择）
        GET /api/users/roles/simple_list/
        """
        roles = Role.objects.filter(is_active=True).order_by("sort_order")
        serializer = RoleSimpleSerializer(roles, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def toggle_status(self, request, pk=None):
        """
        切换角色状态
        POST /api/users/roles/{id}/toggle_status/
        """
        role = self.get_object()

        # 系统内置角色不能禁用
        if role.is_system and role.is_active:
            return Response(
                {"detail": "系统内置角色不能禁用"}, status=status.HTTP_400_BAD_REQUEST
            )

        role.is_active = not role.is_active
        role.save()

        return Response(
            {
                "id": role.id,
                "is_active": role.is_active,
                "message": f"角色已{'启用' if role.is_active else '禁用'}",
            }
        )

    @action(detail=True, methods=["get"])
    def users(self, request, pk=None):
        """
        获取拥有该角色的用户列表
        GET /api/users/roles/{id}/users/
        """
        role = self.get_object()
        users = role.users.filter(is_active=True).order_by("-created_at")

        # 分页
        page = self.paginate_queryset(users)
        if page is not None:
            from apps.users.serializers import UserSerializer

            serializer = UserSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        from apps.users.serializers import UserSerializer

        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def statistics(self, request):
        """
        获取角色统计信息
        GET /api/users/roles/statistics/
        """
        roles = Role.objects.annotate(
            user_count=Count("users", filter=Q(users__is_active=True)),
            permission_count=Count(
                "permissions", filter=Q(permissions__is_active=True)
            ),
        )

        stats = {
            "total_roles": roles.count(),
            "active_roles": roles.filter(is_active=True).count(),
            "system_roles": roles.filter(is_system=True).count(),
            "custom_roles": roles.filter(is_system=False).count(),
            "roles": [
                {
                    "id": role.id,
                    "code": role.code,
                    "name": role.name,
                    "user_count": role.user_count,
                    "permission_count": role.permission_count,
                    "is_system": role.is_system,
                    "is_active": role.is_active,
                }
                for role in roles.order_by("sort_order")
            ],
        }

        return Response(stats)


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    权限管理视图集
    仅校级管理员可以查看权限
    权限本身不提供创建/修改/删除接口，由系统预定义
    """

    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated, IsLevel1Admin]

    def get_queryset(self):
        """获取权限列表"""
        queryset = Permission.objects.all()

        # 搜索过滤
        search = self.request.query_params.get("search", "")
        if search:
            queryset = queryset.filter(
                Q(code__icontains=search)
                | Q(name__icontains=search)
                | Q(description__icontains=search)
            )

        # 分类过滤
        category = self.request.query_params.get("category", "")
        if category:
            queryset = queryset.filter(category=category)

        # 状态过滤
        is_active = self.request.query_params.get("is_active", "")
        if is_active:
            queryset = queryset.filter(is_active=is_active.lower() == "true")

        # 排序
        ordering = self.request.query_params.get("ordering", "category,code")
        queryset = queryset.order_by(*ordering.split(","))

        return queryset

    @action(detail=False, methods=["get"])
    def categories(self, request):
        """
        获取权限分类列表
        GET /api/users/permissions/categories/
        """
        permissions = Permission.objects.filter(is_active=True).order_by(
            "category", "code"
        )

        # 按分类分组
        grouped_data = []
        for category, group in groupby(permissions, key=lambda x: x.category or "其他"):
            grouped_data.append({"category": category, "permissions": list(group)})

        serializer = PermissionCategorySerializer(grouped_data, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def by_category(self, request):
        """
        获取按分类组织的权限树
        GET /api/users/permissions/by_category/
        """
        permissions = Permission.objects.filter(is_active=True).order_by(
            "category", "code"
        )

        # 按分类组织
        result = {}
        for perm in permissions:
            category = perm.category or "其他"
            if category not in result:
                result[category] = []
            result[category].append(
                {
                    "id": perm.id,
                    "code": perm.code,
                    "name": perm.name,
                    "description": perm.description,
                }
            )

        return Response(result)
