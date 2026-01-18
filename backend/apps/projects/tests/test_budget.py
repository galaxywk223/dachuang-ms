from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.projects.models import Project
from apps.projects.services import ProjectService
from apps.users.models import Role
from django.utils.crypto import get_random_string
from decimal import Decimal
import datetime

User = get_user_model()

class BudgetTestCase(TestCase):
    def setUp(self):
        # Create users
        password = get_random_string(12)
        student_role = Role.objects.get(code="STUDENT")
        self.student = User.objects.create_user(
            username='student',
            password=password,
            role_fk=student_role,
            real_name='Student',
            employee_id='1001',
        )
        
        # Create project with budget 1000
        self.project = Project.objects.create(
            project_no='DC20250002',
            title='Budget Project',
            leader=self.student,
            status=Project.ProjectStatus.IN_PROGRESS,
            year=2025,
            budget=1000.00
        )

    def test_budget_stats(self):
        stats = ProjectService.get_budget_stats(self.project)
        self.assertEqual(stats['total_budget'], Decimal("1000.00"))
        self.assertEqual(stats['used_amount'], 0)
        self.assertEqual(stats['remaining_amount'], Decimal("1000.00"))

    def test_add_expenditure_success(self):
        ProjectService.add_expenditure(
            self.project, 
            "Server", 
            500.00, 
            datetime.date.today(),
            None,
            self.student,
        )
        stats = ProjectService.get_budget_stats(self.project)
        self.assertEqual(stats['used_amount'], Decimal("500.00"))
        self.assertEqual(stats['remaining_amount'], Decimal("500.00"))
        self.assertEqual(stats['usage_rate'], 50.0)

    def test_add_expenditure_failure_over_budget(self):
        # First 500
        ProjectService.add_expenditure(
            self.project, 
            "Server", 
            500.00, 
            datetime.date.today(),
            None,
            self.student,
        )
        # Try add 600 > 500 remaining
        with self.assertRaises(ValueError):
            ProjectService.add_expenditure(
                self.project, 
                "GPU", 
                600.00, 
                datetime.date.today(),
                None,
                self.student,
            )
