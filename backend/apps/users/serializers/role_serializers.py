"""
角色和权限管理序列化器
"""

from rest_framework import serializers
from apps.users.models import Role, Permission


class PermissionSerializer(serializers.ModelSerializer):
    """权限序列化器"""

    class Meta:
        model = Permission
        fields = [
            "id",
            "code",
            "name",
            "description",
            "category",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class RoleListSerializer(serializers.ModelSerializer):
    """角色列表序列化器（简化版）"""

    permission_count = serializers.SerializerMethodField()
    user_count = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = [
            "id",
            "code",
            "name",
            "description",
            "is_system",
            "is_active",
            "default_route",
            "sort_order",
            "permission_count",
            "user_count",
            "created_at",
        ]
        read_only_fields = ["created_at"]

    def get_permission_count(self, obj):
        """获取角色拥有的权限数量"""
        return obj.permissions.filter(is_active=True).count()

    def get_user_count(self, obj):
        """获取拥有该角色的用户数量"""
        return obj.users.filter(is_active=True).count()


class RoleDetailSerializer(serializers.ModelSerializer):
    """角色详情序列化器（包含完整权限列表）"""

    permissions = PermissionSerializer(many=True, read_only=True)
    permission_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="权限ID列表",
    )
    user_count = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = [
            "id",
            "code",
            "name",
            "description",
            "permissions",
            "permission_ids",
            "is_system",
            "is_active",
            "default_route",
            "sort_order",
            "user_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def get_user_count(self, obj):
        """获取拥有该角色的用户数量"""
        return obj.users.filter(is_active=True).count()

    def validate_code(self, value):
        """验证角色代码"""
        # 角色代码应该是大写字母、数字和下划线
        import re

        if not re.match(r"^[A-Z0-9_]+$", value):
            raise serializers.ValidationError("角色代码只能包含大写字母、数字和下划线")
        return value

    def validate(self, attrs):
        """验证数据"""
        # 如果是更新操作，检查是否是系统角色
        if self.instance and self.instance.is_system:
            # 系统角色的 code 不可修改
            if "code" in attrs and attrs["code"] != self.instance.code:
                raise serializers.ValidationError(
                    {"code": "系统内置角色的代码不可修改"}
                )

        return attrs

    def create(self, validated_data):
        """创建角色"""
        permission_ids = validated_data.pop("permission_ids", [])
        role = Role.objects.create(**validated_data)

        if permission_ids:
            permissions = Permission.objects.filter(
                id__in=permission_ids, is_active=True
            )
            role.permissions.set(permissions)

        return role

    def update(self, instance, validated_data):
        """更新角色"""
        permission_ids = validated_data.pop("permission_ids", None)

        # 更新基本字段
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # 更新权限关联
        if permission_ids is not None:
            permissions = Permission.objects.filter(
                id__in=permission_ids, is_active=True
            )
            instance.permissions.set(permissions)

        return instance


class RoleSimpleSerializer(serializers.ModelSerializer):
    """角色简化序列化器（用于下拉选择等场景）"""

    class Meta:
        model = Role
        fields = ["id", "code", "name", "default_route"]


class PermissionCategorySerializer(serializers.Serializer):
    """权限分类序列化器（用于分组显示）"""

    category = serializers.CharField()
    permissions = PermissionSerializer(many=True)
