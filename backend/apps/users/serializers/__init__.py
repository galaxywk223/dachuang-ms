"""
用户序列化器
"""

from rest_framework import serializers
from ..models import User, LoginLog


class UserSerializer(serializers.ModelSerializer):
    """
    用户序列化器
    """

    role_info = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "employee_id",
            "real_name",
            "role",
            "role_fk",
            "role_info",
            "permissions",
            "expert_scope",
            "phone",
            "email",
            "major",
            "grade",
            "class_name",
            "college",
            "department",
            "title",
            "avatar",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_role_info(self, obj):
        """获取角色信息"""
        if obj.role_fk:
            return {
                "id": obj.role_fk.id,
                "code": obj.role_fk.code,
                "name": obj.role_fk.name,
                "default_route": obj.role_fk.default_route,
            }
        return None

    def get_permissions(self, obj):
        """获取用户权限列表"""
        return obj.get_permissions()


class LoginSerializer(serializers.Serializer):
    """登录序列化器（使用学号/工号和密码直接登录）"""

    employee_id = serializers.CharField(required=True, help_text="学号/工号")
    password = serializers.CharField(required=True, write_only=True, help_text="密码")

    default_error_messages = {
        "invalid_credentials": "学号/工号或密码错误",
        "inactive": "用户账号已被禁用",
        "required": "必须提供学号/工号和密码",
        "no_role": "用户未分配角色，请联系管理员",
    }

    def validate(self, attrs):
        employee_id = attrs.get("employee_id")
        password = attrs.get("password")

        if not (employee_id and password):
            raise serializers.ValidationError(self.error_messages["required"])

        try:
            user = User.objects.select_related("role_fk").get(employee_id=employee_id)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                self.error_messages["invalid_credentials"]
            )

        if not user.check_password(password):
            raise serializers.ValidationError(
                self.error_messages["invalid_credentials"]
            )

        if not user.is_active:
            raise serializers.ValidationError(self.error_messages["inactive"])

        # 检查用户是否有角色
        if not user.role_fk:
            raise serializers.ValidationError(self.error_messages["no_role"])

        attrs["user"] = user
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    """
    修改密码序列化器
    """

    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError("两次输入的密码不一致")
        if len(attrs["new_password"]) < 6:
            raise serializers.ValidationError("密码长度不能少于6位")
        return attrs


class UserCreateSerializer(serializers.ModelSerializer):
    """
    用户创建序列化器
    """

    password = serializers.CharField(write_only=True, default="123456")

    class Meta:
        model = User
        fields = [
            "employee_id",
            "real_name",
            "role",
            "expert_scope",
            "password",
            "phone",
            "email",
            "major",
            "grade",
            "class_name",
            "college",
            "department",
            "title",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password", "123456")
        if validated_data.get("role") != User.UserRole.EXPERT:
            validated_data.pop("expert_scope", None)
        elif not validated_data.get("expert_scope"):
            validated_data["expert_scope"] = User.ExpertScope.COLLEGE
        user = User.objects.create(**validated_data)
        user.username = user.employee_id  # 使用学号/工号作为用户名
        user.set_password(password)
        user.save()
        return user


class LoginLogSerializer(serializers.ModelSerializer):
    """
    登录日志序列化器
    """

    user_name = serializers.CharField(source="user.real_name", read_only=True)
    user_id = serializers.CharField(source="user.employee_id", read_only=True)

    class Meta:
        model = LoginLog
        fields = [
            "id",
            "user",
            "user_name",
            "user_id",
            "login_time",
            "ip_address",
            "user_agent",
            "login_status",
        ]
        read_only_fields = ["id", "login_time"]
