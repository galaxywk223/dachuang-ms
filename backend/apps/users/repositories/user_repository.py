"""
用户数据访问层
"""

from django.contrib.auth import get_user_model
from django.db.models import Q
from ..models import User

User = get_user_model()


class UserRepository:
    """
    用户数据访问类
    """

    def get_user_by_id(self, user_id):
        """
        根据ID获取用户

        Args:
            user_id: 用户ID

        Returns:
            User: 用户对象或None
        """
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    def get_user_by_employee_id(self, employee_id):
        """
        根据工号/学号获取用户

        Args:
            employee_id: 工号/学号

        Returns:
            User: 用户对象或None
        """
        try:
            return User.objects.get(employee_id=employee_id)
        except User.DoesNotExist:
            return None

    def get_user_data(self, user):
        """
        获取用户基本数据

        Args:
            user: 用户对象

        Returns:
            dict: 用户数据字典
        """
        return {
            "id": user.id,
            "employee_id": user.employee_id,
            "real_name": user.real_name,
            "role": user.role,
            "department": user.department,
            "phone": user.phone,
            "email": user.email,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }

    def update_user(self, user, data):
        """
        更新用户信息

        Args:
            user: 用户对象
            data: 更新数据

        Returns:
            User: 更新后的用户对象
        """
        for key, value in data.items():
            if hasattr(user, key):
                setattr(user, key, value)

        user.save()
        return user

    def get_user_list(self, filters=None):
        """
        获取用户列表

        Args:
            filters: 过滤条件字典

        Returns:
            QuerySet: 用户查询集
        """
        queryset = User.objects.all()

        if filters:
            # 按角色过滤
            if "role" in filters:
                queryset = queryset.filter(role=filters["role"])

            # 按激活状态过滤
            if "is_active" in filters:
                queryset = queryset.filter(is_active=filters["is_active"])

            # 按关键词搜索
            if "search" in filters and filters["search"]:
                search_term = filters["search"]
                queryset = queryset.filter(
                    Q(employee_id__icontains=search_term)
                    | Q(real_name__icontains=search_term)
                    | Q(department__icontains=search_term)
                )

        return queryset.order_by("-created_at")

    def create_user(self, data):
        """
        创建用户

        Args:
            data: 用户数据

        Returns:
            User: 创建的用户对象
        """
        user = User.objects.create(**data)
        return user

    def delete_user(self, user):
        """
        删除用户

        Args:
            user: 用户对象

        Returns:
            bool: 操作结果
        """
        try:
            user.delete()
            return True
        except Exception:
            return False

    def bulk_update_users(self, user_ids, data):
        """
        批量更新用户

        Args:
            user_ids: 用户ID列表
            data: 更新数据

        Returns:
            int: 更新的用户数量
        """
        updated_count = User.objects.filter(id__in=user_ids).update(**data)
        return updated_count
