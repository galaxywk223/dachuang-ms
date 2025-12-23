from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.projects.models import Project, ProjectExpenditure
from apps.dictionaries.models import DictionaryItem, DictionaryType
from apps.projects.services import ProjectService
import datetime

User = get_user_model()

class BudgetTestCase(TestCase):
    def setUp(self):
        # Create users
        self.student = User.objects.create_user(username='student', password='password', role='STUDENT', real_name='Student', employee_id='1001')
        
        # Create dictionary item for category
        type_obj = DictionaryType.objects.create(code='EXPENDITURE_CATEGORY', name='支出类别', is_system=True)
        self.category = DictionaryItem.objects.create(dict_type=type_obj, value='MATERIAL', label='Hardware', sort_order=1)

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
        self.assertEqual(stats['total_budget'], 1000.00)
        self.assertEqual(stats['used_amount'], 0)
        self.assertEqual(stats['remaining_amount'], 1000.00)

    def test_add_expenditure_success(self):
        ProjectService.add_expenditure(
            self.project, 
            self.student, 
            "Server", 
            500.00, 
            datetime.date.today(), 
            self.category
        )
        stats = ProjectService.get_budget_stats(self.project)
        self.assertEqual(stats['used_amount'], 500.00)
        self.assertEqual(stats['remaining_amount'], 500.00)
        self.assertEqual(stats['usage_rate'], 50.0)

    def test_add_expenditure_failure_over_budget(self):
        # First 500
        ProjectService.add_expenditure(
            self.project, 
            self.student, 
            "Server", 
            500.00, 
            datetime.date.today(), 
            self.category
        )
        # Try add 600 > 500 remaining
        with self.assertRaises(ValueError):
            ProjectService.add_expenditure(
                self.project, 
                self.student, 
                "GPU", 
                600.00, 
                datetime.date.today(), 
                self.category
            )
