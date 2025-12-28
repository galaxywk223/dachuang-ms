"""
认证服务
"""

from rest_framework_simplejwt.tokens import RefreshToken
import logging
from ..repositories.user_repository import UserRepository
from ..repositories.login_log_repository import LoginLogRepository


class AuthService:
    """
    认证服务类
    """

    def __init__(self):
        self.user_repository = UserRepository()
        self.login_log_repository = LoginLogRepository()

    def handle_login(self, user, ip_address, user_agent):
        """
        处理用户登录逻辑

        Args:
            user: 用户对象
            ip_address: IP地址
            user_agent: 用户代理

        Returns:
            dict: 包含token和用户信息的字典
        """
        # 记录登录日志
        self.login_log_repository.create_login_log(
            user=user, ip_address=ip_address, user_agent=user_agent, login_status=True
        )

        # 生成token
        refresh = RefreshToken.for_user(user)

        # 获取用户详细信息
        user_data = self.user_repository.get_user_data(user)

        return {
            "code": 200,
            "message": "登录成功",
            "data": {
                "refresh_token": str(refresh),
                "access_token": str(refresh.access_token),
                "user": user_data,
            },
        }

    def handle_logout(self, user, refresh_token=None):
        """
        处理用户登出逻辑

        Args:
            user: 用户对象
            refresh_token: 刷新token（可选）
        """
        # 如果有refresh_token，可以将其加入黑名单
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception as exc:
                logging.getLogger(__name__).warning(
                    "Failed to blacklist refresh token: %s", exc
                )

        # 记录登出日志（如果需要的话）
        # self.login_log_repository.create_logout_log(user)

    def validate_token(self, token):
        """
        验证token有效性

        Args:
            token: JWT token

        Returns:
            dict: 验证结果
        """
        try:
            # 这里可以添加token验证逻辑
            return {"valid": True, "user_id": None}
        except Exception as e:
            return {"valid": False, "error": str(e)}
