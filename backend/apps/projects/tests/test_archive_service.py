from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.projects.models import Project, ProjectMember
from apps.projects.services.archive_service import ArchiveService
from apps.system_settings.models import ProjectBatch
from apps.users.models import Role


User = get_user_model()


class ArchiveServiceTestCase(TestCase):
    def setUp(self):
        student_role, _ = Role.objects.get_or_create(
            code="STUDENT",
            defaults={"name": "学生"},
        )
        self.leader = User.objects.create_user(
            username="archive_leader",
            password="password123",
            role_fk=student_role,
            real_name="归档负责人",
            employee_id="ARC1001",
        )
        self.member = User.objects.create_user(
            username="archive_member",
            password="password123",
            role_fk=student_role,
            real_name="归档成员",
            employee_id="ARC1002",
        )
        self.batch = ProjectBatch.objects.create(
            name="2026",
            year=2026,
            code="ARC2026",
            status=ProjectBatch.STATUS_ACTIVE,
            is_active=True,
            is_current=True,
        )

    def test_archive_metadata_uses_current_project_fields(self):
        project = Project.objects.create(
            project_no="ARC20260001",
            title="归档项目",
            leader=self.leader,
            status=Project.ProjectStatus.CLOSED,
            year=2026,
            batch=self.batch,
            budget=Decimal("1200.00"),
        )
        ProjectMember.objects.create(
            project=project,
            user=self.member,
            role=ProjectMember.MemberRole.MEMBER,
        )

        archive = ArchiveService.archive_project(project)

        self.assertEqual(archive.metadata["total_budget"], "1200.00")
        self.assertEqual(archive.metadata["team_size"], 2)

    def test_ensure_project_archive_writes_metadata(self):
        project = Project.objects.create(
            project_no="ARC20260002",
            title="批量归档项目",
            leader=self.leader,
            status=Project.ProjectStatus.CLOSED,
            year=2026,
            batch=self.batch,
            budget=Decimal("800.00"),
        )
        ProjectMember.objects.create(
            project=project,
            user=self.member,
            role=ProjectMember.MemberRole.MEMBER,
        )

        archive = ArchiveService.ensure_project_archive(project)

        self.assertIsNotNone(archive)
        self.assertEqual(archive.metadata["project_status"], Project.ProjectStatus.CLOSED)
        self.assertEqual(archive.metadata["total_budget"], "800.00")
        self.assertEqual(archive.metadata["team_size"], 2)
