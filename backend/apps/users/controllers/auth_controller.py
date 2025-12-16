"""
用户认证控制器
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from ..serializers import LoginSerializer
from ..business.auth_business import AuthBusiness
from ..business.user_business import UserBusiness


class AuthController(viewsets.GenericViewSet):
    """
    认证控制器
    """

    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auth_business = AuthBusiness()
        self.user_business = UserBusiness()

    @action(methods=["post"], detail=False)
    def login(self, request):
        """
        用户登录
        """
        # 添加调试日志
        import logging

        logger = logging.getLogger(__name__)
        logger.info(f"Login request data: {request.data}")

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Serializer errors: {serializer.errors}")
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        # 通过业务层处理登录逻辑
        token_data = self.auth_business.handle_login(
            user=user,
            ip_address=self._get_client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )

        return Response(token_data, status=status.HTTP_200_OK)

    @action(methods=["post"], detail=False)
    def logout(self, request):
        """
        用户登出
        """
        return Response({"message": "登出成功"}, status=status.HTTP_200_OK)

    @action(methods=["get"], detail=False, permission_classes=[IsAuthenticated])
    def profile(self, request):
        """
        获取用户信息
        """
        user_data = self.user_business.get_user_profile(request.user)
        return Response(user_data, status=status.HTTP_200_OK)

    @action(methods=["put"], detail=False, permission_classes=[IsAuthenticated])
    def update_profile(self, request):
        """
        更新用户信息
        """
        updated_user = self.user_business.update_user_profile(
            request.user, request.data
        )
        return Response(updated_user, status=status.HTTP_200_OK)

    @action(methods=["put"], detail=False, permission_classes=[IsAuthenticated])
    def change_password(self, request):
        """
        修改密码
        """
        result = self.user_business.change_password(
            request.user,
            request.data.get("old_password"),
            request.data.get("new_password"),
        )

        if result["success"]:
            return Response({"message": "密码修改成功"}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": result["error"]}, status=status.HTTP_400_BAD_REQUEST
            )

    def _get_client_ip(self, request):
        """获取客户端IP地址"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip
