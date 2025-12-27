"""
用户服务
"""

from django.contrib.auth.hashers import check_password, make_password
from ..repositories.user_repository import UserRepository
from ..serializers import UserSerializer, ChangePasswordSerializer


class UserService:
    """
    用户服务类
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

    def change_password(self, user, old_password, new_password, confirm_password):
        """
        修改用户密码

        Args:
            user: 用户对象
            old_password: 旧密码
            new_password: 新密码
            confirm_password: 确认密码

        Returns:
            dict: 操作结果
        """
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Changing password for user: {user.username}")

        # 验证旧密码
        if not check_password(old_password, user.password):
            return {"success": False, "error": "原密码错误"}

        # 验证新密码格式
        serializer = ChangePasswordSerializer(
            data={
                "old_password": old_password,
                "new_password": new_password,
                "confirm_password": confirm_password,
            }
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

    def import_users(
        self,
        file,
        default_role="STUDENT",
        expert_scope=None,
        default_college=None,
    ):
        """
        批量导入用户
        """
        import openpyxl
        from django.db import transaction
        from apps.users.models import User

        wb = openpyxl.load_workbook(file)
        sheet = wb.active
        
        created_count = 0
        errors = []

        # Assuming headers: 工号/学号, 姓名, 学院, 专业, 班级, 手机号, 邮箱
        # Row 1 is header
        
        with transaction.atomic():
            for row_idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
                employee_id = str(row[0]).strip() if row[0] else None
                real_name = str(row[1]).strip() if row[1] else None
                
                if not employee_id or not real_name:
                    continue

                if User.objects.filter(employee_id=employee_id).exists():
                    errors.append(f"Row {row_idx}: User {employee_id} already exists")
                    continue
                
                try:
                    user_data = {
                        "employee_id": employee_id,
                        "real_name": real_name,
                        "username": employee_id,
                        "role": default_role,
                        "college": str(row[2]).strip() if len(row) > 2 and row[2] else "",
                        "major": str(row[3]).strip() if len(row) > 3 and row[3] else "",
                        "class_name": str(row[4]).strip() if len(row) > 4 and row[4] else "",
                        "phone": str(row[5]).strip() if len(row) > 5 and row[5] else "",
                        "email": str(row[6]).strip() if len(row) > 6 and row[6] else "",
                    }
                    if default_role == User.UserRole.EXPERT:
                        user_data["expert_scope"] = expert_scope or User.ExpertScope.COLLEGE
                        if user_data["expert_scope"] == User.ExpertScope.SCHOOL:
                            user_data["college"] = ""
                        elif default_college:
                            user_data["college"] = default_college
                    user = User.objects.create(**user_data)
                    user.set_password("123456") # Default password
                    user.save()
                    created_count += 1
                except Exception as e:
                    errors.append(f"Row {row_idx}: {str(e)}")

        return {"created": created_count, "errors": errors}
