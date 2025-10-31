"""
用户序列化器
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, LoginLog


class UserSerializer(serializers.ModelSerializer):
    """
    用户序列化器
    """

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "employee_id",
            "real_name",
            "role",
            "phone",
            "email",
            "major",
            "grade",
            "class_name",
            "college",
            "department",
            "avatar",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class LoginSerializer(serializers.Serializer):
    """登录序列化器（仅允许使用学号/工号 employee_id 登录）"""

    employee_id = serializers.CharField(required=True, help_text="学号/工号")
    password = serializers.CharField(required=True, write_only=True, help_text="密码")
    role = serializers.CharField(
        required=False, default="student", help_text="登录角色"
    )

    default_error_messages = {
        "invalid_credentials": "学号/工号或密码错误",
        "inactive": "用户账号已被禁用",
        "required": "必须提供学号/工号和密码",
        "role_mismatch": "登录身份与账号角色不匹配",
    }

    def validate(self, attrs):
        employee_id = attrs.get("employee_id")
        password = attrs.get("password")
        role = attrs.get("role", "student")

        if not (employee_id and password):
            raise serializers.ValidationError(self.error_messages["required"])

        try:
            user = User.objects.get(employee_id=employee_id)
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

        # 验证角色匹配
        if role == "student" and user.role != "STUDENT":
            raise serializers.ValidationError(self.error_messages["role_mismatch"])
        elif role == "admin" and user.role not in ["LEVEL1_ADMIN", "LEVEL2_ADMIN"]:
            raise serializers.ValidationError(self.error_messages["role_mismatch"])

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
            "password",
            "phone",
            "email",
            "major",
            "grade",
            "class_name",
            "college",
            "department",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password", "123456")
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
