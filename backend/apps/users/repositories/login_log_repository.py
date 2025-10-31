"""
登录日志数据访问层
"""

from ..models import LoginLog


class LoginLogRepository:
    """
    登录日志数据访问类
    """

    def create_login_log(self, user, ip_address, user_agent, login_status=True):
        """
        创建登录日志

        Args:
            user: 用户对象
            ip_address: IP地址
            user_agent: 用户代理
            login_status: 登录状态

        Returns:
            LoginLog: 创建的登录日志对象
        """
        log = LoginLog.objects.create(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            login_status=login_status,
        )
        return log

    def get_user_login_logs(self, user, limit=None):
        """
        获取用户登录日志

        Args:
            user: 用户对象
            limit: 限制条数

        Returns:
            QuerySet: 登录日志查询集
        """
        queryset = LoginLog.objects.filter(user=user).order_by("-login_time")

        if limit:
            queryset = queryset[:limit]

        return queryset

    def get_recent_login_logs(self, days=30, limit=None):
        """
        获取最近的登录日志

        Args:
            days: 最近天数
            limit: 限制条数

        Returns:
            QuerySet: 登录日志查询集
        """
        from datetime import datetime, timedelta

        start_date = datetime.now() - timedelta(days=days)
        queryset = LoginLog.objects.filter(login_time__gte=start_date).order_by(
            "-login_time"
        )

        if limit:
            queryset = queryset[:limit]

        return queryset

    def get_login_statistics(self, user=None, days=30):
        """
        获取登录统计信息

        Args:
            user: 用户对象（可选）
            days: 统计天数

        Returns:
            dict: 统计信息
        """
        from datetime import datetime, timedelta

        start_date = datetime.now() - timedelta(days=days)
        queryset = LoginLog.objects.filter(login_time__gte=start_date)

        if user:
            queryset = queryset.filter(user=user)

        total_logins = queryset.count()
        successful_logins = queryset.filter(login_status=True).count()
        failed_logins = total_logins - successful_logins

        return {
            "total_logins": total_logins,
            "successful_logins": successful_logins,
            "failed_logins": failed_logins,
            "success_rate": (successful_logins / total_logins * 100)
            if total_logins > 0
            else 0,
        }
