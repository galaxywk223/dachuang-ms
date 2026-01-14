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

    def reset_password(self, user, new_password=None):
        """
        重置用户密码

        Args:
            user: 用户对象
            new_password: 新密码

        Returns:
            str: 新密码
        """
        from django.conf import settings

        if not new_password:
            new_password = settings.DEFAULT_RESET_PASSWORD
        if not new_password:
            raise ValueError("未配置默认重置密码")

        user.password = make_password(new_password)
        user.save(update_fields=["password"])
        return new_password

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
        import io
        import os
        import openpyxl  # type: ignore[import-untyped]
        import xlrd  # type: ignore[import-untyped]
        from django.db import transaction
        from apps.users.models import User, Role
        from apps.dictionaries.models import DictionaryItem

        data = file.read()
        ext = os.path.splitext(file.name or "")[1].lower()
        rows = []
        is_zip = data[:2] == b"PK"
        is_ole = data[:8] == b"\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1"

        def load_xlsx():
            wb = openpyxl.load_workbook(io.BytesIO(data), data_only=True)
            sheet = wb.active
            return list(sheet.iter_rows(values_only=True))

        def load_xls():
            book = xlrd.open_workbook(file_contents=data)
            sheet = book.sheet_by_index(0)
            return [sheet.row_values(idx) for idx in range(sheet.nrows)]

        if is_zip:
            rows = load_xlsx()
        elif is_ole:
            rows = load_xls()
        elif ext in [".xlsx", ".xlsm", ".xltx", ".xltm"]:
            rows = load_xlsx()
        elif ext == ".xls":
            rows = load_xls()
        else:
            raise ValueError("仅支持 xlsx/xls 文件")
        
        created_count = 0
        errors = []

        def normalize_cell(value):
            return str(value).strip() if value is not None else ""

        if not rows:
            return {"created": 0, "errors": ["Empty file"]}

        header = [normalize_cell(cell) for cell in rows[0]]
        header_map = {name: idx for idx, name in enumerate(header) if name}
        header_lower = {name.lower(): idx for name, idx in header_map.items()}

        def get_cell(row, key, lower=False):
            idx = header_lower.get(key.lower()) if lower else header_map.get(key)
            if idx is None or idx >= len(row):
                return ""
            return normalize_cell(row[idx])

        is_student_format = "学号" in header_map and "姓名" in header_map
        is_teacher_format = "tno" in header_lower and "tname" in header_lower

        college_items = DictionaryItem.objects.filter(
            dict_type__code="college"
        ).values_list("value", "label")
        college_map = {value: value for value, _ in college_items}
        college_map.update({label: value for value, label in college_items})

        def normalize_college(raw_value):
            raw_value = (raw_value or "").strip()
            if not raw_value:
                return ""
            return college_map.get(raw_value, raw_value)
        
        role_obj = Role.objects.filter(code=default_role).first()
        if not role_obj:
            role_obj = Role.objects.filter(code=User.UserRole.STUDENT).first()
        if not role_obj:
            raise ValueError("默认角色不存在")
        if role_obj.code == User.UserRole.EXPERT:
            raise ValueError("不支持直接导入专家，请先导入教师")

        with transaction.atomic():
            for row_idx, row in enumerate(rows[1:], start=2):
                if not any(cell is not None and str(cell).strip() for cell in row):
                    continue

                if is_student_format:
                    employee_id = get_cell(row, "学号")
                    real_name = get_cell(row, "姓名")
                elif is_teacher_format:
                    employee_id = get_cell(row, "Tno", lower=True)
                    real_name = get_cell(row, "TName", lower=True)
                else:
                    employee_id = normalize_cell(row[0]) if len(row) > 0 else ""
                    real_name = normalize_cell(row[1]) if len(row) > 1 else ""

                if not employee_id or not real_name:
                    continue

                if User.objects.filter(employee_id=employee_id).exists():
                    errors.append(f"Row {row_idx}: User {employee_id} already exists")
                    continue
                
                try:
                    college_value = ""
                    department_value = ""
                    major_value = ""
                    grade_value = ""
                    class_value = ""
                    gender_value = ""
                    title_value = ""
                    phone_value = ""
                    email_value = ""

                    if is_student_format:
                        college_value = normalize_college(get_cell(row, "单位名称"))
                        major_value = get_cell(row, "专业名称")
                        grade_value = get_cell(row, "当前年级")
                        class_value = get_cell(row, "班级")
                        gender_value = get_cell(row, "性别")
                    elif is_teacher_format:
                        college_value = normalize_college(get_cell(row, "Cname", lower=True))
                        department_value = college_value
                        title_value = get_cell(row, "Ranks", lower=True)
                    else:
                        college_value = normalize_college(
                            normalize_cell(row[2]) if len(row) > 2 else ""
                        )
                        major_value = normalize_cell(row[3]) if len(row) > 3 else ""
                        class_value = normalize_cell(row[4]) if len(row) > 4 else ""
                        phone_value = normalize_cell(row[5]) if len(row) > 5 else ""
                        email_value = normalize_cell(row[6]) if len(row) > 6 else ""

                    if default_college and not college_value:
                        college_value = normalize_college(default_college)

                    if gender_value not in ("男", "女"):
                        gender_value = ""

                    user_data = {
                        "employee_id": employee_id,
                        "real_name": real_name,
                        "username": employee_id,
                        "role_fk": role_obj,
                        "college": college_value,
                        "department": department_value,
                        "major": major_value,
                        "grade": grade_value,
                        "class_name": class_value,
                        "gender": gender_value,
                        "title": title_value,
                        "phone": phone_value,
                        "email": email_value,
                    }
                    user = User.objects.create(**user_data)
                    user.set_password("123456") # Default password
                    user.save()
                    created_count += 1
                except Exception as e:
                    errors.append(f"Row {row_idx}: {str(e)}")

        return {"created": created_count, "errors": errors}
