from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.projects.models import Project, ProjectPhaseInstance
from apps.projects.services.phase_service import ProjectPhaseService
from apps.reviews.models import Review, ExpertGroup
from apps.reviews.services import ReviewService
from apps.dictionaries.models import DictionaryItem, DictionaryType
from apps.users.models import Role
from apps.system_settings.models import ProjectBatch, WorkflowConfig, WorkflowNode
from django.utils.crypto import get_random_string

User = get_user_model()

class ExpertGroupTestCase(TestCase):
    def setUp(self):
        # Create dictionary items
        type_obj, _ = DictionaryType.objects.get_or_create(
            code='PROJECT_LEVEL', defaults={"name": "Project Level", "is_system": True}
        )
        self.level, _ = DictionaryItem.objects.get_or_create(
            dict_type=type_obj,
            value='COLLEGE',
            defaults={"label": "College Level", "sort_order": 1},
        )
        college_type, _ = DictionaryType.objects.get_or_create(
            code='college', defaults={"name": "College", "is_system": True}
        )
        college_item, _ = DictionaryItem.objects.get_or_create(
            dict_type=college_type,
            value='CS',
            defaults={"label": "CS", "sort_order": 1},
        )

        # Create Admin
        password = get_random_string(12)
        level2_role = Role.objects.get(code="LEVEL2_ADMIN")
        teacher_role = Role.objects.get(code="TEACHER")
        student_role = Role.objects.get(code="STUDENT")
        self.admin = User.objects.create_user(
            username='admin',
            password=password,
            role_fk=level2_role,
            real_name='Admin',
            employee_id='9999',
            college='CS',
        )
        self.admin.managed_scope_value = college_item
        self.admin.save(update_fields=["managed_scope_value"])

        # Create Experts
        self.expert1 = User.objects.create_user(
            username='expert1',
            password=password,
            role_fk=teacher_role,
            real_name='Expert1',
            employee_id='E001',
            college='CS',
            is_expert=True,
            expert_assigned_by=self.admin,
        )
        self.expert2 = User.objects.create_user(
            username='expert2',
            password=password,
            role_fk=teacher_role,
            real_name='Expert2',
            employee_id='E002',
            college='CS',
            is_expert=True,
            expert_assigned_by=self.admin,
        )

        # Create Group
        self.group = ExpertGroup.objects.create(name="CS Review Group", created_by=self.admin)
        self.group.members.add(self.expert1, self.expert2)

        # Create batch + workflow for application
        self.batch = ProjectBatch.objects.create(
            name="2025",
            year=2025,
            code="B2025",
            status=ProjectBatch.STATUS_ACTIVE,
            is_active=True,
            is_current=True,
        )
        self.app_flow = WorkflowConfig.objects.create(
            name="Application Flow",
            phase=WorkflowConfig.Phase.APPLICATION,
            batch=self.batch,
            version=1,
            is_active=True,
        )
        student_node = WorkflowNode.objects.create(
            workflow=self.app_flow,
            code="STUDENT_SUBMIT",
            name="学生提交立项",
            node_type=WorkflowNode.NodeType.SUBMIT,
            role_fk=student_role,
            sort_order=1,
        )
        teacher_node = WorkflowNode.objects.create(
            workflow=self.app_flow,
            code="TEACHER_REVIEW",
            name="导师审核",
            node_type=WorkflowNode.NodeType.REVIEW,
            role_fk=teacher_role,
            sort_order=2,
            allowed_reject_to=student_node.id,
        )
        college_node = WorkflowNode.objects.create(
            workflow=self.app_flow,
            code="COLLEGE_REVIEW",
            name="学院审核",
            node_type=WorkflowNode.NodeType.APPROVAL,
            role_fk=level2_role,
            sort_order=3,
            require_expert_review=True,
            allowed_reject_to=teacher_node.id,
        )

        # Create Project
        self.student = User.objects.create_user(
            username='student',
            password=password,
            role_fk=student_role,
            real_name='Student',
            employee_id='1001',
        )
        self.student.college = "CS"
        self.student.save(update_fields=["college"])
        self.project = Project.objects.create(
            project_no='DC20250003',
            title='Expert Review Project',
            leader=self.student,
            status=Project.ProjectStatus.SUBMITTED,
            year=2025,
            level=self.level,
            batch=self.batch,
        )
        ProjectPhaseService.ensure_current(
            self.project,
            ProjectPhaseInstance.Phase.APPLICATION,
            step=college_node.code,
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
