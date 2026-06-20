from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.projects.models import Project, ProjectAdvisor, ProjectMember
from apps.projects.services.application_service import _normalize_list, _validate_limits
from apps.projects.services.validation_service import ProjectValidationService
from apps.system_settings.models import ProjectBatch, SystemSetting
from apps.users.models import Role


User = get_user_model()


class ProjectApplicationApiValidationTestCase(TestCase):
    def setUp(self):
        student_role, _ = Role.objects.get_or_create(
            code="STUDENT",
            defaults={"name": "学生"},
        )
        self.student = User.objects.create_user(
            username="application_student",
            password="password123",
            role_fk=student_role,
            real_name="申报学生",
            employee_id="APP1001",
            college="计算机学院",
        )
        self.teacher_role, _ = Role.objects.get_or_create(
            code="TEACHER",
            defaults={"name": "指导教师"},
        )
        self.batch = ProjectBatch.objects.create(
            name="2026",
            year=2026,
            code="APP2026",
            status=ProjectBatch.STATUS_ACTIVE,
            is_active=True,
            is_current=True,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.student)

    def test_create_application_reports_workflow_configuration_error(self):
        response = self.client.post(
            "/api/v1/projects/application/create/",
            {
                "title": "缺少流程配置的申报",
                "description": "提交时应返回配置错误",
                "is_draft": False,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["message"], "流程未落库，请先配置并启用工作流")

    def test_update_application_reports_workflow_configuration_error(self):
        project = Project.objects.create(
            project_no="APP20260001",
            title="待提交草稿",
            leader=self.student,
            status=Project.ProjectStatus.DRAFT,
            year=2026,
            batch=self.batch,
        )

        response = self.client.put(
            f"/api/v1/projects/application/{project.id}/update/",
            {
                "title": "待提交草稿",
                "description": "提交时应返回配置错误",
                "is_draft": False,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["message"], "流程未落库，请先配置并启用工作流")

    def test_saved_project_does_not_duplicate_its_own_title(self):
        project = Project.objects.create(
            project_no="APP20260002",
            title="自查重项目",
            leader=self.student,
            status=Project.ProjectStatus.SUBMITTED,
            year=2026,
            batch=self.batch,
        )

        result = ProjectValidationService.validate_project_application(
            project,
            self.student,
            is_update=False,
        )

        self.assertTrue(result["is_valid"])

    def test_smart_validation_reads_batch_settings(self):
        SystemSetting.objects.create(
            code="LIMIT_RULES",
            name="限制规则",
            batch=self.batch,
            data={"dedupe_title": False},
        )
        Project.objects.create(
            project_no="APP20260010",
            title="批次配置项目",
            leader=self.student,
            status=Project.ProjectStatus.SUBMITTED,
            year=2026,
            batch=self.batch,
        )
        duplicate = Project.objects.create(
            project_no="APP20260011",
            title="批次配置项目",
            leader=self.student,
            status=Project.ProjectStatus.SUBMITTED,
            year=2026,
            batch=self.batch,
        )

        result = ProjectValidationService.validate_project_application(
            duplicate,
            self.student,
            is_update=False,
        )

        self.assertTrue(result["is_valid"])

    def test_create_limits_validate_teacher_active_projects(self):
        teacher = User.objects.create_user(
            username="application_teacher",
            password="password123",
            role_fk=self.teacher_role,
            real_name="指导教师",
            employee_id="APP2001",
        )
        active_project = Project.objects.create(
            project_no="APP20260006",
            title="教师在研项目",
            leader=self.student,
            status=Project.ProjectStatus.IN_PROGRESS,
            year=2026,
            batch=self.batch,
        )
        ProjectAdvisor.objects.create(project=active_project, user=teacher)
        SystemSetting.objects.create(
            code="LIMIT_RULES",
            name="限制规则",
            batch=self.batch,
            data={"max_teacher_active": 1},
        )

        ok, message = _validate_limits(
            self.student,
            advisors_data=[{"user_id": teacher.id}],
            members_data=[],
            project=None,
            batch=self.batch,
        )

        self.assertFalse(ok)
        self.assertEqual(message, "指导教师存在未结题项目，无法继续指导新项目")

    def test_zero_teacher_active_limit_is_disabled(self):
        teacher = User.objects.create_user(
            username="application_teacher_unlimited",
            password="password123",
            role_fk=self.teacher_role,
            real_name="不限项教师",
            employee_id="APP2002",
        )
        SystemSetting.objects.create(
            code="LIMIT_RULES",
            name="限制规则",
            batch=self.batch,
            data={"max_teacher_active": 0},
        )

        ok, message = _validate_limits(
            self.student,
            advisors_data=[{"user_id": teacher.id}],
            members_data=[],
            project=None,
            batch=self.batch,
        )

        self.assertTrue(ok)
        self.assertEqual(message, "")

    def test_limit_validation_tolerates_invalid_numeric_settings(self):
        SystemSetting.objects.create(
            code="LIMIT_RULES",
            name="限制规则",
            batch=self.batch,
            data={
                "max_advisors": "invalid",
                "max_members": "bad",
                "max_teacher_active": "wrong",
                "max_student_member": "bad",
            },
        )

        ok, message = _validate_limits(
            self.student,
            advisors_data=[],
            members_data=[],
            project=None,
            batch=self.batch,
        )

        self.assertTrue(ok)
        self.assertEqual(message, "")

    def test_smart_validation_tolerates_invalid_numeric_settings(self):
        project = Project.objects.create(
            project_no="APP20260007",
            title="配置容错项目",
            leader=self.student,
            status=Project.ProjectStatus.SUBMITTED,
            year=2026,
            batch=self.batch,
        )
        project._advisors_list = []
        project._members_list = []

        result = ProjectValidationService.validate_project_application(
            project,
            self.student,
            is_update=False,
        )

        self.assertTrue(result["is_valid"])

        SystemSetting.objects.create(
            code="VALIDATION_RULES",
            name="校验规则",
            batch=self.batch,
            data={"title_min_length": "bad", "title_max_length": "invalid"},
        )

        result = ProjectValidationService.validate_project_application(
            project,
            self.student,
            is_update=False,
        )

        self.assertTrue(result["is_valid"])

    def test_zero_member_active_limit_is_disabled_in_smart_validation(self):
        SystemSetting.objects.create(
            code="LIMIT_RULES",
            name="限制规则",
            batch=self.batch,
            data={"max_student_member": 0},
        )
        existing = Project.objects.create(
            project_no="APP20260008",
            title="既有参与项目",
            leader=self.student,
            status=Project.ProjectStatus.IN_PROGRESS,
            year=2026,
            batch=self.batch,
        )
        ProjectMember.objects.create(
            project=existing,
            user=self.student,
            role=ProjectMember.MemberRole.LEADER,
        )
        project = Project.objects.create(
            project_no="APP20260009",
            title="不限成员项目",
            leader=self.student,
            status=Project.ProjectStatus.SUBMITTED,
            year=2026,
            batch=self.batch,
        )
        project._members_list = []

        result = ProjectValidationService.validate_project_application(
            project,
            self.student,
            is_update=False,
        )

        self.assertTrue(result["is_valid"])

    def test_duplicate_project_title_still_rejected(self):
        Project.objects.create(
            project_no="APP20260003",
            title="重复项目",
            leader=self.student,
            status=Project.ProjectStatus.SUBMITTED,
            year=2026,
            batch=self.batch,
        )
        duplicate = Project.objects.create(
            project_no="APP20260004",
            title="重复项目",
            leader=self.student,
            status=Project.ProjectStatus.SUBMITTED,
            year=2026,
            batch=self.batch,
        )

        result = ProjectValidationService.validate_project_application(
            duplicate,
            self.student,
            is_update=False,
        )

        self.assertFalse(result["is_valid"])
        self.assertIn("项目标题与已有项目重复", result["errors"][0])

    def test_member_limit_validation_uses_current_member_schema(self):
        project = Project.objects.create(
            project_no="APP20260005",
            title="成员限项项目",
            leader=self.student,
            status=Project.ProjectStatus.SUBMITTED,
            year=2026,
            batch=self.batch,
        )

        result = ProjectValidationService.validate_project_application(
            project,
            self.student,
            is_update=False,
        )

        self.assertTrue(result["is_valid"])

    def test_normalize_list_accepts_json_list(self):
        result = _normalize_list('[{"user_id": 1}]')

        self.assertEqual(result, [{"user_id": 1}])

    def test_normalize_list_accepts_blank_as_empty(self):
        self.assertEqual(_normalize_list(""), [])

    def test_normalize_list_rejects_invalid_json(self):
        with self.assertRaisesMessage(ValueError, "列表数据格式错误"):
            _normalize_list("[invalid")

    def test_normalize_list_rejects_non_object_items(self):
        with self.assertRaisesMessage(ValueError, "列表数据格式错误"):
            _normalize_list('["bad"]')
