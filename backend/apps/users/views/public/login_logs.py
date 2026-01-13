"""
登录日志视图
"""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from ...models import LoginLog
from ...serializers import LoginLogSerializer


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
        if user.is_level1_admin or user.is_level2_admin:
            return self.queryset
        return self.queryset.filter(user=user)
