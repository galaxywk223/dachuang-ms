"""
用户业务逻辑
"""

from django.contrib.auth.hashers import check_password, make_password
from ..repositories.user_repository import UserRepository
from ..serializers import UserSerializer, ChangePasswordSerializer


class UserBusiness:
    """
    用户业务逻辑类
    """

    def __init__(self):
        self.user_repository = UserRepository()

    def get_user_profile(self, user):
        """
        获取用户资料

        Args:
            user: 用户对象

        Returns:
            dict: 用户资料数据
        """
        serializer = UserSerializer(user)
        return serializer.data

    def update_user_profile(self, user, data):
        """
        更新用户资料

        Args:
            user: 用户对象
            data: 更新数据

        Returns:
            dict: 更新后的用户数据
        """
        # 过滤掉不允许更新的字段
        allowed_fields = ["real_name", "phone", "email"]
        filtered_data = {k: v for k, v in data.items() if k in allowed_fields}

        updated_user = self.user_repository.update_user(user, filtered_data)
        serializer = UserSerializer(updated_user)
        return serializer.data

    def change_password(self, user, old_password, new_password):
        """
        修改用户密码

        Args:
            user: 用户对象
            old_password: 旧密码
            new_password: 新密码

        Returns:
            dict: 操作结果
        """
        # 验证旧密码
        if not check_password(old_password, user.password):
            return {"success": False, "error": "原密码错误"}

        # 验证新密码格式
        serializer = ChangePasswordSerializer(
            data={"old_password": old_password, "new_password": new_password}
        )

        if not serializer.is_valid():
            return {"success": False, "error": "新密码格式不正确"}

        # 更新密码
        user.password = make_password(new_password)
        user.save(update_fields=["password"])

        return {"success": True}

    def reset_password(self, user, new_password="123456"):
        """
        重置用户密码

        Args:
            user: 用户对象
            new_password: 新密码，默认为123456

        Returns:
            bool: 操作结果
        """
        user.password = make_password(new_password)
        user.save(update_fields=["password"])
        return True

    def toggle_user_active(self, user):
        """
        切换用户激活状态

        Args:
            user: 用户对象

        Returns:
            bool: 新的激活状态
        """
        user.is_active = not user.is_active
        user.save(update_fields=["is_active"])
        return user.is_active

    def get_user_list(self, filters=None):
        """
        获取用户列表

        Args:
            filters: 过滤条件

        Returns:
            QuerySet: 用户查询集
        """
        return self.user_repository.get_user_list(filters)

    def create_user(self, data):
        """
        创建用户

        Args:
            data: 用户数据

        Returns:
            User: 创建的用户对象
        """
        return self.user_repository.create_user(data)
