"""
用户认证视图
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from ...serializers import LoginSerializer
from ...services.auth_service import AuthService
from ...services.user_service import UserService


class AuthViewSet(viewsets.GenericViewSet):
    """
    认证控制器
    """

    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auth_service = AuthService()
        self.user_service = UserService()

    def get_permissions(self):
        public_actions = {"login", "refresh"}
        if self.action in public_actions:
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(methods=["post"], detail=False)
    def login(self, request):
        """
        用户登录
        """
        import logging

        logger = logging.getLogger(__name__)

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.error("Login serializer errors: %s", serializer.errors)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        # 通过业务层处理登录逻辑
        token_data = self.auth_service.handle_login(
            user=user,
            ip_address=self._get_client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )
        return Response(token_data, status=status.HTTP_200_OK)

    @action(methods=["post"], detail=False, permission_classes=[AllowAny])
    def refresh(self, request):
        """
        刷新访问令牌
        """
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return Response(
                {"code": 400, "message": "请提供刷新令牌", "data": None},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = TokenRefreshSerializer(data={"refresh": refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
        except (InvalidToken, TokenError):
            return Response(
                {"code": 401, "message": "刷新令牌无效或已过期", "data": None},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        token_data = serializer.validated_data

        return Response(
            {
                "code": 200,
                "message": "刷新成功",
                "data": {
                    "access_token": token_data["access"],
                    "refresh_token": token_data.get("refresh", refresh_token),
                },
            },
            status=status.HTTP_200_OK,
        )

    @action(methods=["post"], detail=False, permission_classes=[IsAuthenticated])
    def logout(self, request):
        """
        用户登出
        """
        self.auth_service.handle_logout(
            request.user, refresh_token=request.data.get("refresh_token")
        )
        return Response(
            {"code": 200, "message": "登出成功", "data": None},
            status=status.HTTP_200_OK,
        )

    @action(methods=["get"], detail=False, permission_classes=[IsAuthenticated])
    def profile(self, request):
        """
        获取用户信息
        """
        user_data = self.user_service.get_user_profile(request.user)
        return Response(
            {"code": 200, "message": "获取成功", "data": user_data},
            status=status.HTTP_200_OK,
        )

    @action(methods=["put"], detail=False, permission_classes=[IsAuthenticated])
    def update_profile(self, request):
        """
        更新用户信息
        """
        updated_user = self.user_service.update_user_profile(
            request.user, request.data
        )
        return Response(
            {"code": 200, "message": "更新成功", "data": updated_user},
            status=status.HTTP_200_OK,
        )

    @action(methods=["post"], detail=False, permission_classes=[IsAuthenticated])
    def change_password(self, request):
        """
        修改密码
        """
        result = self.user_service.change_password(
            user=request.user,
            old_password=request.data.get("old_password"),
            new_password=request.data.get("new_password"),
            confirm_password=request.data.get("confirm_password"),
        )

        if result["success"]:
            return Response(
                {"code": 200, "message": "密码修改成功", "data": None},
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "code": 400,
                "message": result["error"],
                "errors": {"non_field_errors": [result["error"]]},
                "data": None,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def _get_client_ip(self, request):
        """获取客户端IP地址"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip
