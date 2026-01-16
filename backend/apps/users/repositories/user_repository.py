"""
用户数据访问层
"""

from django.contrib.auth import get_user_model
from django.db.models import Q

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
        # 获取角色信息
        role_info = None
        default_route = "/"

        if user.role_fk:
            role_info = {
                "id": user.role_fk.id,
                "code": user.role_fk.code,
                "name": user.role_fk.name,
                "default_route": user.role_fk.default_route,
            }
            default_route = user.role_fk.default_route or "/"

        return {
            "id": user.id,
            "employee_id": user.employee_id,
            "real_name": user.real_name,
            "role": user.get_role_code(),  # 兼容旧的角色代码字段
            "role_info": role_info,
            "default_route": default_route,
            "is_expert": user.is_expert,
            "expert_scope": user.expert_scope if user.is_expert else None,
            "college": user.college,
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
        from apps.users.models import Role

        role_code = data.pop("role", None)
        if role_code:
            role = Role.objects.filter(code=role_code).first()
            if not role:
                raise ValueError("角色不存在")
            data["role_fk"] = role

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
                role = filters["role"]
                if role == "EXPERT":
                    queryset = queryset.filter(
                        Q(role_fk__code=User.UserRole.TEACHER)
                        | Q(role_fk__code__endswith="_ADMIN"),
                        is_expert=True,
                    )
                elif role == User.UserRole.TEACHER:
                    queryset = queryset.filter(
                        Q(role_fk__code=User.UserRole.TEACHER)
                        | Q(role_fk__code__endswith="_ADMIN")
                    )
                else:
                    queryset = queryset.filter(role_fk__code=role)

            # 按学院过滤
            if "college" in filters:
                queryset = queryset.filter(college=filters["college"])

            # 按专家级别过滤
            if "expert_scope" in filters:
                queryset = queryset.filter(expert_scope=filters["expert_scope"])

            # 按专家资格过滤
            if "is_expert" in filters:
                queryset = queryset.filter(is_expert=filters["is_expert"])

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
        from apps.users.models import Role

        role_code = data.pop("role", None)
        if role_code and "role_fk" not in data:
            role = Role.objects.filter(code=role_code).first()
            if not role:
                raise ValueError("角色不存在")
            data["role_fk"] = role
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
