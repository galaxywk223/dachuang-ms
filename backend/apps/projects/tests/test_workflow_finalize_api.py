from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from apps.projects.models import Project, ProjectPhaseInstance
from apps.reviews.models import Review
from apps.system_settings.models import ProjectBatch, WorkflowConfig, WorkflowNode
from apps.users.models import Role


User = get_user_model()


class ProjectWorkflowFinalizeApiTestCase(TestCase):
    def setUp(self):
        self.admin_role = self._role("LEVEL1_ADMIN", "校级管理员", "SCHOOL")
        self.student_role = self._role("STUDENT", "学生")
        self.teacher_role = self._role("TEACHER", "导师")
        self.admin = User.objects.create_user(
            username="finalize_admin",
            password="password123",
            role_fk=self.admin_role,
            real_name="终审管理员",
            employee_id="FA10001",
        )
        self.student = User.objects.create_user(
            username="finalize_student",
            password="password123",
            role_fk=self.student_role,
            real_name="项目负责人",
            employee_id="FS10001",
            college="计算机学院",
        )
        self.batch = ProjectBatch.objects.create(
            name="2026",
            year=2026,
            code="FZ2026",
            status=ProjectBatch.STATUS_ACTIVE,
            is_active=True,
            is_current=True,
        )
        self.project = Project.objects.create(
            project_no="FZ20260001",
            title="Finalize Project",
            leader=self.student,
            status=Project.ProjectStatus.MID_TERM_REVIEWING,
            year=2026,
            batch=self.batch,
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

    def _make_admin_review(self, phase, review_type):
        workflow = WorkflowConfig.objects.create(
            name=f"{phase} Workflow",
            phase=phase,
            batch=self.batch,
            version=1,
            is_active=True,
        )
        node = WorkflowNode.objects.create(
            workflow=workflow,
            code=f"{phase}_FINAL",
            name="终审",
            node_type=WorkflowNode.NodeType.REVIEW,
            role_fk=self.admin_role,
            sort_order=1,
        )
        phase_instance = ProjectPhaseInstance.objects.create(
            project=self.project,
            phase=phase,
            attempt_no=1,
            step=node.code,
            current_node_id=node.id,
            state=ProjectPhaseInstance.State.IN_PROGRESS,
        )
        return Review.objects.create(
            project=self.project,
            phase_instance=phase_instance,
            workflow_node=node,
            review_type=review_type,
            status=Review.ReviewStatus.PENDING,
        )

    def _make_closure_review_chain(self):
        workflow = WorkflowConfig.objects.create(
            name="Closure Return Workflow",
            phase=ProjectPhaseInstance.Phase.CLOSURE,
            batch=self.batch,
            version=2,
            is_active=True,
        )
        submit_node = WorkflowNode.objects.create(
            workflow=workflow,
            code="CLOSURE_SUBMIT",
            name="学生提交结题",
            node_type=WorkflowNode.NodeType.SUBMIT,
            role_fk=self.student_role,
            sort_order=1,
        )
        teacher_node = WorkflowNode.objects.create(
            workflow=workflow,
            code="CLOSURE_TEACHER",
            name="导师审核",
            node_type=WorkflowNode.NodeType.REVIEW,
            role_fk=self.teacher_role,
            sort_order=2,
            allowed_reject_to=submit_node.id,
        )
        college_node = WorkflowNode.objects.create(
            workflow=workflow,
            code="CLOSURE_COLLEGE",
            name="学院审核",
            node_type=WorkflowNode.NodeType.APPROVAL,
            role_fk=self._role("LEVEL2_ADMIN", "学院管理员", "COLLEGE"),
            sort_order=3,
            allowed_reject_to=teacher_node.id,
        )
        school_node = WorkflowNode.objects.create(
            workflow=workflow,
            code="CLOSURE_SCHOOL",
            name="学校审核",
            node_type=WorkflowNode.NodeType.APPROVAL,
            role_fk=self.admin_role,
            sort_order=4,
            allowed_reject_to=college_node.id,
        )
        forward_node = WorkflowNode.objects.create(
            workflow=workflow,
            code="CLOSURE_FORWARD",
            name="后置节点",
            node_type=WorkflowNode.NodeType.APPROVAL,
            role_fk=self.admin_role,
            sort_order=5,
            allowed_reject_to=school_node.id,
        )
        self.project.status = Project.ProjectStatus.CLOSURE_LEVEL1_REVIEWING
        self.project.save(update_fields=["status", "updated_at"])
        phase_instance = ProjectPhaseInstance.objects.create(
            project=self.project,
            phase=ProjectPhaseInstance.Phase.CLOSURE,
            attempt_no=1,
            step=school_node.code,
            current_node_id=school_node.id,
            state=ProjectPhaseInstance.State.IN_PROGRESS,
        )
        review = Review.objects.create(
            project=self.project,
            phase_instance=phase_instance,
            workflow_node=school_node,
            review_type=Review.ReviewType.CLOSURE,
            status=Review.ReviewStatus.PENDING,
        )
        return review, teacher_node, forward_node

    def test_finalize_midterm_rejects_invalid_target_node_id(self):
        self._make_admin_review(
            ProjectPhaseInstance.Phase.MID_TERM,
            Review.ReviewType.MID_TERM,
        )

        response = self.client.post(
            f"/api/v1/projects/{self.project.id}/workflow/finalize-midterm/",
            {"action": "return", "target_node_id": "bad"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["message"], "target_node_id格式错误")

    def test_finalize_closure_rejects_invalid_target_node_id(self):
        self.project.status = Project.ProjectStatus.CLOSURE_LEVEL1_REVIEWING
        self.project.save(update_fields=["status", "updated_at"])
        self._make_admin_review(
            ProjectPhaseInstance.Phase.CLOSURE,
            Review.ReviewType.CLOSURE,
        )

        response = self.client.post(
            f"/api/v1/projects/{self.project.id}/workflow/finalize-closure/",
            {"action": "return", "target_node_id": "bad"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["message"], "target_node_id格式错误")

    def test_finalize_closure_can_return_to_teacher_node(self):
        review, teacher_node, _forward_node = self._make_closure_review_chain()

        response = self.client.post(
            f"/api/v1/projects/{self.project.id}/workflow/finalize-closure/",
            {"action": "return", "reason": "需导师复核", "return_to": "teacher"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        review.refresh_from_db()
        self.assertEqual(review.status, Review.ReviewStatus.REJECTED)
        new_phase = ProjectPhaseInstance.objects.filter(
            project=self.project,
            phase=ProjectPhaseInstance.Phase.CLOSURE,
            state=ProjectPhaseInstance.State.IN_PROGRESS,
        ).latest("attempt_no")
        self.assertEqual(new_phase.current_node_id, teacher_node.id)

    def test_finalize_closure_rejects_forward_target_node(self):
        review, _teacher_node, forward_node = self._make_closure_review_chain()

        response = self.client.post(
            f"/api/v1/projects/{self.project.id}/workflow/finalize-closure/",
            {
                "action": "return",
                "reason": "错误目标",
                "target_node_id": forward_node.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["message"], "退回目标不属于当前节点可退回范围")
        review.refresh_from_db()
        self.assertEqual(review.status, Review.ReviewStatus.PENDING)
