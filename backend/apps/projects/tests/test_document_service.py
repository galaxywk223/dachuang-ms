from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.projects.certificates import render_certificate_html
from apps.projects.models import Project
from apps.projects.services.document import DocumentService
from apps.projects.views.mixins.project_admin_export_documents_mixin import (
    ProjectAdminExportDocumentsMixin,
)
from apps.system_settings.models import CertificateSetting, ProjectBatch
from apps.users.models import Role


User = get_user_model()


class DocumentServiceTestCase(TestCase):
    def setUp(self):
        student_role, _ = Role.objects.get_or_create(
            code="STUDENT",
            defaults={"name": "学生"},
        )
        self.student = User.objects.create_user(
            username="document_student",
            password="password123",
            role_fk=student_role,
            real_name="文档负责人",
            employee_id="DOC10001",
        )
        self.batch = ProjectBatch.objects.create(
            name="2026",
            year=2026,
            code="DOC2026",
            status=ProjectBatch.STATUS_ACTIVE,
            is_active=True,
            is_current=True,
        )

    def test_generate_project_doc_sanitizes_download_filename(self):
        project = Project.objects.create(
            project_no="DOC20260001",
            title="../unsafe:项目?.",
            leader=self.student,
            status=Project.ProjectStatus.IN_PROGRESS,
            year=2026,
            batch=self.batch,
        )

        _, filename = DocumentService.generate_project_doc(project.id)

        self.assertEqual(filename, "unsafe_项目__申报书.docx")

    def test_certificate_html_escapes_project_and_issuer_text(self):
        self.student.real_name = '<img src=x onerror="alert(1)">'
        self.student.save(update_fields=["real_name"])
        project = Project.objects.create(
            project_no='DOC"><script>alert(1)</script>',
            title='<script>alert("title")</script>',
            leader=self.student,
            status=Project.ProjectStatus.CLOSED,
            year=2026,
            batch=self.batch,
        )
        setting = CertificateSetting.objects.create(
            name="默认模板",
            school_name="测试学校",
            issuer_name='<script>alert("issuer")</script>',
            template_code="DEFAULT",
            is_active=True,
        )

        html = render_certificate_html(project, setting=setting)

        self.assertNotIn("<script>", html)
        self.assertNotIn("<img src=x", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertIn("&lt;img src=x", html)

    def test_establishment_notice_html_escapes_project_text(self):
        self.student.real_name = '<img src=x onerror="alert(1)">'
        self.student.save(update_fields=["real_name"])
        project = Project.objects.create(
            project_no='DOC"><script>alert(1)</script>',
            title='<script>alert("title")</script>',
            description="<b>description</b>",
            expected_results="<b>result</b>",
            leader=self.student,
            status=Project.ProjectStatus.IN_PROGRESS,
            year=2026,
            batch=self.batch,
        )

        html = ProjectAdminExportDocumentsMixin()._render_establishment_notice(project)

        self.assertNotIn("<script>", html)
        self.assertNotIn("<img src=x", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertIn("&lt;img src=x", html)
