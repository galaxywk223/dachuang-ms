from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.dictionaries.models import DictionaryItem, DictionaryType
from apps.notifications.models import Notification, PlatformMaterial, PlatformNotice
from apps.notifications.serializers import (
    NotificationSerializer,
    PlatformMaterialSerializer,
    PlatformNoticeSerializer,
)
from apps.users.models import Role


User = get_user_model()


class PlatformMaterialUploadValidationTestCase(SimpleTestCase):
    def test_material_serializer_sanitizes_path_like_upload_name(self):
        upload = SimpleUploadedFile(
            "../guide.pdf",
            b"%PDF-1.4\ncontent",
            content_type="application/pdf",
        )
        serializer = PlatformMaterialSerializer()

        validated = serializer.validate_file(upload)

        self.assertEqual(validated.name, "guide.pdf")

    def test_material_serializer_rejects_unsupported_extension(self):
        upload = SimpleUploadedFile(
            "guide.exe",
            b"not allowed",
            content_type="application/octet-stream",
        )
        serializer = PlatformMaterialSerializer()

        with self.assertRaisesMessage(Exception, "资料仅支持"):
            serializer.validate_file(upload)

    def test_material_serializer_rejects_empty_file(self):
        upload = SimpleUploadedFile(
            "guide.pdf",
            b"",
            content_type="application/pdf",
        )
        serializer = PlatformMaterialSerializer()

        with self.assertRaisesMessage(Exception, "资料不能为空"):
            serializer.validate_file(upload)

    def test_material_serializer_rejects_large_file(self):
        upload = SimpleUploadedFile(
            "guide.pdf",
            b"0" * (20 * 1024 * 1024 + 1),
            content_type="application/pdf",
        )
        serializer = PlatformMaterialSerializer()

        with self.assertRaisesMessage(Exception, "资料文件大小不能超过20MB"):
            serializer.validate_file(upload)


class NotificationBatchSendValidationTestCase(TestCase):
    def setUp(self):
        self.level1_role, _ = Role.objects.get_or_create(
            code="LEVEL1_ADMIN",
            defaults={"name": "校级管理员", "scope_dimension": "SCHOOL"},
        )
        self.level2_role, _ = Role.objects.get_or_create(
            code="LEVEL2_ADMIN",
            defaults={"name": "学院管理员", "scope_dimension": "COLLEGE"},
        )
        self.student_role, _ = Role.objects.get_or_create(
            code="STUDENT",
            defaults={"name": "学生"},
        )
        self.level1_role.scope_dimension = "SCHOOL"
        self.level1_role.is_active = True
        self.level1_role.save(update_fields=["scope_dimension", "is_active"])
        self.level2_role.scope_dimension = "COLLEGE"
        self.level2_role.is_active = True
        self.level2_role.save(update_fields=["scope_dimension", "is_active"])
        self.level1_admin = User.objects.create_user(
            username="notice_level1",
            employee_id="N10001",
            real_name="校级管理员",
            password="password123",
            role_fk=self.level1_role,
        )
        self.level2_admin_without_college = User.objects.create_user(
            username="notice_level2",
            employee_id="N20001",
            real_name="学院管理员",
            password="password123",
            role_fk=self.level2_role,
        )
        self.student = User.objects.create_user(
            username="notice_student",
            employee_id="N30001",
            real_name="通知学生",
            password="password123",
            role_fk=self.student_role,
        )
        self.client = APIClient()

    def test_batch_send_rejects_non_list_recipients_without_broadcasting(self):
        self.client.force_authenticate(user=self.level1_admin)

        response = self.client.post(
            "/api/v1/notifications/batch-send/",
            {
                "title": "系统通知",
                "content": "通知内容",
                "recipients": str(self.student.id),
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["message"], "接收人列表不合法")
        self.assertEqual(Notification.objects.count(), 0)

    def test_batch_send_rejects_college_admin_without_college(self):
        self.client.force_authenticate(user=self.level2_admin_without_college)

        response = self.client.post(
            "/api/v1/notifications/batch-send/",
            {
                "title": "学院通知",
                "content": "通知内容",
                "recipients": [self.student.id],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["message"], "当前账号未设置学院信息")
        self.assertEqual(Notification.objects.count(), 0)


class PlatformAudienceValidationTestCase(TestCase):
    def setUp(self):
        self.student_role, _ = Role.objects.get_or_create(
            code="STUDENT",
            defaults={"name": "学生"},
        )
        self.teacher_role, _ = Role.objects.get_or_create(
            code="TEACHER",
            defaults={"name": "教师"},
        )
        self.student_role.is_active = True
        self.teacher_role.is_active = True
        self.student_role.save(update_fields=["is_active"])
        self.teacher_role.save(update_fields=["is_active"])

    def test_notice_target_roles_rejects_non_list_payload(self):
        serializer = PlatformNoticeSerializer(
            data={
                "title": "公告",
                "content": "公告内容",
                "target_roles": "STUDENT",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("target_roles", serializer.errors)

    def test_material_target_roles_rejects_unknown_role(self):
        serializer = PlatformMaterialSerializer(
            data={
                "title": "资料",
                "target_roles": ["STUDENT", "UNKNOWN_ROLE"],
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("target_roles", serializer.errors)

    def test_notice_target_roles_normalizes_duplicates(self):
        serializer = PlatformNoticeSerializer(
            data={
                "title": "公告",
                "content": "公告内容",
                "target_roles": ["STUDENT", "STUDENT", "TEACHER", ""],
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(
            serializer.validated_data["target_roles"],
            ["STUDENT", "TEACHER"],
        )


class PlatformAudienceVisibilityTestCase(TestCase):
    def setUp(self):
        self.level1_role, _ = Role.objects.get_or_create(
            code="LEVEL1_ADMIN",
            defaults={"name": "校级管理员", "scope_dimension": "SCHOOL"},
        )
        self.level2_role, _ = Role.objects.get_or_create(
            code="LEVEL2_ADMIN",
            defaults={"name": "学院管理员", "scope_dimension": "COLLEGE"},
        )
        self.custom_school_role, _ = Role.objects.get_or_create(
            code="SCHOOL_NOTICE_ADMIN",
            defaults={"name": "校级公告管理员", "scope_dimension": "SCHOOL"},
        )
        self.custom_college_role, _ = Role.objects.get_or_create(
            code="COLLEGE_NOTICE_ADMIN",
            defaults={"name": "学院公告管理员", "scope_dimension": "COLLEGE"},
        )
        for role, scope_dimension in (
            (self.level1_role, "SCHOOL"),
            (self.level2_role, "COLLEGE"),
            (self.custom_school_role, "SCHOOL"),
            (self.custom_college_role, "COLLEGE"),
        ):
            role.scope_dimension = scope_dimension
            role.is_active = True
            role.save(update_fields=["scope_dimension", "is_active"])

        self.custom_school_admin = User.objects.create_user(
            username="custom_notice_school",
            employee_id="PN10001",
            real_name="校级公告管理员",
            password="password123",
            role_fk=self.custom_school_role,
        )
        self.custom_college_admin = User.objects.create_user(
            username="custom_notice_college",
            employee_id="PN20001",
            real_name="学院公告管理员",
            password="password123",
            role_fk=self.custom_college_role,
            college="计算机学院",
        )
        self.client = APIClient()

    def test_custom_school_admin_sees_legacy_level1_target_notice(self):
        visible_notice = PlatformNotice.objects.create(
            title="校级公告",
            content="公告内容",
            target_roles=[User.UserRole.LEVEL1_ADMIN],
            status=PlatformNotice.NoticeStatus.PUBLISHED,
        )
        hidden_notice = PlatformNotice.objects.create(
            title="院级公告",
            content="公告内容",
            target_roles=[User.UserRole.LEVEL2_ADMIN],
            status=PlatformNotice.NoticeStatus.PUBLISHED,
        )
        self.client.force_authenticate(user=self.custom_school_admin)

        response = self.client.get("/api/v1/notifications/notices/")

        self.assertEqual(response.status_code, 200)
        notice_ids = {item["id"] for item in response.data["results"]}
        self.assertIn(visible_notice.id, notice_ids)
        self.assertNotIn(hidden_notice.id, notice_ids)

    def test_custom_college_admin_sees_legacy_level2_target_material(self):
        visible_material = PlatformMaterial.objects.create(
            title="院级资料",
            target_roles=[User.UserRole.LEVEL2_ADMIN],
            is_active=True,
        )
        hidden_material = PlatformMaterial.objects.create(
            title="校级资料",
            target_roles=[User.UserRole.LEVEL1_ADMIN],
            is_active=True,
        )
        self.client.force_authenticate(user=self.custom_college_admin)

        response = self.client.get("/api/v1/notifications/materials/")

        self.assertEqual(response.status_code, 200)
        material_ids = {item["id"] for item in response.data["results"]}
        self.assertIn(visible_material.id, material_ids)
        self.assertNotIn(hidden_material.id, material_ids)


class PlatformMaterialProjectTemplateTestCase(TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory(ignore_cleanup_errors=True)
        self.settings_override = override_settings(MEDIA_ROOT=self.temp_dir.name)
        self.settings_override.enable()
        self.student_role, _ = Role.objects.get_or_create(
            code="STUDENT",
            defaults={"name": "学生"},
        )
        self.student_role.is_active = True
        self.student_role.save(update_fields=["is_active"])
        self.student = User.objects.create_user(
            username="material_template_student",
            employee_id="PMT30001",
            real_name="资料学生",
            password="password123",
            role_fk=self.student_role,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.student)

    def tearDown(self):
        self.settings_override.disable()
        self.temp_dir.cleanup()

    def test_materials_include_project_type_template(self):
        dict_type, _ = DictionaryType.objects.get_or_create(
            code="project_type",
            defaults={"name": "项目类型", "is_system": True},
        )
        item = DictionaryItem.objects.create(
            dict_type=dict_type,
            value="template_test_innovation",
            label="创新训练项目",
            description="模板说明",
        )
        item.template_file.save(
            "innovation-template.pdf",
            SimpleUploadedFile(
                "innovation-template.pdf",
                b"%PDF-1.4\ncontent",
                content_type="application/pdf",
            ),
            save=True,
        )

        response = self.client.get("/api/v1/notifications/materials/")

        self.assertEqual(response.status_code, 200)
        template_rows = [
            row
            for row in response.data["results"]
            if row["id"] == f"project_template_{item.id}"
        ]
        self.assertEqual(len(template_rows), 1)
        self.assertEqual(template_rows[0]["title"], "创新训练项目申请书模板")
        self.assertEqual(template_rows[0]["category"], "申请书模板")
        self.assertIn(
            f"/api/v1/notifications/materials/project_template_{item.id}/download/",
            template_rows[0]["file_url"],
        )

    def test_project_type_template_download_returns_file(self):
        dict_type, _ = DictionaryType.objects.get_or_create(
            code="project_type",
            defaults={"name": "项目类型", "is_system": True},
        )
        item = DictionaryItem.objects.create(
            dict_type=dict_type,
            value="template_test_innovation_download",
            label="创新训练项目",
        )
        item.template_file.save(
            "innovation-template.pdf",
            SimpleUploadedFile(
                "innovation-template.pdf",
                b"%PDF-1.4\ncontent",
                content_type="application/pdf",
            ),
            save=True,
        )
        response = self.client.get(
            f"/api/v1/notifications/materials/project_template_{item.id}/download/"
        )

        try:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response["Content-Type"], "application/pdf")
        finally:
            response.close()


class PlatformNoticePublishLifecycleTestCase(TestCase):
    def setUp(self):
        self.level1_role, _ = Role.objects.get_or_create(
            code="LEVEL1_ADMIN",
            defaults={"name": "校级管理员", "scope_dimension": "SCHOOL"},
        )
        self.level1_role.scope_dimension = "SCHOOL"
        self.level1_role.is_active = True
        self.level1_role.save(update_fields=["scope_dimension", "is_active"])
        self.admin = User.objects.create_user(
            username="notice_lifecycle_admin",
            employee_id="NL10001",
            real_name="公告管理员",
            password="password123",
            role_fk=self.level1_role,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

    def test_create_default_published_notice_sets_published_at(self):
        response = self.client.post(
            "/api/v1/notifications/notices/",
            {"title": "默认发布公告", "content": "公告内容"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        notice = PlatformNotice.objects.get(id=response.data["data"]["id"])
        self.assertEqual(notice.status, PlatformNotice.NoticeStatus.PUBLISHED)
        self.assertIsNotNone(notice.published_at)

    def test_patch_draft_notice_to_published_sets_published_at(self):
        notice = PlatformNotice.objects.create(
            title="草稿公告",
            content="公告内容",
            status=PlatformNotice.NoticeStatus.DRAFT,
            created_by=self.admin,
        )

        response = self.client.patch(
            f"/api/v1/notifications/notices/{notice.id}/",
            {"status": PlatformNotice.NoticeStatus.PUBLISHED},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        notice.refresh_from_db()
        self.assertEqual(notice.status, PlatformNotice.NoticeStatus.PUBLISHED)
        self.assertIsNotNone(notice.published_at)


class NotificationSerializerContractTestCase(TestCase):
    def setUp(self):
        self.student_role, _ = Role.objects.get_or_create(
            code="STUDENT",
            defaults={"name": "学生"},
        )
        self.student = User.objects.create_user(
            username="notification_contract_student",
            employee_id="NS10001",
            real_name="通知字段学生",
            password="password123",
            role_fk=self.student_role,
        )

    def test_notification_includes_frontend_display_alias(self):
        notification = Notification.objects.create(
            recipient=self.student,
            title="审核通知",
            content="通知内容",
            notification_type=Notification.NotificationType.REVIEW,
        )

        data = NotificationSerializer(notification).data

        self.assertEqual(data["type_display"], "审核通知")
        self.assertEqual(data["notification_type_display"], "审核通知")
