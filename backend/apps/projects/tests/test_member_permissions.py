from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.crypto import get_random_string
from rest_framework.test import APIClient

from apps.dictionaries.models import DictionaryItem, DictionaryType
from apps.projects.models import Project, ProjectMember
from apps.system_settings.models import ProjectBatch
from apps.users.models import Role

User = get_user_model()


class ProjectMemberPermissionsTestCase(TestCase):
    def setUp(self):
        password = get_random_string(12)
        student_role = Role.objects.get(code="STUDENT")

        self.leader = User.objects.create_user(
            username="leader",
            password=password,
            role_fk=student_role,
            real_name="Leader",
            employee_id="S1001",
        )
        self.member = User.objects.create_user(
            username="member",
            password=password,
            role_fk=student_role,
            real_name="Member",
            employee_id="S1002",
        )

        self.batch = ProjectBatch.objects.create(
            name="2025",
            year=2025,
            code="B2025",
            status=ProjectBatch.STATUS_ACTIVE,
            is_active=True,
            is_current=True,
        )

        self.project = Project.objects.create(
            project_no="DC20250099",
            title="Perm Test Project",
            leader=self.leader,
            status=Project.ProjectStatus.IN_PROGRESS,
            year=2025,
            batch=self.batch,
        )
        ProjectMember.objects.create(
            project=self.project,
            user=self.member,
            role=ProjectMember.MemberRole.MEMBER,
        )

        dict_type = DictionaryType.objects.create(
            code="achievement_type",
            name="成果类型",
        )
        self.achievement_type = DictionaryItem.objects.create(
            dict_type=dict_type,
            value="PAPER",
            label="论文",
            sort_order=1,
        )

        self.member_client = APIClient()
        self.member_client.force_authenticate(user=self.member)

        self.leader_client = APIClient()
        self.leader_client.force_authenticate(user=self.leader)

    def test_member_cannot_update_project(self):
        resp = self.member_client.patch(
            f"/api/v1/projects/{self.project.id}/",
            {"title": "Hacked"},
            format="json",
        )
        self.assertEqual(resp.status_code, 403)

    def test_member_cannot_create_achievement(self):
        resp = self.member_client.post(
            "/api/v1/projects/achievements/",
            {
                "project": self.project.id,
                "achievement_type": self.achievement_type.id,
                "title": "A1",
                "description": "D1",
                "authors": "Someone",
                "journal": "Journal",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 403)

    def test_leader_can_create_achievement(self):
        resp = self.leader_client.post(
            "/api/v1/projects/achievements/",
            {
                "project": self.project.id,
                "achievement_type": self.achievement_type.id,
                "title": "A1",
                "description": "D1",
                "authors": "Someone",
                "journal": "Journal",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
