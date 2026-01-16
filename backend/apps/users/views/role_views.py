"""
角色管理视图
提供角色的查询、创建、更新功能
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q
import uuid

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
    角色管理视图集
    校级管理员可以创建、修改、删除角色
    所有创建的角色都是二级管理员（有scope_dimension）
    """

    permission_classes = [IsAuthenticated]

    def _check_level1_admin(self, user):
        """检查是否为校级管理员"""
        return (
            hasattr(user, "role_fk")
            and user.role_fk
            and user.role_fk.code == "LEVEL1_ADMIN"
        )

    def _generate_role_code(self, name):
        """根据角色名称生成唯一的角色代码"""
        import re

        # 尝试从名称提取字母
        base = re.sub(r"[^A-Za-z0-9]", "", name).upper()
        if not base:
            base = "ROLE"

        # 生成唯一代码
        code = base[:20]
        counter = 1
        while Role.objects.filter(code=code).exists():
            suffix = str(uuid.uuid4().hex[:6]).upper()
            code = f"{base[:14]}_{suffix}"
            counter += 1
            if counter > 10:
                code = f"ROLE_{uuid.uuid4().hex[:16].upper()}"
                break

        return code

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
        if not self._check_level1_admin(request.user):
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

    def create(self, request):
        """
        创建角色（仅校级管理员）
        POST /api/auth/roles/

        所有创建的角色都是二级管理员，必须指定scope_dimension
        """
        if not self._check_level1_admin(request.user):
            return Response({"detail": "权限不足"}, status=status.HTTP_403_FORBIDDEN)

        name = request.data.get("name")
        scope_dimension = request.data.get("scope_dimension")

        if not name:
            return Response(
                {"detail": "角色名称不能为空"}, status=status.HTTP_400_BAD_REQUEST
            )

        if not scope_dimension:
            return Response(
                {"detail": "必须指定管理范围维度（scope_dimension）"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 自动生成角色代码
        code = self._generate_role_code(name)

        # 创建角色，统一设置为二级管理员
        role = Role.objects.create(
            code=code,
            name=name,
            scope_dimension=scope_dimension,
            default_route="/level2-admin/projects",  # 统一的二级管理员路由
            is_system=False,
            is_active=True,
        )

        return Response(
            {
                "id": role.id,
                "code": role.code,
                "name": role.name,
                "scope_dimension": role.scope_dimension,
                "default_route": role.default_route,
                "is_system": role.is_system,
                "is_active": role.is_active,
            },
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, pk=None):
        """
        更新角色（仅校级管理员）
        PUT /api/auth/roles/{id}/
        """
        if not self._check_level1_admin(request.user):
            return Response({"detail": "权限不足"}, status=status.HTTP_403_FORBIDDEN)

        try:
            role = Role.objects.get(pk=pk)
        except Role.DoesNotExist:
            return Response({"detail": "角色不存在"}, status=status.HTTP_404_NOT_FOUND)

        # 系统角色不能修改
        if role.is_system:
            return Response(
                {"detail": "系统内置角色不可修改"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 更新字段
        if "name" in request.data:
            role.name = request.data["name"]

        if "scope_dimension" in request.data:
            if not request.data["scope_dimension"]:
                return Response(
                    {"detail": "管理范围维度不能为空"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            role.scope_dimension = request.data["scope_dimension"]

        role.save()

        return Response(
            {
                "id": role.id,
                "code": role.code,
                "name": role.name,
                "scope_dimension": role.scope_dimension,
                "default_route": role.default_route,
                "is_system": role.is_system,
                "is_active": role.is_active,
            }
        )

    def destroy(self, request, pk=None):
        """
        删除角色（仅校级管理员）
        DELETE /api/auth/roles/{id}/
        """
        if not self._check_level1_admin(request.user):
            return Response({"detail": "权限不足"}, status=status.HTTP_403_FORBIDDEN)

        try:
            role = Role.objects.get(pk=pk)
        except Role.DoesNotExist:
            return Response({"detail": "角色不存在"}, status=status.HTTP_404_NOT_FOUND)

        # 系统角色不能删除
        if role.is_system:
            return Response(
                {"detail": "系统内置角色不能删除"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 检查是否有用户使用该角色
        user_count = role.users.count()
        if user_count > 0:
            return Response(
                {"detail": f"该角色被 {user_count} 个用户使用，无法删除"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        role.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], url_path="toggle-status")
    def toggle_status(self, request, pk=None):
        """
        切换角色状态
        POST /api/auth/roles/{id}/toggle-status/
        """
        if not self._check_level1_admin(request.user):
            return Response({"detail": "权限不足"}, status=status.HTTP_403_FORBIDDEN)

        try:
            role = Role.objects.get(pk=pk)
        except Role.DoesNotExist:
            return Response({"detail": "角色不存在"}, status=status.HTTP_404_NOT_FOUND)

        # 系统角色不能禁用
        if role.is_system and role.is_active:
            return Response(
                {"detail": "系统内置角色不能禁用"},
                status=status.HTTP_400_BAD_REQUEST,
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
