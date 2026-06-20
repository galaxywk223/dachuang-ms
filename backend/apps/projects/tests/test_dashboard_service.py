from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.crypto import get_random_string

from apps.projects.models import Project
from apps.projects.services.dashboard_service import DashboardService
from apps.reviews.models import Review
from apps.system_settings.models import ProjectBatch, WorkflowConfig, WorkflowNode
from apps.users.models import Role

User = get_user_model()


class DashboardServiceTestCase(TestCase):
    def setUp(self):
        password = get_random_string(12)
        teacher_role = Role.objects.get(code="TEACHER")
        student_role = Role.objects.get(code="STUDENT")

        self.expert = User.objects.create_user(
            username="expert-dashboard",
            password=password,
            role_fk=teacher_role,
            real_name="Expert Dashboard",
            employee_id="ED001",
            is_expert=True,
        )
        self.other_expert = User.objects.create_user(
            username="other-expert-dashboard",
            password=password,
            role_fk=teacher_role,
            real_name="Other Expert Dashboard",
            employee_id="ED002",
            is_expert=True,
        )
        self.student = User.objects.create_user(
            username="dashboard-student",
            password=password,
            role_fk=student_role,
            real_name="Dashboard Student",
            employee_id="DS001",
            college="计算机学院",
        )
        self.batch = ProjectBatch.objects.create(
            name="2026",
            year=2026,
            code="B2026",
            status=ProjectBatch.STATUS_ACTIVE,
            is_active=True,
            is_current=True,
        )
        self.project = Project.objects.create(
            project_no="DC20260001",
            title="Expert Dashboard Project",
            leader=self.student,
            status=Project.ProjectStatus.COLLEGE_AUDITING,
            year=2026,
            batch=self.batch,
        )

    def _role(self, code, name, scope_dimension=None):
        role, _ = Role.objects.get_or_create(
            code=code,
            defaults={"name": name, "scope_dimension": scope_dimension},
        )
        role.name = name
        role.scope_dimension = scope_dimension
        role.is_active = True
        role.save(update_fields=["name", "scope_dimension", "is_active"])
        return role

    def _workflow_node(self, role, code):
        workflow = WorkflowConfig.objects.create(
            name=f"Dashboard Workflow {code}",
            phase=WorkflowConfig.Phase.APPLICATION,
            batch=self.batch,
            version=100 + WorkflowConfig.objects.count(),
            is_active=True,
        )
        return WorkflowNode.objects.create(
            workflow=workflow,
            code=code,
            name=code,
            node_type=WorkflowNode.NodeType.REVIEW,
            role_fk=role,
            sort_order=1,
        )

    def test_expert_dashboard_uses_review_assignments(self):
        pending_review = Review.objects.create(
            project=self.project,
            reviewer=self.expert,
            review_type=Review.ReviewType.APPLICATION,
            status=Review.ReviewStatus.PENDING,
            is_expert_review=True,
        )
        Review.objects.create(
            project=self.project,
            reviewer=self.expert,
            review_type=Review.ReviewType.APPLICATION,
            status=Review.ReviewStatus.APPROVED,
            is_expert_review=True,
        )
        Review.objects.create(
            project=self.project,
            reviewer=self.other_expert,
            review_type=Review.ReviewType.APPLICATION,
            status=Review.ReviewStatus.PENDING,
            is_expert_review=True,
        )

        dashboard = DashboardService.get_expert_dashboard(self.expert)

        self.assertEqual(dashboard["pending_count"], 1)
        self.assertEqual(dashboard["completed_count"], 1)
        self.assertEqual(len(dashboard["pending_tasks"]), 1)
        self.assertEqual(dashboard["pending_tasks"][0]["task_id"], pending_review.id)
        self.assertEqual(
            dashboard["pending_tasks"][0]["project_name"],
            "Expert Dashboard Project",
        )
        self.assertEqual(dashboard["pending_tasks"][0]["group_name"], "")
        self.assertEqual(
            dashboard["pending_tasks"][0]["assigned_at"],
            pending_review.created_at,
        )

    def test_level2_dashboard_counts_custom_college_scope_review_nodes(self):
        college_role = self._role("COLLEGE_SECRETARY_DASHBOARD", "学院秘书", "COLLEGE")
        school_role = self._role("SCHOOL_SECRETARY_DASHBOARD", "学校秘书", "SCHOOL")
        college_admin = User.objects.create_user(
            username="college-dashboard-admin",
            password=get_random_string(12),
            role_fk=college_role,
            real_name="College Dashboard Admin",
            employee_id="CDA001",
            college="计算机学院",
        )
        Review.objects.create(
            project=self.project,
            workflow_node=self._workflow_node(college_role, "COLLEGE_SECRETARY_REVIEW"),
            review_type=Review.ReviewType.APPLICATION,
            status=Review.ReviewStatus.PENDING,
        )
        Review.objects.create(
            project=self.project,
            workflow_node=self._workflow_node(school_role, "SCHOOL_SECRETARY_REVIEW"),
            review_type=Review.ReviewType.APPLICATION,
            status=Review.ReviewStatus.PENDING,
        )

        dashboard = DashboardService.get_level2_admin_dashboard(college_admin)

        self.assertEqual(dashboard["review_stats"], {Review.ReviewType.APPLICATION: 1})

    def test_level1_dashboard_counts_custom_school_scope_review_nodes(self):
        college_role = self._role(
            "COLLEGE_SECRETARY_DASHBOARD_L1", "学院秘书", "COLLEGE"
        )
        school_role = self._role("SCHOOL_SECRETARY_DASHBOARD_L1", "学校秘书", "SCHOOL")
        school_admin = User.objects.create_user(
            username="school-dashboard-admin",
            password=get_random_string(12),
            role_fk=school_role,
            real_name="School Dashboard Admin",
            employee_id="SDA001",
        )
        Review.objects.create(
            project=self.project,
            workflow_node=self._workflow_node(school_role, "SCHOOL_DASH_REVIEW"),
            review_type=Review.ReviewType.MID_TERM,
            status=Review.ReviewStatus.PENDING,
        )
        Review.objects.create(
            project=self.project,
            workflow_node=self._workflow_node(college_role, "COLLEGE_DASH_REVIEW"),
            review_type=Review.ReviewType.MID_TERM,
            status=Review.ReviewStatus.PENDING,
        )

        dashboard = DashboardService.get_level1_admin_dashboard(school_admin)

        self.assertEqual(dashboard["review_stats"], {Review.ReviewType.MID_TERM: 1})

    def test_level1_dashboard_teacher_total_counts_custom_scoped_admins(self):
        teacher_role = Role.objects.get(code="TEACHER")
        college_role = self._role(
            "COLLEGE_DASHBOARD_TOTAL", "学院统计管理员", "COLLEGE"
        )
        school_role = self._role("SCHOOL_DASHBOARD_TOTAL", "学校统计管理员", "SCHOOL")
        school_admin = User.objects.create_user(
            username="school-dashboard-total-admin",
            password=get_random_string(12),
            role_fk=school_role,
            real_name="School Dashboard Total Admin",
            employee_id="SDT001",
        )
        User.objects.create_user(
            username="dashboard-total-teacher",
            password=get_random_string(12),
            role_fk=teacher_role,
            real_name="Dashboard Total Teacher",
            employee_id="DTT001",
        )
        User.objects.create_user(
            username="dashboard-total-college-admin",
            password=get_random_string(12),
            role_fk=college_role,
            real_name="Dashboard Total College Admin",
            employee_id="DTC001",
        )
        User.objects.create_user(
            username="dashboard-total-school-admin",
            password=get_random_string(12),
            role_fk=school_role,
            real_name="Dashboard Total School Admin",
            employee_id="DTS001",
        )

        dashboard = DashboardService.get_level1_admin_dashboard(school_admin)

        self.assertEqual(dashboard["overview"]["total_teachers"], 6)
