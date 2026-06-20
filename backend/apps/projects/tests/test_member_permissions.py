from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.crypto import get_random_string
from rest_framework.test import APIClient

from apps.dictionaries.models import DictionaryItem, DictionaryType
from apps.projects.models import (
    Project,
    ProjectAdvisor,
    ProjectAchievement,
    ProjectChangeRequest,
    ProjectExpenditure,
    ProjectMember,
)
from apps.system_settings.models import ProjectBatch
from apps.users.models import Role

User = get_user_model()


class ProjectMemberPermissionsTestCase(TestCase):
    def setUp(self):
        password = get_random_string(12)
        student_role = Role.objects.get(code="STUDENT")
        teacher_role = Role.objects.get(code="TEACHER")
        self.school_role, _ = Role.objects.get_or_create(
            code="SCHOOL_RESOURCE_VIEWER",
            defaults={"name": "校级资源查看员", "scope_dimension": "SCHOOL"},
        )
        self.school_role.scope_dimension = "SCHOOL"
        self.school_role.is_active = True
        self.school_role.save(update_fields=["scope_dimension", "is_active"])
        self.legacy_school_role, _ = Role.objects.get_or_create(
            code="LEVEL1_ADMIN",
            defaults={"name": "校级管理员"},
        )
        self.legacy_school_role.scope_dimension = None
        self.legacy_school_role.is_active = True
        self.legacy_school_role.save(update_fields=["scope_dimension", "is_active"])
        self.college_admin_role, _ = Role.objects.get_or_create(
            code="LEVEL2_ADMIN",
            defaults={"name": "学院管理员", "scope_dimension": "COLLEGE"},
        )
        self.college_admin_role.scope_dimension = "COLLEGE"
        self.college_admin_role.is_active = True
        self.college_admin_role.save(update_fields=["scope_dimension", "is_active"])

        self.leader = User.objects.create_user(
            username="leader",
            password=password,
            role_fk=student_role,
            real_name="Leader",
            employee_id="S1001",
            college="计算机学院",
        )
        self.member = User.objects.create_user(
            username="member",
            password=password,
            role_fk=student_role,
            real_name="Member",
            employee_id="S1002",
        )
        self.teacher = User.objects.create_user(
            username="teacher",
            password=password,
            role_fk=teacher_role,
            real_name="Teacher",
            employee_id="T1001",
        )
        self.school_admin = User.objects.create_user(
            username="school-resource-admin",
            password=password,
            role_fk=self.school_role,
            real_name="School Resource Admin",
            employee_id="A1001",
        )
        self.legacy_school_admin = User.objects.create_user(
            username="legacy-school-resource-admin",
            password=password,
            role_fk=self.legacy_school_role,
            real_name="Legacy School Resource Admin",
            employee_id="A1002",
        )
        self.college_admin = User.objects.create_user(
            username="college-resource-admin",
            password=password,
            role_fk=self.college_admin_role,
            real_name="College Resource Admin",
            employee_id="A2001",
            college="计算机学院",
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
        ProjectAdvisor.objects.create(project=self.project, user=self.teacher)

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

        self.teacher_client = APIClient()
        self.teacher_client.force_authenticate(user=self.teacher)

        self.school_admin_client = APIClient()
        self.school_admin_client.force_authenticate(user=self.school_admin)

        self.legacy_school_admin_client = APIClient()
        self.legacy_school_admin_client.force_authenticate(
            user=self.legacy_school_admin
        )

        self.college_admin_client = APIClient()
        self.college_admin_client.force_authenticate(user=self.college_admin)

    def test_member_cannot_update_project(self):
        resp = self.member_client.patch(
            f"/api/v1/projects/{self.project.id}/",
            {"title": "Hacked"},
            format="json",
        )
        self.assertEqual(resp.status_code, 403)

    def test_advisor_cannot_update_project_via_public_endpoint(self):
        resp = self.teacher_client.patch(
            f"/api/v1/projects/{self.project.id}/",
            {"title": "Teacher Edit"},
            format="json",
        )

        self.assertEqual(resp.status_code, 403)
        self.assertEqual(resp.data["message"], "只有项目负责人或管理员可以操作该项目")
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Perm Test Project")

    def test_advisor_cannot_delete_project_via_public_endpoint(self):
        resp = self.teacher_client.delete(f"/api/v1/projects/{self.project.id}/")

        self.assertEqual(resp.status_code, 403)
        self.assertEqual(resp.data["message"], "只有项目负责人或管理员可以操作该项目")
        self.assertTrue(Project.objects.filter(id=self.project.id).exists())

    def test_leader_cannot_direct_delete_non_draft_project(self):
        resp = self.leader_client.delete(f"/api/v1/projects/{self.project.id}/")

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.data["message"], "只有草稿项目可以直接删除")
        self.assertTrue(Project.objects.filter(id=self.project.id).exists())

    def test_leader_cannot_patch_server_owned_project_fields(self):
        other_batch = ProjectBatch.objects.create(
            name="2026 Other",
            year=2026,
            code="B2026-O",
            status=ProjectBatch.STATUS_ACTIVE,
            is_active=True,
            is_current=False,
        )

        resp = self.leader_client.patch(
            f"/api/v1/projects/{self.project.id}/",
            {
                "title": "Allowed Title",
                "status": Project.ProjectStatus.CLOSED,
                "leader": self.member.id,
                "batch": other_batch.id,
                "approved_budget": "9999.00",
                "is_deleted": True,
            },
            format="json",
        )

        self.assertEqual(resp.status_code, 200)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Allowed Title")
        self.assertEqual(self.project.status, Project.ProjectStatus.IN_PROGRESS)
        self.assertEqual(self.project.leader_id, self.leader.id)
        self.assertEqual(self.project.batch_id, self.batch.id)
        self.assertIsNone(self.project.approved_budget)
        self.assertFalse(self.project.is_deleted)

    def test_leader_cannot_update_archived_project_with_archive_filter(self):
        archived_batch = ProjectBatch.objects.create(
            name="2024",
            year=2024,
            code="B2024",
            status=ProjectBatch.STATUS_ARCHIVED,
            is_active=True,
            is_current=False,
        )
        archived_project = Project.objects.create(
            project_no="DC20240098",
            title="Archived Project",
            leader=self.leader,
            status=Project.ProjectStatus.CLOSED,
            year=2024,
            batch=archived_batch,
        )

        resp = self.leader_client.patch(
            f"/api/v1/projects/{archived_project.id}/?include_archived=true",
            {"title": "Changed Archived Project"},
            format="json",
        )

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.data["message"], "当前批次不允许操作该项目")
        archived_project.refresh_from_db()
        self.assertEqual(archived_project.title, "Archived Project")

    def test_leader_cannot_run_write_action_on_archived_project(self):
        archived_batch = ProjectBatch.objects.create(
            name="2024 Action",
            year=2024,
            code="B2024-A",
            status=ProjectBatch.STATUS_ARCHIVED,
            is_active=True,
            is_current=False,
        )
        archived_project = Project.objects.create(
            project_no="DC20240097",
            title="Archived Action Project",
            leader=self.leader,
            status=Project.ProjectStatus.IN_PROGRESS,
            year=2024,
            batch=archived_batch,
        )

        resp = self.leader_client.post(
            f"/api/v1/projects/{archived_project.id}/add_member/?include_archived=true",
            {"user_id": self.member.id},
            format="json",
        )

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.data["message"], "当前批次不允许操作该项目")
        self.assertFalse(
            ProjectMember.objects.filter(
                project=archived_project,
                user=self.member,
            ).exists()
        )

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

    def test_college_admin_cannot_create_achievement_for_other_college_project(self):
        other_leader = User.objects.create_user(
            username="other-achievement-leader",
            password=get_random_string(12),
            role_fk=Role.objects.get(code="STUDENT"),
            real_name="Other Achievement Leader",
            employee_id="S1006",
            college="数学学院",
        )
        other_project = Project.objects.create(
            project_no="DC20250106",
            title="Other College Achievement Target",
            leader=other_leader,
            status=Project.ProjectStatus.IN_PROGRESS,
            year=2025,
            batch=self.batch,
        )

        resp = self.college_admin_client.post(
            "/api/v1/projects/achievements/",
            {
                "project": other_project.id,
                "achievement_type": self.achievement_type.id,
                "title": "Cross College Achievement",
                "description": "D1",
                "authors": "Someone",
                "journal": "Journal",
            },
            format="json",
        )

        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.data["message"], "项目不存在")
        self.assertFalse(ProjectAchievement.objects.filter(project=other_project).exists())

    def test_leader_cannot_create_achievement_for_archived_batch_project(self):
        archived_batch = ProjectBatch.objects.create(
            name="2024",
            year=2024,
            code="B2024",
            status=ProjectBatch.STATUS_ARCHIVED,
            is_active=True,
            is_current=False,
        )
        archived_project = Project.objects.create(
            project_no="DC20240099",
            title="Archived Achievement Project",
            leader=self.leader,
            status=Project.ProjectStatus.CLOSED,
            year=2024,
            batch=archived_batch,
        )

        resp = self.leader_client.post(
            "/api/v1/projects/achievements/",
            {
                "project": archived_project.id,
                "achievement_type": self.achievement_type.id,
                "title": "A1",
                "description": "D1",
                "authors": "Someone",
                "journal": "Journal",
            },
            format="json",
        )

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.data["message"], "当前批次不允许操作该项目成果")
        self.assertEqual(ProjectAchievement.objects.filter(project=archived_project).count(), 0)

    def test_leader_cannot_move_achievement_to_another_leaders_project(self):
        other_project = Project.objects.create(
            project_no="DC20250100",
            title="Other Leader Project",
            leader=self.member,
            status=Project.ProjectStatus.IN_PROGRESS,
            year=2025,
            batch=self.batch,
        )
        achievement = ProjectAchievement.objects.create(
            project=self.project,
            achievement_type=self.achievement_type,
            title="Current Achievement",
            description="D1",
            authors="Someone",
            journal="Journal",
        )

        resp = self.leader_client.patch(
            f"/api/v1/projects/achievements/{achievement.id}/",
            {"project": other_project.id},
            format="json",
        )

        self.assertEqual(resp.status_code, 403)
        achievement.refresh_from_db()
        self.assertEqual(achievement.project_id, self.project.id)

    def test_leader_cannot_move_achievement_to_archived_project(self):
        archived_batch = ProjectBatch.objects.create(
            name="2024 Achievement Target",
            year=2024,
            code="B2024-AT",
            status=ProjectBatch.STATUS_ARCHIVED,
            is_active=True,
            is_current=False,
        )
        archived_project = Project.objects.create(
            project_no="DC20240100",
            title="Archived Target Project",
            leader=self.leader,
            status=Project.ProjectStatus.CLOSED,
            year=2024,
            batch=archived_batch,
        )
        achievement = ProjectAchievement.objects.create(
            project=self.project,
            achievement_type=self.achievement_type,
            title="Current Achievement",
            description="D1",
            authors="Someone",
            journal="Journal",
        )

        resp = self.leader_client.patch(
            f"/api/v1/projects/achievements/{achievement.id}/",
            {"project": archived_project.id},
            format="json",
        )

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.data["message"], "当前批次不允许操作该项目成果")
        achievement.refresh_from_db()
        self.assertEqual(achievement.project_id, self.project.id)

    def test_my_projects_tolerates_invalid_pagination(self):
        resp = self.leader_client.get(
            "/api/v1/projects/my-projects/",
            {"page": "invalid", "page_size": "1000"},
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["page"], 1)
        self.assertEqual(resp.data["page_size"], 100)
        self.assertEqual(resp.data["total"], 1)

    def test_add_member_rejects_invalid_user_id(self):
        resp = self.leader_client.post(
            f"/api/v1/projects/{self.project.id}/add_member/",
            {"user_id": "invalid"},
            format="json",
        )

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.data["message"], "用户ID不合法")

    def test_remove_achievement_rejects_invalid_id(self):
        resp = self.leader_client.delete(
            f"/api/v1/projects/{self.project.id}/remove-achievement/bad/"
        )

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.data["message"], "成果ID不合法")

    def test_project_list_tolerates_invalid_integer_filters(self):
        resp = self.leader_client.get(
            "/api/v1/projects/",
            {"leader": "invalid", "year": "bad", "level": "bad"},
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["data"]["count"], 0)

    def test_custom_school_admin_lists_public_resources_across_colleges(self):
        other_leader = User.objects.create_user(
            username="other-resource-leader",
            password=get_random_string(12),
            role_fk=Role.objects.get(code="STUDENT"),
            real_name="Other Resource Leader",
            employee_id="S1003",
            college="数学学院",
        )
        other_project = Project.objects.create(
            project_no="DC20250102",
            title="Other Resource Project",
            leader=other_leader,
            status=Project.ProjectStatus.IN_PROGRESS,
            year=2025,
            batch=self.batch,
        )
        ProjectAchievement.objects.create(
            project=self.project,
            achievement_type=self.achievement_type,
            title="Current College Achievement",
            description="D1",
            authors="Someone",
            journal="Journal",
        )
        ProjectAchievement.objects.create(
            project=other_project,
            achievement_type=self.achievement_type,
            title="Other College Achievement",
            description="D2",
            authors="Someone",
            journal="Journal",
        )
        ProjectExpenditure.objects.create(
            project=self.project,
            title="Current College Expense",
            amount="100.00",
            expenditure_date="2026-01-01",
            created_by=self.leader,
        )
        ProjectExpenditure.objects.create(
            project=other_project,
            title="Other College Expense",
            amount="200.00",
            expenditure_date="2026-01-02",
            created_by=other_leader,
        )
        ProjectChangeRequest.objects.create(
            project=self.project,
            request_type=ProjectChangeRequest.ChangeType.CHANGE,
            reason="current college change",
            created_by=self.leader,
        )
        ProjectChangeRequest.objects.create(
            project=other_project,
            request_type=ProjectChangeRequest.ChangeType.CHANGE,
            reason="other college change",
            created_by=other_leader,
        )

        project_resp = self.school_admin_client.get("/api/v1/projects/")
        achievement_resp = self.school_admin_client.get("/api/v1/projects/achievements/")
        expenditure_resp = self.school_admin_client.get("/api/v1/projects/expenditures/")
        change_resp = self.school_admin_client.get("/api/v1/projects/change-requests/")

        self.assertEqual(project_resp.status_code, 200)
        self.assertEqual(project_resp.data["data"]["count"], 2)
        self.assertEqual(achievement_resp.status_code, 200)
        self.assertEqual(achievement_resp.data["data"]["count"], 2)
        self.assertEqual(expenditure_resp.status_code, 200)
        self.assertEqual(expenditure_resp.data["data"]["count"], 2)
        self.assertEqual(change_resp.status_code, 200)
        self.assertEqual(change_resp.data["count"], 2)

    def test_legacy_level1_admin_lists_public_resources_across_colleges(self):
        other_leader = User.objects.create_user(
            username="legacy-resource-leader",
            password=get_random_string(12),
            role_fk=Role.objects.get(code="STUDENT"),
            real_name="Legacy Resource Leader",
            employee_id="S1005",
            college="数学学院",
        )
        other_project = Project.objects.create(
            project_no="DC20250104",
            title="Legacy Resource Project",
            leader=other_leader,
            status=Project.ProjectStatus.IN_PROGRESS,
            year=2025,
            batch=self.batch,
        )
        ProjectAchievement.objects.create(
            project=self.project,
            achievement_type=self.achievement_type,
            title="Legacy Current College Achievement",
            description="D1",
            authors="Someone",
            journal="Journal",
        )
        ProjectAchievement.objects.create(
            project=other_project,
            achievement_type=self.achievement_type,
            title="Legacy Other College Achievement",
            description="D2",
            authors="Someone",
            journal="Journal",
        )
        ProjectExpenditure.objects.create(
            project=self.project,
            title="Legacy Current College Expense",
            amount="100.00",
            expenditure_date="2026-01-01",
            created_by=self.leader,
        )
        ProjectExpenditure.objects.create(
            project=other_project,
            title="Legacy Other College Expense",
            amount="200.00",
            expenditure_date="2026-01-02",
            created_by=other_leader,
        )
        ProjectChangeRequest.objects.create(
            project=self.project,
            request_type=ProjectChangeRequest.ChangeType.CHANGE,
            reason="legacy current college change",
            created_by=self.leader,
        )
        ProjectChangeRequest.objects.create(
            project=other_project,
            request_type=ProjectChangeRequest.ChangeType.CHANGE,
            reason="legacy other college change",
            created_by=other_leader,
        )

        project_resp = self.legacy_school_admin_client.get("/api/v1/projects/")
        achievement_resp = self.legacy_school_admin_client.get(
            "/api/v1/projects/achievements/"
        )
        expenditure_resp = self.legacy_school_admin_client.get(
            "/api/v1/projects/expenditures/"
        )
        change_resp = self.legacy_school_admin_client.get(
            "/api/v1/projects/change-requests/"
        )

        self.assertEqual(project_resp.status_code, 200)
        self.assertEqual(project_resp.data["data"]["count"], 2)
        self.assertEqual(achievement_resp.status_code, 200)
        self.assertEqual(achievement_resp.data["data"]["count"], 2)
        self.assertEqual(expenditure_resp.status_code, 200)
        self.assertEqual(expenditure_resp.data["data"]["count"], 2)
        self.assertEqual(change_resp.status_code, 200)
        self.assertEqual(change_resp.data["count"], 2)

    def test_custom_school_admin_lists_closure_applications_across_colleges(self):
        self.project.status = Project.ProjectStatus.CLOSURE_SUBMITTED
        self.project.save(update_fields=["status", "updated_at"])
        other_leader = User.objects.create_user(
            username="other-closure-leader",
            password=get_random_string(12),
            role_fk=Role.objects.get(code="STUDENT"),
            real_name="Other Closure Leader",
            employee_id="S1004",
            college="数学学院",
        )
        Project.objects.create(
            project_no="DC20250103",
            title="Other Closure Project",
            leader=other_leader,
            status=Project.ProjectStatus.CLOSURE_LEVEL1_REVIEWING,
            year=2025,
            batch=self.batch,
        )

        response = self.school_admin_client.get("/api/v1/projects/closure/applied/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["total"], 2)

    def test_legacy_level1_admin_lists_closure_applications_across_colleges(self):
        self.project.status = Project.ProjectStatus.CLOSURE_SUBMITTED
        self.project.save(update_fields=["status", "updated_at"])
        other_leader = User.objects.create_user(
            username="legacy-closure-leader",
            password=get_random_string(12),
            role_fk=Role.objects.get(code="STUDENT"),
            real_name="Legacy Closure Leader",
            employee_id="S1006",
            college="数学学院",
        )
        Project.objects.create(
            project_no="DC20250105",
            title="Legacy Closure Project",
            leader=other_leader,
            status=Project.ProjectStatus.CLOSURE_LEVEL1_REVIEWING,
            year=2025,
            batch=self.batch,
        )

        response = self.legacy_school_admin_client.get(
            "/api/v1/projects/closure/applied/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["total"], 2)

    def test_custom_school_admin_cannot_use_college_export_actions(self):
        excel_response = self.school_admin_client.get("/api/v1/projects/export-excel/")
        attachment_response = self.school_admin_client.get(
            "/api/v1/projects/export-attachments/"
        )

        self.assertEqual(excel_response.status_code, 403)
        self.assertEqual(excel_response.data["message"], "无权限导出数据")
        self.assertEqual(attachment_response.status_code, 403)
        self.assertEqual(attachment_response.data["message"], "无权限下载附件")

    def test_legacy_level1_admin_cannot_use_college_export_actions(self):
        excel_response = self.legacy_school_admin_client.get(
            "/api/v1/projects/export-excel/"
        )
        attachment_response = self.legacy_school_admin_client.get(
            "/api/v1/projects/export-attachments/"
        )

        self.assertEqual(excel_response.status_code, 403)
        self.assertEqual(excel_response.data["message"], "无权限导出数据")
        self.assertEqual(attachment_response.status_code, 403)
        self.assertEqual(attachment_response.data["message"], "无权限下载附件")

    def test_my_projects_tolerates_invalid_dictionary_filters(self):
        resp = self.leader_client.get(
            "/api/v1/projects/my-projects/",
            {"level": "invalid", "category": "bad"},
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["total"], 0)

    def test_achievement_list_tolerates_invalid_integer_filters(self):
        ProjectAchievement.objects.create(
            project=self.project,
            achievement_type=self.achievement_type,
            title="A1",
            description="D1",
            authors="Someone",
            journal="Journal",
        )

        resp = self.leader_client.get(
            "/api/v1/projects/achievements/",
            {"project": "invalid", "achievement_type": "bad"},
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["data"]["count"], 0)

    def test_achievement_list_is_limited_to_current_batch(self):
        archived_batch = ProjectBatch.objects.create(
            name="2024",
            year=2024,
            code="B2024",
            status=ProjectBatch.STATUS_ARCHIVED,
            is_active=True,
            is_current=False,
        )
        archived_project = Project.objects.create(
            project_no="DC20240099",
            title="Archived Achievement Project",
            leader=self.leader,
            status=Project.ProjectStatus.CLOSED,
            year=2024,
            batch=archived_batch,
        )
        ProjectAchievement.objects.create(
            project=self.project,
            achievement_type=self.achievement_type,
            title="Current Achievement",
            description="D1",
            authors="Someone",
            journal="Journal",
        )
        ProjectAchievement.objects.create(
            project=archived_project,
            achievement_type=self.achievement_type,
            title="Archived Achievement",
            description="D2",
            authors="Someone",
            journal="Journal",
        )

        resp = self.leader_client.get("/api/v1/projects/achievements/")

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["data"]["count"], 1)
        self.assertEqual(resp.data["data"]["results"][0]["title"], "Current Achievement")

    def test_expenditure_list_tolerates_invalid_project_filter(self):
        ProjectExpenditure.objects.create(
            project=self.project,
            title="E1",
            amount="100.00",
            expenditure_date="2026-01-01",
            created_by=self.leader,
        )

        resp = self.leader_client.get(
            "/api/v1/projects/expenditures/",
            {"project": "invalid"},
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["data"]["count"], 0)

    def test_change_request_list_tolerates_invalid_project_filter(self):
        ProjectChangeRequest.objects.create(
            project=self.project,
            request_type=ProjectChangeRequest.ChangeType.CHANGE,
            reason="change",
            created_by=self.leader,
        )

        resp = self.leader_client.get(
            "/api/v1/projects/change-requests/",
            {"project": "invalid"},
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 0)

    def test_change_request_rejects_non_object_change_data(self):
        resp = self.leader_client.post(
            "/api/v1/projects/change-requests/",
            {
                "project": self.project.id,
                "request_type": ProjectChangeRequest.ChangeType.CHANGE,
                "reason": "change",
                "change_data": '["bad"]',
            },
            format="json",
        )

        self.assertEqual(resp.status_code, 400)
        self.assertIn("变更内容必须为JSON对象", str(resp.data))

    def test_leader_cannot_move_change_request_to_another_leaders_project(self):
        other_project = Project.objects.create(
            project_no="DC20250101",
            title="Other Change Target",
            leader=self.member,
            status=Project.ProjectStatus.IN_PROGRESS,
            year=2025,
            batch=self.batch,
        )
        change_request = ProjectChangeRequest.objects.create(
            project=self.project,
            request_type=ProjectChangeRequest.ChangeType.CHANGE,
            reason="change",
            created_by=self.leader,
        )

        resp = self.leader_client.patch(
            f"/api/v1/projects/change-requests/{change_request.id}/",
            {"project": other_project.id},
            format="json",
        )

        self.assertEqual(resp.status_code, 403)
        self.assertEqual(resp.data["message"], "只有项目负责人可以提交异动申请")
        change_request.refresh_from_db()
        self.assertEqual(change_request.project_id, self.project.id)

    def test_leader_cannot_submit_stale_closed_project_change_request(self):
        change_request = ProjectChangeRequest.objects.create(
            project=self.project,
            request_type=ProjectChangeRequest.ChangeType.CHANGE,
            reason="stale closed project change",
            change_data={},
            created_by=self.leader,
        )
        self.project.status = Project.ProjectStatus.CLOSED
        self.project.save(update_fields=["status", "updated_at"])

        resp = self.leader_client.post(
            f"/api/v1/projects/change-requests/{change_request.id}/submit/",
            format="json",
        )

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.data["message"], "项目已结题或终止，无法申请异动")
        change_request.refresh_from_db()
        self.assertEqual(change_request.status, ProjectChangeRequest.ChangeStatus.DRAFT)
