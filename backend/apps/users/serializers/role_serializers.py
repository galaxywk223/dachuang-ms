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

    user_count = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = [
            "id",
            "code",
            "name",
            "is_system",
            "is_active",
            "user_count",
            "created_at",
        ]
        read_only_fields = ["created_at", "code"]

    def get_user_count(self, obj):
        """获取拥有该角色的用户数量"""
        return obj.users.filter(is_active=True).count()


class RoleDetailSerializer(serializers.ModelSerializer):
    """角色详情序列化器"""

    user_count = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = [
            "id",
            "code",
            "name",
            "scope_dimension",
            "is_system",
            "is_active",
            "user_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at", "code", "is_system"]

    def get_user_count(self, obj):
        """获取拥有该角色的用户数量"""
        return obj.users.filter(is_active=True).count()

    def _generate_role_code(self, name):
        """根据角色名称生成唯一的角色代码"""
        import re
        import uuid

        # 尝试从名称提取字母
        base = re.sub(r"[^A-Za-z0-9]", "", name).upper()
        if not base:
            base = "ROLE"

        # 生成唯一代码
        code = base[:20]  # 限制长度
        counter = 1
        while Role.objects.filter(code=code).exists():
            suffix = str(uuid.uuid4().hex[:6]).upper()
            code = f"{base[:14]}_{suffix}"
            counter += 1
            if counter > 10:  # 避免无限循环
                code = f"ROLE_{uuid.uuid4().hex[:16].upper()}"
                break

        return code

    def validate(self, attrs):
        """验证数据"""
        # 如果是更新操作，检查是否是系统角色
        if self.instance and self.instance.is_system:
            # 系统角色不允许修改任何字段（除了is_active状态在视图层处理）
            raise serializers.ValidationError("系统内置角色不可修改")

        return attrs

    def create(self, validated_data):
        """创建角色"""
        # 自动生成角色代码
        validated_data["code"] = self._generate_role_code(validated_data["name"])
        role = Role.objects.create(**validated_data)
        return role

    def update(self, instance, validated_data):
        """更新角色"""
        # 更新基本字段（code不可修改）
        for attr, value in validated_data.items():
            if attr != "code":  # 不允许修改code
                setattr(instance, attr, value)
        instance.save()
        return instance


class RoleSimpleSerializer(serializers.ModelSerializer):
    """角色简化序列化器（用于下拉选择等场景）"""

    class Meta:
        model = Role
        fields = ["id", "code", "name", "default_route", "scope_dimension"]


class PermissionCategorySerializer(serializers.Serializer):
    """权限分类序列化器（用于分组显示）"""

    category = serializers.CharField()
    permissions = PermissionSerializer(many=True)
