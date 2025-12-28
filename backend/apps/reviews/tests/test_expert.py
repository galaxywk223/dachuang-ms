from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.projects.models import Project
from apps.reviews.models import Review, ExpertGroup
from apps.reviews.services import ReviewService
from apps.dictionaries.models import DictionaryItem, DictionaryType
from django.utils.crypto import get_random_string

User = get_user_model()

class ExpertGroupTestCase(TestCase):
    def setUp(self):
        # Create dictionary items
        type_obj = DictionaryType.objects.create(code='PROJECT_LEVEL', name='Project Level', is_system=True)
        self.level = DictionaryItem.objects.create(dict_type=type_obj, value='COLLEGE', label='College Level', sort_order=1)

        # Create Admin
        password = get_random_string(12)
        self.admin = User.objects.create_user(
            username='admin',
            password=password,
            role='LEVEL2_ADMIN',
            real_name='Admin',
            employee_id='9999',
            college='CS',
        )

        # Create Experts
        self.expert1 = User.objects.create_user(
            username='expert1',
            password=password,
            role='EXPERT',
            real_name='Expert1',
            employee_id='E001',
        )
        self.expert2 = User.objects.create_user(
            username='expert2',
            password=password,
            role='EXPERT',
            real_name='Expert2',
            employee_id='E002',
        )

        # Create Group
        self.group = ExpertGroup.objects.create(name="CS Review Group", created_by=self.admin)
        self.group.members.add(self.expert1, self.expert2)

        # Create Project
        self.student = User.objects.create_user(
            username='student',
            password=password,
            role='STUDENT',
            real_name='Student',
            employee_id='1001',
        )
        self.project = Project.objects.create(
            project_no='DC20250003',
            title='Expert Review Project',
            leader=self.student,
            status=Project.ProjectStatus.SUBMITTED,
            year=2025,
            level=self.level
        )

    def test_group_creation(self):
        self.assertEqual(self.group.members.count(), 2)
        self.assertEqual(self.group.name, "CS Review Group")

    def test_assign_project_to_group(self):
        # Assign
        created = ReviewService.assign_project_to_group(
            project_ids=[self.project.id],
            group_id=self.group.id,
            review_type=Review.ReviewType.APPLICATION,
            creator=self.admin
        )
        
        # Should create 2 reviews (one for each expert)
        self.assertEqual(len(created), 2)
        
        # Verify reviews exist
        reviews = Review.objects.filter(project=self.project, review_type=Review.ReviewType.APPLICATION)
        self.assertEqual(reviews.count(), 2)
        self.assertTrue(reviews.filter(reviewer=self.expert1).exists())
        self.assertTrue(reviews.filter(reviewer=self.expert2).exists())
        
        # Verify status is PENDING
        self.assertEqual(reviews.first().status, Review.ReviewStatus.PENDING)

    def test_duplicate_assignment_prevention(self):
        # Assign once
        ReviewService.assign_project_to_group(
            project_ids=[self.project.id],
            group_id=self.group.id,
            creator=self.admin
        )
        
        # Assign again
        created = ReviewService.assign_project_to_group(
            project_ids=[self.project.id],
            group_id=self.group.id,
            creator=self.admin
        )
        
        # Should not create any new reviews
        self.assertEqual(len(created), 0)
        self.assertEqual(Review.objects.filter(project=self.project).count(), 2)
