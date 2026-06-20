import base64

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase
from django.test import TestCase
from rest_framework.test import APIClient

from apps.projects.models import Project
from apps.system_settings.models import (
    CertificateSetting,
    ProjectBatch,
    SystemSetting,
    WorkflowConfig,
    WorkflowNode,
)
from apps.system_settings.serializers import CertificateSettingSerializer
from apps.users.models import Role


PNG_1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAC0lEQVR4nGNgAAIAAAUAAXpeqz8AAAAASUVORK5CYII="
)


class CertificateImageUploadValidationTestCase(SimpleTestCase):
    def test_certificate_serializer_sanitizes_background_image_name(self):
        upload = SimpleUploadedFile(
            "../background.png",
            PNG_1X1,
            content_type="image/png",
        )
        field = CertificateSettingSerializer().fields["background_image"]

        validated = field.run_validation(upload)

        self.assertEqual(validated.name, "background.png")

    def test_certificate_serializer_rejects_unsupported_background_extension(self):
        upload = SimpleUploadedFile(
            "background.svg",
            b"<svg></svg>",
            content_type="image/svg+xml",
        )
        field = CertificateSettingSerializer().fields["background_image"]

        with self.assertRaisesMessage(Exception, "证书底图仅支持"):
            field.run_validation(upload)

    def test_certificate_serializer_rejects_large_seal_image(self):
        upload = SimpleUploadedFile(
            "seal.png",
            b"0" * (5 * 1024 * 1024 + 1),
            content_type="image/png",
        )
        field = CertificateSettingSerializer().fields["seal_image"]

        with self.assertRaisesMessage(Exception, "电子印章文件大小不能超过5MB"):
            field.run_validation(upload)

    def test_certificate_serializer_rejects_empty_seal_image(self):
        upload = SimpleUploadedFile(
            "seal.png",
            b"",
            content_type="image/png",
        )
        field = CertificateSettingSerializer().fields["seal_image"]

        with self.assertRaisesMessage(Exception, "电子印章不能为空"):
            field.run_validation(upload)


User = get_user_model()


class BatchWorkflowViewSetTestCase(TestCase):
    def setUp(self):
        self.student_role = self._role("STUDENT", "学生")
        self.teacher_role = self._role("TEACHER", "教师")
        self.admin_role = self._role("LEVEL1_ADMIN", "校级管理员", "SCHOOL")
        self.admin = User.objects.create_user(
            username="workflow-admin",
            password="123456",
            role_fk=self.admin_role,
            real_name="Workflow Admin",
            employee_id="WF1001",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)
        self.batch = ProjectBatch.objects.create(
            name="2026",
            year=2026,
            code="WF2026",
            status=ProjectBatch.STATUS_ACTIVE,
            is_active=True,
            is_current=True,
        )
        self.workflow = WorkflowConfig.objects.create(
            name="Application Workflow",
            phase=WorkflowConfig.Phase.APPLICATION,
            batch=self.batch,
            version=1,
            is_active=True,
        )
        self.submit_node = WorkflowNode.objects.create(
            workflow=self.workflow,
            code="SUBMIT",
            name="提交",
            node_type=WorkflowNode.NodeType.SUBMIT,
            role_fk=self.student_role,
            sort_order=1,
        )
        self.review_node = WorkflowNode.objects.create(
            workflow=self.workflow,
            code="REVIEW",
            name="审核",
            node_type=WorkflowNode.NodeType.REVIEW,
            role_fk=self.teacher_role,
            sort_order=2,
            allowed_reject_to=self.submit_node.id,
        )

    def _role(self, code, name, scope_dimension=None):
        role, _ = Role.objects.get_or_create(code=code, defaults={"name": name})
        role.name = name
        role.scope_dimension = scope_dimension
        role.is_active = True
        role.save(update_fields=["name", "scope_dimension", "is_active"])
        return role

    def _reorder_url(self):
        return (
            f"/api/v1/system/batch-workflows/{self.batch.id}/"
            "workflows/APPLICATION/nodes/reorder/"
        )

    def _nodes_url(self):
        return (
            f"/api/v1/system/batch-workflows/{self.batch.id}/"
            "workflows/APPLICATION/nodes/"
        )

    def _node_url(self, node):
        return (
            f"/api/v1/system/batch-workflows/{self.batch.id}/"
            f"workflows/APPLICATION/nodes/{node.id}/"
        )

    def test_reorder_nodes_rejects_invalid_node_ids(self):
        response = self.client.post(
            self._reorder_url(),
            {"node_ids": [self.submit_node.id, "bad"]},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["detail"], "节点ID列表不合法")

    def test_reorder_nodes_rejects_duplicate_node_ids(self):
        response = self.client.post(
            self._reorder_url(),
            {"node_ids": [self.submit_node.id, self.submit_node.id]},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["detail"], "节点ID不能重复")

    def test_list_nodes_rejects_invalid_batch_id(self):
        response = self.client.get(
            "/api/v1/system/batch-workflows/bad/workflows/APPLICATION/nodes/"
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["detail"], "批次ID不合法")

    def test_update_node_rejects_invalid_node_id(self):
        response = self.client.patch(
            f"/api/v1/system/batch-workflows/{self.batch.id}/"
            "workflows/APPLICATION/nodes/bad/",
            {"name": "无效节点"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["detail"], "节点ID不合法")

    def test_init_workflow_rejects_unknown_phase(self):
        response = self.client.post(
            f"/api/v1/system/batch-workflows/{self.batch.id}/workflows/UNKNOWN/init/"
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["detail"], "流程阶段不合法")
        self.assertFalse(
            WorkflowConfig.objects.filter(batch=self.batch, phase="UNKNOWN").exists()
        )

    def test_create_node_rejects_return_target_from_other_workflow(self):
        other_workflow = WorkflowConfig.objects.create(
            name="Other Workflow",
            phase=WorkflowConfig.Phase.MID_TERM,
            batch=self.batch,
            version=1,
            is_active=True,
        )
        other_node = WorkflowNode.objects.create(
            workflow=other_workflow,
            code="OTHER_SUBMIT",
            name="其他提交",
            node_type=WorkflowNode.NodeType.SUBMIT,
            role_fk=self.student_role,
            sort_order=0,
        )

        response = self.client.post(
            self._nodes_url(),
            {
                "code": "INVALID_TARGET",
                "name": "无效退回目标",
                "node_type": WorkflowNode.NodeType.REVIEW,
                "role_fk": self.teacher_role.id,
                "sort_order": 3,
                "allowed_reject_to": other_node.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("退回目标节点不存在", str(response.data))
        self.assertFalse(
            WorkflowNode.objects.filter(
                workflow=self.workflow, code="INVALID_TARGET"
            ).exists()
        )

    def test_update_node_rejects_later_return_target(self):
        later_node = WorkflowNode.objects.create(
            workflow=self.workflow,
            code="LATER_REVIEW",
            name="后续审核",
            node_type=WorkflowNode.NodeType.REVIEW,
            role_fk=self.admin_role,
            sort_order=3,
            allowed_reject_to=self.review_node.id,
        )

        response = self.client.patch(
            self._node_url(self.review_node),
            {"allowed_reject_to": later_node.id},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("退回目标必须为前序节点", str(response.data))
        self.review_node.refresh_from_db()
        self.assertEqual(self.review_node.allowed_reject_to, self.submit_node.id)


class SystemSettingViewSetTestCase(TestCase):
    def setUp(self):
        self.admin_role = self._role("LEVEL1_ADMIN", "校级管理员", "SCHOOL")
        self.custom_school_role = self._role(
            "SCHOOL_SETTINGS_DIRECTOR",
            "校级配置主管",
            "SCHOOL",
        )
        self.admin = User.objects.create_user(
            username="settings-admin",
            password="123456",
            role_fk=self.admin_role,
            real_name="Settings Admin",
            employee_id="SS1001",
        )
        self.custom_school_admin = User.objects.create_user(
            username="custom-settings-admin",
            password="123456",
            role_fk=self.custom_school_role,
            real_name="Custom Settings Admin",
            employee_id="SS1002",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

    def _role(self, code, name, scope_dimension=None):
        role, _ = Role.objects.get_or_create(code=code, defaults={"name": name})
        role.name = name
        role.scope_dimension = scope_dimension
        role.is_active = True
        role.save(update_fields=["name", "scope_dimension", "is_active"])
        return role

    def test_effective_settings_reject_invalid_batch_id(self):
        response = self.client.get(
            "/api/v1/system/settings/effective/",
            {"batch_id": "invalid"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["message"], "批次参数不合法")

    def test_effective_settings_rejects_missing_batch_id(self):
        response = self.client.get(
            "/api/v1/system/settings/effective/",
            {"batch_id": "999999"},
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["message"], "批次不存在")

    def test_upsert_by_code_rejects_missing_batch_without_global_write(self):
        response = self.client.put(
            "/api/v1/system/settings/by-code/APPLICATION_WINDOW/",
            {"batch": 999999, "name": "立项时间窗口", "data": {"enabled": True}},
            format="json",
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["message"], "批次不存在")
        self.assertFalse(
            SystemSetting.objects.filter(
                code="APPLICATION_WINDOW", batch__isnull=True
            ).exists()
        )

    def test_custom_school_admin_can_access_effective_settings(self):
        self.client.force_authenticate(user=self.custom_school_admin)

        response = self.client.get("/api/v1/system-settings/settings/effective/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["message"], "获取成功")
        self.assertIn("APPLICATION_WINDOW", response.data["data"])


class CertificateSettingViewSetTestCase(TestCase):
    def setUp(self):
        self.admin_role = self._role("LEVEL1_ADMIN", "校级管理员", "SCHOOL")
        self.admin = User.objects.create_user(
            username="certificate-admin",
            password="123456",
            role_fk=self.admin_role,
            real_name="Certificate Admin",
            employee_id="CS1001",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

    def _role(self, code, name, scope_dimension=None):
        role, _ = Role.objects.get_or_create(code=code, defaults={"name": name})
        role.name = name
        role.scope_dimension = scope_dimension
        role.is_active = True
        role.save(update_fields=["name", "scope_dimension", "is_active"])
        return role

    def test_create_rejects_duplicate_active_certificate_scope(self):
        CertificateSetting.objects.create(
            name="默认模板",
            school_name="测试大学",
            issuer_name="教务处",
            is_active=True,
        )

        response = self.client.post(
            "/api/v1/system-settings/certificates/",
            {
                "name": "重复默认模板",
                "school_name": "测试大学",
                "issuer_name": "教务处",
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("is_active", response.data)
        self.assertEqual(CertificateSetting.objects.count(), 1)

    def test_inactive_duplicate_certificate_scope_can_be_saved(self):
        CertificateSetting.objects.create(
            name="默认模板",
            school_name="测试大学",
            issuer_name="教务处",
            is_active=True,
        )

        response = self.client.post(
            "/api/v1/system-settings/certificates/",
            {
                "name": "停用默认模板",
                "school_name": "测试大学",
                "issuer_name": "教务处",
                "is_active": False,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(CertificateSetting.objects.count(), 2)

    def test_update_rejects_enabling_duplicate_certificate_scope(self):
        CertificateSetting.objects.create(
            name="默认模板",
            school_name="测试大学",
            issuer_name="教务处",
            is_active=True,
        )
        inactive = CertificateSetting.objects.create(
            name="停用默认模板",
            school_name="测试大学",
            issuer_name="教务处",
            is_active=False,
        )

        response = self.client.patch(
            f"/api/v1/system-settings/certificates/{inactive.id}/",
            {"is_active": True},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("is_active", response.data)
        inactive.refresh_from_db()
        self.assertFalse(inactive.is_active)


class ProjectBatchViewSetTestCase(TestCase):
    def setUp(self):
        self.student_role = self._role("STUDENT", "学生")
        self.admin_role = self._role("LEVEL1_ADMIN", "校级管理员", "SCHOOL")
        self.custom_school_role = self._role(
            "SCHOOL_BATCH_DIRECTOR",
            "校级批次主管",
            "SCHOOL",
        )
        self.admin = User.objects.create_user(
            username="batch-admin",
            password="123456",
            role_fk=self.admin_role,
            real_name="Batch Admin",
            employee_id="PB1001",
        )
        self.custom_school_admin = User.objects.create_user(
            username="custom-batch-admin",
            password="123456",
            role_fk=self.custom_school_role,
            real_name="Custom Batch Admin",
            employee_id="PB1002",
        )
        self.student = User.objects.create_user(
            username="batch-student",
            password="123456",
            role_fk=self.student_role,
            real_name="Batch Student",
            employee_id="PB2001",
            college="计算机学院",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

    def _role(self, code, name, scope_dimension=None):
        role, _ = Role.objects.get_or_create(code=code, defaults={"name": name})
        role.name = name
        role.scope_dimension = scope_dimension
        role.is_active = True
        role.save(update_fields=["name", "scope_dimension", "is_active"])
        return role

    def test_delete_archived_batch_with_projects_preserves_history_link(self):
        batch = ProjectBatch.objects.create(
            name="2025",
            year=2025,
            code="PB2025",
            status=ProjectBatch.STATUS_ARCHIVED,
            is_active=False,
            is_current=False,
        )
        project = Project.objects.create(
            project_no="PB20250001",
            title="历史批次项目",
            leader=self.student,
            status=Project.ProjectStatus.CLOSED,
            year=2025,
            batch=batch,
        )

        response = self.client.delete(f"/api/v1/system-settings/batches/{batch.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(ProjectBatch.objects.filter(id=batch.id).exists())
        batch.refresh_from_db()
        project.refresh_from_db()
        self.assertTrue(batch.is_deleted)
        self.assertFalse(batch.is_active)
        self.assertFalse(batch.is_current)
        self.assertEqual(project.batch_id, batch.id)

    def test_non_admin_list_cannot_include_deleted_batches(self):
        deleted_batch = ProjectBatch.objects.create(
            name="2024",
            year=2024,
            code="PB2024-DELETED",
            status=ProjectBatch.STATUS_ARCHIVED,
            is_active=False,
            is_current=False,
            is_deleted=True,
        )
        self.client.force_authenticate(user=self.student)

        response = self.client.get(
            "/api/v1/system-settings/batches/",
            {"include_deleted": "1", "include_archived": "1"},
        )

        self.assertEqual(response.status_code, 200)
        ids = {item["id"] for item in response.data["data"]}
        self.assertNotIn(deleted_batch.id, ids)

    def test_custom_school_admin_can_include_deleted_batches(self):
        deleted_batch = ProjectBatch.objects.create(
            name="2024",
            year=2024,
            code="PB2024-CUSTOM-DELETED",
            status=ProjectBatch.STATUS_ARCHIVED,
            is_active=False,
            is_current=False,
            is_deleted=True,
        )
        self.client.force_authenticate(user=self.custom_school_admin)

        response = self.client.get(
            "/api/v1/system-settings/batches/",
            {"include_deleted": "1", "include_archived": "1"},
        )

        self.assertEqual(response.status_code, 200)
        ids = {item["id"] for item in response.data["data"]}
        self.assertIn(deleted_batch.id, ids)

    def test_non_admin_cannot_retrieve_batch_detail(self):
        batch = ProjectBatch.objects.create(
            name="2026",
            year=2026,
            code="PB2026-DETAIL",
            status=ProjectBatch.STATUS_ACTIVE,
            is_active=True,
            is_current=True,
        )
        self.client.force_authenticate(user=self.student)

        response = self.client.get(f"/api/v1/system-settings/batches/{batch.id}/")

        self.assertEqual(response.status_code, 403)
