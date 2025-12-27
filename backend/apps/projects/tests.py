from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.projects.models import Project, ProjectMember
from apps.projects.services import ProjectService
from apps.reviews.services import ReviewService
from apps.reviews.models import Review

User = get_user_model()

class MidTermTestCase(TestCase):
    def setUp(self):
        # Create users
        self.student = User.objects.create_user(username='student', password='password', role='STUDENT', real_name='Student', employee_id='1001')
        self.teacher = User.objects.create_user(username='teacher', password='password', role='TEACHER', real_name='Teacher', employee_id='2001')
        self.admin = User.objects.create_user(username='admin', password='password', role='LEVEL2_ADMIN', real_name='Admin', employee_id='3001', college='CS')

        # Create project
        self.project = Project.objects.create(
            project_no='DC20250001',
            title='Test Project',
            leader=self.student,
            status=Project.ProjectStatus.IN_PROGRESS,
            year=2025
        )
        # Assign admin's college to project leader for visibility
        self.student.college = 'CS'
        self.student.save()

    def test_mid_term_flow(self):
        """
        Test the full mid-term inspection flow
        """
        # 1. Apply (Draft)
        report_file = None # Mock file not strictly needed for logic test if we bypass validation or mock it, 
                           # but service checks for it on submit. 
                           # We'll simulated file upload later or just mock the file field.
        
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

        # 4. Create midterm phase + a legacy level2 review record (admin approval path)
        phase_instance = ReviewService.create_mid_term_review(self.project)
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, Project.ProjectStatus.MID_TERM_REVIEWING)

        review = ReviewService.create_review(
            self.project,
            Review.ReviewType.MID_TERM,
            Review.ReviewLevel.LEVEL2,
            phase_instance=phase_instance,
        )
        self.assertEqual(review.status, Review.ReviewStatus.PENDING)

        # 5. Approve Review (should advance to 待结题)
        ReviewService.approve_review(review, self.admin, "Good job")
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, Project.ProjectStatus.READY_FOR_CLOSURE)

    def test_mid_term_rejection(self):
        # Setup as reviewing
        self.project.status = Project.ProjectStatus.MID_TERM_REVIEWING
        self.project.save()
        review = ReviewService.create_review(self.project, Review.ReviewType.MID_TERM, Review.ReviewLevel.LEVEL2)

        # Reject
        ReviewService.reject_review(review, self.admin, "Bad job")
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, Project.ProjectStatus.MID_TERM_REJECTED)

        # Re-submit allowed
        from django.core.files.uploadedfile import SimpleUploadedFile
        file = SimpleUploadedFile("report_v2.pdf", b"file_content", content_type="application/pdf")
        
        # apply_mid_term handles upload and status update
        ProjectService.apply_mid_term(self.project, file, is_draft=False)
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, Project.ProjectStatus.MID_TERM_SUBMITTED)
