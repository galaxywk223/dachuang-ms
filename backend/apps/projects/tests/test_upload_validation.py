from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import SimpleTestCase
from django.test import TestCase

from apps.projects.models import Project
from apps.projects.serializers.closure import ProjectClosureSerializer
from apps.projects.serializers.midterm import ProjectMidTermSerializer
from apps.projects.serializers.project import ProjectSerializer
from apps.projects.services import ProjectService
from apps.projects.upload_validation import validate_project_support_file
from apps.users.models import Role


User = get_user_model()


class ProjectUploadValidationTestCase(SimpleTestCase):
    def test_project_serializer_sanitizes_path_like_upload_name(self):
        upload = SimpleUploadedFile(
            "../proposal.pdf",
            b"%PDF-1.4\ncontent",
            content_type="application/pdf",
        )
        serializer = ProjectSerializer()

        validated = serializer.validate_proposal_file(upload)

        self.assertEqual(validated.name, "proposal.pdf")

    def test_project_serializer_rejects_unsupported_application_extension(self):
        upload = SimpleUploadedFile(
            "proposal.exe",
            b"not a document",
            content_type="application/octet-stream",
        )
        serializer = ProjectSerializer()

        with self.assertRaisesMessage(Exception, "申报书仅支持"):
            serializer.validate_proposal_file(upload)

    def test_midterm_serializer_rejects_empty_report(self):
        upload = SimpleUploadedFile(
            "midterm.pdf",
            b"",
            content_type="application/pdf",
        )
        serializer = ProjectMidTermSerializer()

        with self.assertRaisesMessage(Exception, "中期报告不能为空"):
            serializer.validate_mid_term_report(upload)

    def test_closure_serializer_rejects_large_report(self):
        upload = SimpleUploadedFile(
            "closure.pdf",
            b"0" * (2 * 1024 * 1024 + 1),
            content_type="application/pdf",
        )
        serializer = ProjectClosureSerializer()

        with self.assertRaisesMessage(Exception, "结题报告文件大小不能超过2MB"):
            serializer.validate_final_report(upload)

    def test_support_upload_rejects_script_extension(self):
        upload = SimpleUploadedFile(
            "proof.js",
            b"alert(1)",
            content_type="application/javascript",
        )

        with self.assertRaisesMessage(Exception, "经费凭证仅支持"):
            validate_project_support_file(
                upload,
                label="经费凭证",
                max_size_mb=10,
                empty_as_none=True,
            )


class ProjectUploadServiceValidationTestCase(TestCase):
    def setUp(self):
        role = Role.objects.get(code="STUDENT")
        self.student = User.objects.create_user(
            username="upload_service_student",
            password="upload-password",
            role_fk=role,
            real_name="Upload Service Student",
            employee_id="UPS1001",
        )

    def test_apply_mid_term_requires_report_for_submit(self):
        project = Project.objects.create(
            project_no="UPS-MID-001",
            title="Midterm Upload Policy",
            leader=self.student,
            status=Project.ProjectStatus.IN_PROGRESS,
            year=2026,
        )

        with self.assertRaisesMessage(ValueError, "请先上传中期检查报告书"):
            ProjectService.apply_mid_term(project, None, is_draft=False)

    def test_apply_closure_requires_report_for_submit(self):
        project = Project.objects.create(
            project_no="UPS-CLO-001",
            title="Closure Upload Policy",
            leader=self.student,
            status=Project.ProjectStatus.READY_FOR_CLOSURE,
            year=2026,
        )

        with self.assertRaisesMessage(ValueError, "请先上传结题报告书"):
            ProjectService.apply_closure(project, None, is_draft=False)
