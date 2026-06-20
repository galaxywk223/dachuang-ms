from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.crypto import get_random_string

from apps.projects.models import Project, ProjectPhaseInstance
from apps.reviews.models import Review
from apps.reviews.services import ReviewService
from apps.system_settings.models import ProjectBatch, WorkflowConfig, WorkflowNode
from apps.users.models import Role


User = get_user_model()


class ReviewServiceWorkflowTestCase(TestCase):
    def setUp(self):
        password = get_random_string(12)
        self.student_role = Role.objects.get(code="STUDENT")
        self.teacher_role = Role.objects.get(code="TEACHER")
        self.level2_role = Role.objects.get(code="LEVEL2_ADMIN")
        self.custom_college_role, _ = Role.objects.get_or_create(
            code="REVIEW_FLOW_COLLEGE_DIRECTOR",
            defaults={"name": "流程学院主管", "scope_dimension": "COLLEGE"},
        )
        self.custom_college_role.scope_dimension = "COLLEGE"
        self.custom_college_role.is_active = True
        self.custom_college_role.save(update_fields=["scope_dimension", "is_active"])
        self.custom_school_role, _ = Role.objects.get_or_create(
            code="REVIEW_FLOW_SCHOOL_DIRECTOR",
            defaults={"name": "流程学校主管", "scope_dimension": "SCHOOL"},
        )
        self.custom_school_role.scope_dimension = "SCHOOL"
        self.custom_school_role.is_active = True
        self.custom_school_role.save(update_fields=["scope_dimension", "is_active"])
        self.student = User.objects.create_user(
            username="review-flow-student",
            password=password,
            role_fk=self.student_role,
            real_name="Student",
            employee_id="RF1001",
            college="CS",
        )
        self.teacher = User.objects.create_user(
            username="review-flow-teacher",
            password=password,
            role_fk=self.teacher_role,
            real_name="Teacher",
            employee_id="RF2001",
            college="CS",
        )
        self.batch = ProjectBatch.objects.create(
            name="2026",
            year=2026,
            code="RFW2026",
            status=ProjectBatch.STATUS_ACTIVE,
            is_active=True,
            is_current=True,
        )
        self.workflow = WorkflowConfig.objects.create(
            name="Midterm Flow",
            phase=WorkflowConfig.Phase.MID_TERM,
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
        self.teacher_node = WorkflowNode.objects.create(
            workflow=self.workflow,
            code="TEACHER_REVIEW",
            name="导师审核",
            node_type=WorkflowNode.NodeType.REVIEW,
            role_fk=self.teacher_role,
            sort_order=2,
            allowed_reject_to=self.submit_node.id,
        )
        self.college_node = WorkflowNode.objects.create(
            workflow=self.workflow,
            code="COLLEGE_REVIEW",
            name="学院审核",
            node_type=WorkflowNode.NodeType.APPROVAL,
            role_fk=self.level2_role,
            sort_order=3,
            allowed_reject_to=self.teacher_node.id,
        )
        self.other_college_node = WorkflowNode.objects.create(
            workflow=self.workflow,
            code="OTHER_COLLEGE_REVIEW",
            name="其他学院审核",
            node_type=WorkflowNode.NodeType.APPROVAL,
            role_fk=self.level2_role,
            sort_order=4,
            allowed_reject_to=self.college_node.id,
        )
        self.project = Project.objects.create(
            project_no="RFW2026001",
            title="Review Flow Project",
            leader=self.student,
            status=Project.ProjectStatus.MID_TERM_REVIEWING,
            year=2026,
            batch=self.batch,
        )

    def _phase_instance(self, current_node, state=ProjectPhaseInstance.State.IN_PROGRESS):
        return ProjectPhaseInstance.objects.create(
            project=self.project,
            phase=ProjectPhaseInstance.Phase.MID_TERM,
            attempt_no=1,
            step=current_node.code,
            current_node_id=current_node.id,
            state=state,
            created_by=self.student,
        )

    def test_approve_review_rejects_stale_workflow_node_without_mutation(self):
        phase_instance = self._phase_instance(self.college_node)
        review = Review.objects.create(
            project=self.project,
            phase_instance=phase_instance,
            workflow_node=self.teacher_node,
            review_type=Review.ReviewType.MID_TERM,
            status=Review.ReviewStatus.PENDING,
        )

        with self.assertRaisesMessage(ValueError, "审核记录不属于当前流程节点"):
            ReviewService.approve_review(review, self.teacher, "同意")

        review.refresh_from_db()
        phase_instance.refresh_from_db()
        self.assertEqual(review.status, Review.ReviewStatus.PENDING)
        self.assertEqual(phase_instance.current_node_id, self.college_node.id)

    def test_reject_review_rejects_completed_phase_without_mutation(self):
        phase_instance = self._phase_instance(
            self.teacher_node,
            state=ProjectPhaseInstance.State.COMPLETED,
        )
        review = Review.objects.create(
            project=self.project,
            phase_instance=phase_instance,
            workflow_node=self.teacher_node,
            review_type=Review.ReviewType.MID_TERM,
            status=Review.ReviewStatus.PENDING,
        )

        with self.assertRaisesMessage(ValueError, "阶段流程已结束"):
            ReviewService.reject_review(review, self.teacher, "退回")

        review.refresh_from_db()
        phase_instance.refresh_from_db()
        self.assertEqual(review.status, Review.ReviewStatus.PENDING)
        self.assertEqual(phase_instance.state, ProjectPhaseInstance.State.COMPLETED)

    def test_approve_review_rejects_processed_review_without_mutation(self):
        phase_instance = self._phase_instance(self.teacher_node)
        review = Review.objects.create(
            project=self.project,
            phase_instance=phase_instance,
            workflow_node=self.teacher_node,
            review_type=Review.ReviewType.MID_TERM,
            status=Review.ReviewStatus.APPROVED,
        )

        with self.assertRaisesMessage(ValueError, "审核记录已处理，无法重复审核"):
            ReviewService.approve_review(review, self.teacher, "再次同意")

        review.refresh_from_db()
        phase_instance.refresh_from_db()
        self.assertEqual(review.status, Review.ReviewStatus.APPROVED)
        self.assertEqual(phase_instance.current_node_id, self.teacher_node.id)

    def test_reject_review_rejects_disallowed_target_node_without_mutation(self):
        phase_instance = self._phase_instance(self.college_node)
        review = Review.objects.create(
            project=self.project,
            phase_instance=phase_instance,
            workflow_node=self.college_node,
            review_type=Review.ReviewType.MID_TERM,
            status=Review.ReviewStatus.PENDING,
        )

        with self.assertRaisesMessage(
            ValueError, "退回目标不属于当前节点可退回范围"
        ):
            ReviewService.reject_review(
                review,
                self.teacher,
                "退回",
                target_node_id=self.other_college_node.id,
            )

        review.refresh_from_db()
        phase_instance.refresh_from_db()
        self.assertEqual(review.status, Review.ReviewStatus.PENDING)
        self.assertEqual(phase_instance.current_node_id, self.college_node.id)

    def test_application_status_uses_custom_college_scope_node(self):
        workflow = WorkflowConfig.objects.create(
            name="Application Custom College Flow",
            phase=WorkflowConfig.Phase.APPLICATION,
            batch=self.batch,
            version=2,
            is_active=True,
        )
        node = WorkflowNode.objects.create(
            workflow=workflow,
            code="CUSTOM_COLLEGE_APPROVAL",
            name="自定义学院审核",
            node_type=WorkflowNode.NodeType.APPROVAL,
            role_fk=self.custom_college_role,
            sort_order=1,
        )
        project = Project.objects.create(
            project_no="RFW2026002",
            title="Custom College Status Project",
            leader=self.student,
            status=Project.ProjectStatus.SUBMITTED,
            year=2026,
            batch=self.batch,
        )

        ReviewService._update_project_status_for_node(
            project,
            node,
            ProjectPhaseInstance.Phase.APPLICATION,
        )

        project.refresh_from_db()
        self.assertEqual(project.status, Project.ProjectStatus.COLLEGE_AUDITING)

    def test_closure_status_uses_custom_school_scope_node(self):
        workflow = WorkflowConfig.objects.create(
            name="Closure Custom School Flow",
            phase=WorkflowConfig.Phase.CLOSURE,
            batch=self.batch,
            version=3,
            is_active=True,
        )
        node = WorkflowNode.objects.create(
            workflow=workflow,
            code="CUSTOM_SCHOOL_APPROVAL",
            name="自定义校级审核",
            node_type=WorkflowNode.NodeType.APPROVAL,
            role_fk=self.custom_school_role,
            sort_order=1,
        )
        project = Project.objects.create(
            project_no="RFW2026003",
            title="Custom School Status Project",
            leader=self.student,
            status=Project.ProjectStatus.CLOSURE_SUBMITTED,
            year=2026,
            batch=self.batch,
        )

        ReviewService._update_project_status_for_node(
            project,
            node,
            ProjectPhaseInstance.Phase.CLOSURE,
        )

        project.refresh_from_db()
        self.assertEqual(project.status, Project.ProjectStatus.CLOSURE_LEVEL1_REVIEWING)
