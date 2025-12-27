"""
用户视图 - 使用分层架构
"""

# 导入新的控制器
from ..controllers.auth_controller import AuthController
from ..controllers.user_management_controller import UserManagementController

# 为了保持向后兼容，创建别名
AuthViewSet = AuthController
UserViewSet = UserManagementController

# 保留原有的LoginLogViewSet（如果需要的话）
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from ..models import LoginLog
from ..serializers import LoginLogSerializer
from .admin import UserManagementViewSet


class LoginLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    登录日志视图集
    """

    queryset = LoginLog.objects.all().order_by("-login_time")
    serializer_class = LoginLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        根据用户权限返回相应的查询集
        """
        user = self.request.user

        # 管理员可以查看所有日志，普通用户只能查看自己的日志
        if user.role in ["LEVEL1_ADMIN", "LEVEL2_ADMIN"]:
            return self.queryset
        else:
            return self.queryset.filter(user=user)
