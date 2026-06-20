from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, TestCase, override_settings
from rest_framework.test import APIClient

from apps.dictionaries.models import DictionaryItem, DictionaryType
from apps.dictionaries.serializers import DictionaryItemSerializer
from apps.users.models import Role


User = get_user_model()


class DictionaryTemplateUploadValidationTestCase(SimpleTestCase):
    def test_dictionary_serializer_sanitizes_template_file_name(self):
        upload = SimpleUploadedFile(
            "../template.docx",
            b"document",
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        serializer = DictionaryItemSerializer()

        validated = serializer.validate_template_file(upload)

        self.assertEqual(validated.name, "template.docx")

    def test_dictionary_serializer_rejects_unsupported_template_extension(self):
        upload = SimpleUploadedFile(
            "template.exe",
            b"not allowed",
            content_type="application/octet-stream",
        )
        serializer = DictionaryItemSerializer()

        with self.assertRaisesMessage(Exception, "模板文件仅支持"):
            serializer.validate_template_file(upload)

    def test_dictionary_serializer_rejects_empty_template_file(self):
        upload = SimpleUploadedFile(
            "template.pdf",
            b"",
            content_type="application/pdf",
        )
        serializer = DictionaryItemSerializer()

        with self.assertRaisesMessage(Exception, "模板文件不能为空"):
            serializer.validate_template_file(upload)

    def test_dictionary_serializer_rejects_large_template_file(self):
        upload = SimpleUploadedFile(
            "template.pdf",
            b"0" * (5 * 1024 * 1024 + 1),
            content_type="application/pdf",
        )
        serializer = DictionaryItemSerializer()

        with self.assertRaisesMessage(Exception, "模板文件文件大小不能超过5MB"):
            serializer.validate_template_file(upload)


class DictionarySeedDataTestCase(TestCase):
    def test_teacher_staff_title_is_seeded(self):
        self.assertTrue(
            DictionaryItem.objects.filter(
                dict_type__code="title",
                value="教工",
                label="教工",
                is_active=True,
            ).exists()
        )


class DictionaryItemApiValidationTestCase(TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.settings_override = override_settings(MEDIA_ROOT=self.temp_dir.name)
        self.settings_override.enable()
        role, _ = Role.objects.get_or_create(
            code="LEVEL1_ADMIN",
            defaults={"name": "校级管理员", "scope_dimension": "SCHOOL"},
        )
        role.scope_dimension = "SCHOOL"
        role.is_active = True
        role.save(update_fields=["scope_dimension", "is_active"])
        self.admin = User.objects.create_user(
            username="dictionary_admin",
            password="password123",
            role_fk=role,
            real_name="字典管理员",
            employee_id="D10001",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

    def tearDown(self):
        self.settings_override.disable()
        self.temp_dir.cleanup()

    def test_bulk_create_rejects_invalid_dict_type_id(self):
        response = self.client.post(
            "/api/v1/dictionaries/items/bulk/",
            {"dict_type": "invalid", "items": [{"label": "测试项", "value": "TEST"}]},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["detail"], "字典类型不存在")

    def test_item_list_tolerates_invalid_dict_type_filter(self):
        response = self.client.get(
            "/api/v1/dictionaries/items/",
            {"dict_type": "invalid"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_by_code_includes_project_type_template_file(self):
        dict_type, _ = DictionaryType.objects.get_or_create(
            code="project_type",
            defaults={
                "name": "项目类型",
                "is_system": True,
            },
        )
        item = DictionaryItem.objects.create(
            dict_type=dict_type,
            value="template_test_innovation",
            label="创新训练项目",
            description="创新训练项目申请书模板",
        )
        item.template_file.save(
            "innovation-template.docx",
            SimpleUploadedFile(
                "innovation-template.docx",
                b"document",
                content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ),
            save=True,
        )

        response = self.client.get("/api/v1/dictionaries/types/by-code/project_type/")

        self.assertEqual(response.status_code, 200)
        response_item = next(
            row
            for row in response.data["items"]
            if row["value"] == "template_test_innovation"
        )
        self.assertEqual(response_item["label"], "创新训练项目")
        self.assertEqual(response_item["description"], "创新训练项目申请书模板")
        self.assertIn(
            "dictionary_templates/innovation-template",
            response_item["template_file"],
        )
