import base64
from io import BytesIO

import openpyxl  # type: ignore[import-untyped]
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import SimpleTestCase
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.dictionaries.models import DictionaryItem, DictionaryType
from apps.users.models import Role
from apps.users.serializers import UserSerializer
from apps.users.services.user_service import UserService


User = get_user_model()

PNG_1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAC0lEQVR4nGNgAAIAAAUAAXpeqz8AAAAASUVORK5CYII="
)


class UserAvatarUploadValidationTestCase(SimpleTestCase):
    def test_user_serializer_sanitizes_avatar_name(self):
        upload = SimpleUploadedFile(
            "../avatar.png",
            PNG_1X1,
            content_type="image/png",
        )
        field = UserSerializer().fields["avatar"]

        validated = field.run_validation(upload)

        self.assertEqual(validated.name, "avatar.png")

    def test_user_serializer_rejects_unsupported_avatar_extension(self):
        upload = SimpleUploadedFile(
            "avatar.gif",
            b"GIF89a",
            content_type="image/gif",
        )
        field = UserSerializer().fields["avatar"]

        with self.assertRaisesMessage(Exception, "头像仅支持"):
            field.run_validation(upload)

    def test_user_serializer_rejects_large_avatar(self):
        upload = SimpleUploadedFile(
            "avatar.png",
            b"0" * (5 * 1024 * 1024 + 1),
            content_type="image/png",
        )
        field = UserSerializer().fields["avatar"]

        with self.assertRaisesMessage(Exception, "头像文件大小不能超过5MB"):
            field.run_validation(upload)


@override_settings(DEFAULT_USER_PASSWORD="import-password-123")
class UserImportValidationTestCase(TestCase):
    def _student_workbook_upload(self):
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.append(["学号", "姓名", "单位名称", "专业名称", "当前年级", "班级", "性别"])
        sheet.append(["S20260001", "导入学生", "计算机学院", "软件工程", "2026", "1班", "男"])
        stream = BytesIO()
        workbook.save(stream)
        return SimpleUploadedFile(
            "users.xlsx",
            stream.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    def test_import_rejects_unsupported_extension(self):
        upload = SimpleUploadedFile(
            "users.txt",
            b"employee_id,real_name",
            content_type="text/plain",
        )

        with self.assertRaisesMessage(ValueError, "仅支持 xls/xlsx/xlsm/xltx/xltm 文件"):
            UserService().import_users(upload)

    def test_import_rejects_large_file(self):
        upload = SimpleUploadedFile(
            "users.xlsx",
            b"0" * (10 * 1024 * 1024 + 1),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        with self.assertRaisesMessage(ValueError, "导入文件不能超过 10MB"):
            UserService().import_users(upload)

    def test_import_sanitizes_path_like_filename_before_parsing(self):
        upload = SimpleUploadedFile(
            "../users.xlsx",
            b"not an excel file",
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        with self.assertRaisesMessage(ValueError, "导入文件格式错误"):
            UserService().import_users(upload)
        self.assertEqual(upload.name, "users.xlsx")

    def test_import_rejects_unknown_default_role(self):
        upload = self._student_workbook_upload()

        with self.assertRaisesMessage(ValueError, "导入角色不存在"):
            UserService().import_users(upload, default_role="NOT_A_ROLE")

    def test_import_reports_invalid_excel_content_as_validation_error(self):
        upload = SimpleUploadedFile(
            "users.xlsx",
            b"not an excel file",
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        with self.assertRaisesMessage(ValueError, "导入文件格式错误"):
            UserService().import_users(upload)


class AdminUserRoleValidationTestCase(TestCase):
    def setUp(self):
        college_type, _ = DictionaryType.objects.get_or_create(
            code="college",
            defaults={"name": "学院", "is_system": True},
        )
        self.cs_college, _ = DictionaryItem.objects.get_or_create(
            dict_type=college_type,
            value="计算机学院",
            defaults={"label": "计算机学院"},
        )
        self.ai_college, _ = DictionaryItem.objects.get_or_create(
            dict_type=college_type,
            value="人工智能学院",
            defaults={"label": "人工智能学院"},
        )
        level1_role, _ = Role.objects.get_or_create(
            code="LEVEL1_ADMIN",
            defaults={"name": "校级管理员", "scope_dimension": "SCHOOL"},
        )
        self.level2_role, _ = Role.objects.get_or_create(
            code="LEVEL2_ADMIN",
            defaults={"name": "学院管理员", "scope_dimension": "COLLEGE"},
        )
        level1_role.scope_dimension = "SCHOOL"
        level1_role.is_active = True
        level1_role.save(update_fields=["scope_dimension", "is_active"])
        self.level2_role.scope_dimension = "COLLEGE"
        self.level2_role.is_active = True
        self.level2_role.save(update_fields=["scope_dimension", "is_active"])
        self.custom_school_role, _ = Role.objects.get_or_create(
            code="SCHOOL_USER_DIRECTOR",
            defaults={"name": "校级用户主管", "scope_dimension": "SCHOOL"},
        )
        self.custom_school_role.scope_dimension = "SCHOOL"
        self.custom_school_role.is_active = True
        self.custom_school_role.save(update_fields=["scope_dimension", "is_active"])
        self.teacher_role, _ = Role.objects.get_or_create(
            code="TEACHER",
            defaults={"name": "指导教师"},
        )
        self.expert_role, _ = Role.objects.get_or_create(
            code="EXPERT",
            defaults={"name": "评审专家"},
        )
        self.admin = User.objects.create_user(
            username="user_admin",
            employee_id="UA10001",
            real_name="用户管理员",
            password="password123",
            role_fk=level1_role,
        )
        self.custom_school_admin = User.objects.create_user(
            username="custom_school_user_admin",
            employee_id="UA10002",
            real_name="校级用户主管",
            password="password123",
            role_fk=self.custom_school_role,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

    def _make_level1_admin_legacy(self):
        self.admin.role_fk.scope_dimension = None
        self.admin.role_fk.save(update_fields=["scope_dimension"])
        self.admin.refresh_from_db()

    def test_role_detail_supports_management_edit_form(self):
        response = self.client.get(f"/api/v1/auth/roles/{self.level2_role.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.level2_role.id)
        self.assertEqual(response.data["code"], self.level2_role.code)
        self.assertEqual(response.data["scope_dimension"], "COLLEGE")
        self.assertIn("user_count", response.data)

    def test_role_detail_requires_level1_admin(self):
        level2_admin = User.objects.create_user(
            username="role_detail_level2",
            employee_id="UR20001",
            real_name="角色详情二级管理员",
            password="password123",
            role_fk=self.level2_role,
        )
        self.client.force_authenticate(user=level2_admin)

        response = self.client.get(f"/api/v1/auth/roles/{self.level2_role.id}/")

        self.assertEqual(response.status_code, 403)

    def test_custom_school_admin_can_retrieve_role_detail(self):
        self.client.force_authenticate(user=self.custom_school_admin)

        response = self.client.get(f"/api/v1/auth/roles/{self.level2_role.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.level2_role.id)

    def test_create_rejects_expert_role_fk(self):
        response = self.client.post(
            "/api/v1/auth/admin/users/",
            {
                "employee_id": "UE10001",
                "real_name": "专家账号",
                "role_fk": self.expert_role.id,
                "password": "password123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("role", response.data["errors"])
        self.assertFalse(User.objects.filter(employee_id="UE10001").exists())

    def test_update_rejects_expert_role_fk(self):
        teacher = User.objects.create_user(
            username="teacher_user",
            employee_id="UT10001",
            real_name="教师账号",
            password="password123",
            role_fk=self.teacher_role,
        )

        response = self.client.patch(
            f"/api/v1/auth/admin/users/{teacher.id}/",
            {"role_fk": self.expert_role.id},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("role", response.data)
        teacher.refresh_from_db()
        self.assertEqual(teacher.role_fk_id, self.teacher_role.id)

    def test_create_college_admin_derives_college_from_managed_scope(self):
        response = self.client.post(
            "/api/v1/auth/admin/users/",
            {
                "employee_id": "UA20001",
                "real_name": "学院管理员",
                "role_fk": self.level2_role.id,
                "managed_scope_value": self.cs_college.id,
                "password": "password123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        user = User.objects.get(employee_id="UA20001")
        self.assertEqual(user.managed_scope_value_id, self.cs_college.id)
        self.assertEqual(user.college, "计算机学院")

    def test_custom_school_admin_lists_all_users(self):
        User.objects.create_user(
            username="school_scope_teacher",
            employee_id="UT20001",
            real_name="全校教师",
            password="password123",
            role_fk=self.teacher_role,
            college="人工智能学院",
        )
        User.objects.create_user(
            username="school_scope_student",
            employee_id="US20001",
            real_name="全校学生",
            password="password123",
            role_fk=Role.objects.get(code="STUDENT"),
            college="计算机学院",
        )
        self.client.force_authenticate(user=self.custom_school_admin)

        response = self.client.get("/api/v1/auth/admin/users/")

        self.assertEqual(response.status_code, 200)
        employee_ids = {
            item["employee_id"] for item in response.data["data"]["results"]
        }
        self.assertIn("UT20001", employee_ids)
        self.assertIn("US20001", employee_ids)

    def test_custom_school_admin_can_create_user(self):
        self.client.force_authenticate(user=self.custom_school_admin)

        response = self.client.post(
            "/api/v1/auth/admin/users/",
            {
                "employee_id": "US20002",
                "real_name": "自定义校级创建学生",
                "password": "password123",
                "role": "STUDENT",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(employee_id="US20002").exists())

    def test_legacy_level1_admin_without_scope_can_create_user(self):
        self._make_level1_admin_legacy()
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            "/api/v1/auth/admin/users/",
            {
                "employee_id": "US20003",
                "real_name": "旧校级创建学生",
                "password": "password123",
                "role": "STUDENT",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(employee_id="US20003").exists())

    def test_custom_school_admin_public_lookup_is_not_college_scoped(self):
        teacher = User.objects.create_user(
            username="school_lookup_teacher",
            employee_id="UT20002",
            real_name="跨学院教师",
            password="password123",
            role_fk=self.teacher_role,
            college="人工智能学院",
        )
        self.client.force_authenticate(user=self.custom_school_admin)

        response = self.client.get(
            "/api/v1/auth/users/",
            {
                "role": "TEACHER",
                "employee_id": teacher.employee_id,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["employee_id"], teacher.employee_id)

    def test_legacy_level1_admin_public_lookup_is_not_college_scoped(self):
        self._make_level1_admin_legacy()
        teacher = User.objects.create_user(
            username="legacy_lookup_teacher",
            employee_id="UT20004",
            real_name="旧校级跨学院教师",
            password="password123",
            role_fk=self.teacher_role,
            college="人工智能学院",
        )
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            "/api/v1/auth/users/",
            {
                "role": "TEACHER",
                "employee_id": teacher.employee_id,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["employee_id"], teacher.employee_id)

    def test_custom_scoped_admins_are_included_in_teacher_lookup(self):
        scoped_admin = User.objects.create_user(
            username="scoped_admin_teacher_lookup",
            employee_id="UA30001",
            real_name="自定义范围管理员",
            password="password123",
            role_fk=self.custom_school_role,
        )
        self.client.force_authenticate(user=self.custom_school_admin)

        response = self.client.get(
            "/api/v1/auth/users/",
            {
                "role": "TEACHER",
                "employee_id": scoped_admin.employee_id,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["employee_id"],
            scoped_admin.employee_id,
        )

    def test_user_statistics_counts_custom_admin_roles(self):
        self.client.force_authenticate(user=self.custom_school_admin)

        response = self.client.get("/api/v1/auth/admin/users/statistics/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"]["admin_count"], 2)

    def test_legacy_admin_roles_are_included_in_admin_filters_and_statistics(self):
        self._make_level1_admin_legacy()
        self.client.force_authenticate(user=self.admin)

        list_response = self.client.get(
            "/api/v1/auth/admin/users/",
            {"is_admin": "true"},
        )
        stats_response = self.client.get("/api/v1/auth/admin/users/statistics/")

        self.assertEqual(list_response.status_code, 200)
        employee_ids = {
            item["employee_id"]
            for item in list_response.data["data"]["results"]
        }
        self.assertIn(self.admin.employee_id, employee_ids)
        self.assertEqual(stats_response.status_code, 200)
        self.assertEqual(stats_response.data["data"]["admin_count"], 2)

    def test_update_college_admin_derives_college_from_managed_scope(self):
        admin = User.objects.create_user(
            username="college_admin",
            employee_id="UA20002",
            real_name="学院管理员",
            password="password123",
            role_fk=self.level2_role,
            managed_scope_value=self.cs_college,
            college="计算机学院",
        )

        response = self.client.patch(
            f"/api/v1/auth/admin/users/{admin.id}/",
            {"managed_scope_value": self.ai_college.id},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        admin.refresh_from_db()
        self.assertEqual(admin.managed_scope_value_id, self.ai_college.id)
        self.assertEqual(admin.college, "人工智能学院")

    def test_update_college_admin_rejects_scope_college_mismatch(self):
        admin = User.objects.create_user(
            username="mismatch_admin",
            employee_id="UA20003",
            real_name="学院管理员",
            password="password123",
            role_fk=self.level2_role,
            managed_scope_value=self.cs_college,
            college="计算机学院",
        )

        response = self.client.patch(
            f"/api/v1/auth/admin/users/{admin.id}/",
            {
                "managed_scope_value": self.ai_college.id,
                "college": "计算机学院",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("college", response.data)
        admin.refresh_from_db()
        self.assertEqual(admin.managed_scope_value_id, self.cs_college.id)
        self.assertEqual(admin.college, "计算机学院")
