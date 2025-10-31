"""
用户业务逻辑层
"""

from .models import User, LoginLog


class UserService:
    """
    用户服务类
    """

    @staticmethod
    def create_login_log(user, ip_address, user_agent, login_status=True):
        """
        创建登录日志
        """
        return LoginLog.objects.create(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            login_status=login_status,
        )

    @staticmethod
    def create_user(employee_id, real_name, role, **kwargs):
        """
        创建用户
        """
        user = User.objects.create(
            username=employee_id,
            employee_id=employee_id,
            real_name=real_name,
            role=role,
            **kwargs,
        )
        user.set_password("123456")  # 默认密码
        user.save()
        return user

    @staticmethod
    def reset_password(user, new_password="123456"):
        """
        重置密码
        """
        user.set_password(new_password)
        user.save()
        return user

    @staticmethod
    def get_users_by_college(college):
        """
        获取指定学院的用户
        """
        return User.objects.filter(college=college)

    @staticmethod
    def get_students_by_college(college):
        """
        获取指定学院的学生
        """
        return User.objects.filter(role=User.UserRole.STUDENT, college=college)
