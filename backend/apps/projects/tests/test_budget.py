from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.projects.models import Project, ProjectExpenditure
from apps.projects.services.budget_service import BudgetService
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

    def test_budget_stats_uses_approved_budget_when_present(self):
        self.project.approved_budget = Decimal("600.00")
        self.project.save(update_fields=["approved_budget"])

        stats = ProjectService.get_budget_stats(self.project)

        self.assertEqual(stats["total_budget"], Decimal("600.00"))
        self.assertEqual(stats["remaining_amount"], Decimal("600.00"))

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

    def test_budget_stats_ignores_rejected_and_deleted_expenditures(self):
        ProjectExpenditure.objects.create(
            project=self.project,
            title="Approved",
            amount=Decimal("200.00"),
            expenditure_date=datetime.date.today(),
            status=ProjectExpenditure.ExpenditureStatus.APPROVED,
            created_by=self.student,
        )
        ProjectExpenditure.objects.create(
            project=self.project,
            title="Rejected",
            amount=Decimal("300.00"),
            expenditure_date=datetime.date.today(),
            status=ProjectExpenditure.ExpenditureStatus.REJECTED,
            created_by=self.student,
        )
        ProjectExpenditure.objects.create(
            project=self.project,
            title="Deleted",
            amount=Decimal("400.00"),
            expenditure_date=datetime.date.today(),
            status=ProjectExpenditure.ExpenditureStatus.APPROVED,
            is_deleted=True,
            created_by=self.student,
        )

        stats = ProjectService.get_budget_stats(self.project)

        self.assertEqual(stats["used_amount"], Decimal("200.00"))
        self.assertEqual(stats["remaining_amount"], Decimal("800.00"))

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

    def test_calculate_budget_usage_uses_project_budget(self):
        stats = BudgetService.calculate_budget_usage(self.project)

        self.assertEqual(stats["total_budget"], 1000.0)
        self.assertEqual(stats["remaining"], 1000.0)

    def test_submit_expenditure_uses_project_budget_before_approval(self):
        expenditure = BudgetService.submit_expenditure(
            self.project,
            self.student,
            {
                "title": "Server",
                "amount": "500.00",
                "expenditure_date": datetime.date.today(),
            },
        )

        self.assertEqual(expenditure.amount, Decimal("500.00"))
        self.assertEqual(expenditure.status, ProjectExpenditure.ExpenditureStatus.PENDING)

    def test_submit_expenditure_rejects_invalid_amount(self):
        with self.assertRaisesMessage(ValueError, "经费金额格式错误"):
            BudgetService.submit_expenditure(
                self.project,
                self.student,
                {
                    "title": "Server",
                    "amount": "bad",
                    "expenditure_date": datetime.date.today(),
                },
            )

    def test_submit_expenditure_rejects_zero_amount(self):
        with self.assertRaisesMessage(ValueError, "经费金额必须大于0"):
            BudgetService.submit_expenditure(
                self.project,
                self.student,
                {
                    "title": "Server",
                    "amount": "0",
                    "expenditure_date": datetime.date.today(),
                },
            )

    def test_review_expenditure_completes_with_notifications(self):
        expenditure = ProjectExpenditure.objects.create(
            project=self.project,
            title="Server",
            amount=Decimal("500.00"),
            expenditure_date=datetime.date.today(),
            status=ProjectExpenditure.ExpenditureStatus.PENDING,
            created_by=self.student,
        )

        reviewed = BudgetService.review_expenditure(
            expenditure,
            self.student,
            True,
            "同意",
        )

        self.assertEqual(reviewed.status, ProjectExpenditure.ExpenditureStatus.APPROVED)
        self.assertEqual(reviewed.reviewed_by, self.student)
        self.assertEqual(reviewed.review_comment, "同意")
