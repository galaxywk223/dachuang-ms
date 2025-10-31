"""
用户视图
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

from .models import User, LoginLog
from .serializers import (
    UserSerializer,
    LoginSerializer,
    ChangePasswordSerializer,
    UserCreateSerializer,
    LoginLogSerializer,
)
from .services import UserService

User = get_user_model()


class AuthViewSet(viewsets.GenericViewSet):
    """
    认证相关视图集
    """

    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    @action(methods=["post"], detail=False)
    def login(self, request):
        """
        用户登录
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        # 记录登录日志
        UserService.create_login_log(
            user=user,
            ip_address=self.get_client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            login_status=True,
        )

        # 生成JWT Token
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "code": 200,
                "message": "登录成功",
                "data": {
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                    "user": UserSerializer(user).data,
                },
            }
        )

    @action(methods=["post"], detail=False, permission_classes=[IsAuthenticated])
    def logout(self, request):
        """
        用户登出
        """
        return Response({"code": 200, "message": "登出成功"})

    @action(methods=["get"], detail=False, permission_classes=[IsAuthenticated])
    def profile(self, request):
        """
        获取当前用户信息
        """
        serializer = UserSerializer(request.user)
        return Response({"code": 200, "message": "获取成功", "data": serializer.data})

    @action(methods=["put"], detail=False, permission_classes=[IsAuthenticated])
    def update_profile(self, request):
        """
        更新当前用户信息
        """
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"code": 200, "message": "更新成功", "data": serializer.data})

    @action(methods=["post"], detail=False, permission_classes=[IsAuthenticated])
    def change_password(self, request):
        """
        修改密码
        """
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        if not user.check_password(serializer.validated_data["old_password"]):
            return Response(
                {"code": 400, "message": "原密码错误"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(serializer.validated_data["new_password"])
        user.save()

        return Response({"code": 200, "message": "密码修改成功"})

    def get_client_ip(self, request):
        """获取客户端IP地址"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


class UserViewSet(viewsets.ModelViewSet):
    """
    用户管理视图集（仅管理员可用）
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["role", "college", "is_active"]
    search_fields = ["employee_id", "real_name", "phone"]
    ordering_fields = ["created_at", "updated_at"]

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        return UserSerializer

    def get_queryset(self):
        """
        根据用户角色过滤查询集
        """
        user = self.request.user
        queryset = super().get_queryset()

        # 二级管理员只能看到自己学院的用户
        if user.is_level2_admin:
            queryset = queryset.filter(college=user.college)

        return queryset

    @action(methods=["post"], detail=True)
    def reset_password(self, request, pk=None):
        """
        重置用户密码为默认密码123456
        """
        user = self.get_object()
        user.set_password("123456")
        user.save()

        return Response({"code": 200, "message": "密码已重置为123456"})

    @action(methods=["post"], detail=True)
    def toggle_active(self, request, pk=None):
        """
        启用/禁用用户
        """
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()

        return Response(
            {"code": 200, "message": f"用户已{'启用' if user.is_active else '禁用'}"}
        )


class LoginLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    登录日志视图集（仅管理员可查看）
    """

    queryset = LoginLog.objects.all()
    serializer_class = LoginLogSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["user", "login_status"]
    search_fields = ["user__real_name", "user__employee_id", "ip_address"]
    ordering_fields = ["login_time"]
