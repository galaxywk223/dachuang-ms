from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.projects.models import Project, ProjectPhaseInstance
from apps.projects.services import ProjectService
from apps.projects.services.phase_service import ProjectPhaseService
from apps.reviews.services import ReviewService
from apps.reviews.models import Review
from apps.users.models import Role
from apps.system_settings.models import ProjectBatch, WorkflowConfig, WorkflowNode
from django.utils.crypto import get_random_string

User = get_user_model()

class MidTermTestCase(TestCase):
    def setUp(self):
        # Create users
        password = get_random_string(12)
        student_role = Role.objects.get(code="STUDENT")
        teacher_role = Role.objects.get(code="TEACHER")
        level2_role = Role.objects.get(code="LEVEL2_ADMIN")
        self.student = User.objects.create_user(
            username='student',
            password=password,
            role_fk=student_role,
            real_name='Student',
            employee_id='1001',
        )
        self.teacher = User.objects.create_user(
            username='teacher',
            password=password,
            role_fk=teacher_role,
            real_name='Teacher',
            employee_id='2001',
        )
        self.admin = User.objects.create_user(
            username='admin',
            password=password,
            role_fk=level2_role,
            real_name='Admin',
            employee_id='3001',
            college='CS',
        )

        # Create batch + workflow for mid-term
        self.batch = ProjectBatch.objects.create(
            name="2025",
            year=2025,
            code="B2025",
            status=ProjectBatch.STATUS_ACTIVE,
            is_active=True,
            is_current=True,
        )
        self.midterm_flow = WorkflowConfig.objects.create(
            name="Midterm Flow",
            phase=WorkflowConfig.Phase.MID_TERM,
            batch=self.batch,
            version=1,
            is_active=True,
        )
        student_node = WorkflowNode.objects.create(
            workflow=self.midterm_flow,
            code="STUDENT_SUBMIT",
            name="学生提交中期",
            node_type=WorkflowNode.NodeType.SUBMIT,
            role_fk=student_role,
            sort_order=1,
        )
        teacher_node = WorkflowNode.objects.create(
            workflow=self.midterm_flow,
            code="TEACHER_REVIEW",
            name="导师审核",
            node_type=WorkflowNode.NodeType.REVIEW,
            role_fk=teacher_role,
            sort_order=2,
            allowed_reject_to=student_node.id,
        )
        WorkflowNode.objects.create(
            workflow=self.midterm_flow,
            code="COLLEGE_FINALIZE",
            name="学院确认",
            node_type=WorkflowNode.NodeType.APPROVAL,
            role_fk=level2_role,
            sort_order=3,
            allowed_reject_to=teacher_node.id,
        )

        # Create project
        self.project = Project.objects.create(
            project_no='DC20250001',
            title='Test Project',
            leader=self.student,
            status=Project.ProjectStatus.IN_PROGRESS,
            year=2025,
            batch=self.batch,
        )
        # Assign admin's college to project leader for visibility
        self.student.college = 'CS'
        self.student.save()

    def test_mid_term_flow(self):
        """
        Test the full mid-term inspection flow
        """
        # 1. Apply (Draft)
        # Test Draft
        ProjectService.apply_mid_term(self.project, None, is_draft=True)
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, Project.ProjectStatus.MID_TERM_DRAFT)

        # 2. Submit (Fail without file)
        with self.assertRaises(ValueError):
             ProjectService.submit_mid_term(self.project)

        # 3. Apply with File (Submit)
        # Mock file
        from django.core.files.uploadedfile import SimpleUploadedFile
        file = SimpleUploadedFile("report.pdf", b"file_content", content_type="application/pdf")
        
        ProjectService.apply_mid_term(self.project, file, is_draft=False)
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, Project.ProjectStatus.MID_TERM_SUBMITTED)
        self.assertIsNotNone(self.project.mid_term_report)
        self.assertIsNotNone(self.project.mid_term_submitted_at)

        # 4. Start workflow and approve teacher + college nodes
        ReviewService.start_phase_review(
            self.project,
            ProjectPhaseInstance.Phase.MID_TERM,
            created_by=self.student,
        )
        phase_instance = ProjectPhaseService.get_current(
            self.project, ProjectPhaseInstance.Phase.MID_TERM
        )
        review = Review.objects.filter(
            project=self.project,
            phase_instance=phase_instance,
            status=Review.ReviewStatus.PENDING,
            workflow_node_id=phase_instance.current_node_id,
        ).first()
        self.assertIsNotNone(review)
        ReviewService.approve_review(review, self.teacher, "Good job")

        phase_instance.refresh_from_db()
        admin_review = Review.objects.filter(
            project=self.project,
            phase_instance=phase_instance,
            status=Review.ReviewStatus.PENDING,
            workflow_node_id=phase_instance.current_node_id,
        ).first()
        self.assertIsNotNone(admin_review)
        ReviewService.approve_review(admin_review, self.admin, "Looks good")
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, Project.ProjectStatus.READY_FOR_CLOSURE)

    def test_mid_term_rejection(self):
        # Setup and create review
        ReviewService.start_phase_review(
            self.project,
            ProjectPhaseInstance.Phase.MID_TERM,
            created_by=self.student,
        )
        phase_instance = ProjectPhaseService.get_current(
            self.project, ProjectPhaseInstance.Phase.MID_TERM
        )
        review = Review.objects.filter(
            project=self.project,
            phase_instance=phase_instance,
            status=Review.ReviewStatus.PENDING,
            workflow_node_id=phase_instance.current_node_id,
        ).first()
        self.assertIsNotNone(review)

        # Reject
        ReviewService.reject_review(review, self.teacher, "Bad job")
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, Project.ProjectStatus.MID_TERM_RETURNED)

        # Re-submit allowed
        from django.core.files.uploadedfile import SimpleUploadedFile
        file = SimpleUploadedFile("report_v2.pdf", b"file_content", content_type="application/pdf")
        
        # apply_mid_term handles upload and status update
        ProjectService.apply_mid_term(self.project, file, is_draft=False)
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, Project.ProjectStatus.MID_TERM_SUBMITTED)
