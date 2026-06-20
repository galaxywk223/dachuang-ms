import datetime
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.crypto import get_random_string
from rest_framework.test import APIClient

from apps.projects.models import (
    Project,
    ProjectExpenditure,
    ProjectExpenditureReview,
)
from apps.projects.services.expenditure_workflow_service import (
    ExpenditureWorkflowService,
)
from apps.system_settings.models import ProjectBatch, WorkflowConfig, WorkflowNode
from apps.users.models import Role


User = get_user_model()


class ExpenditureWorkflowFixtureMixin:
    def setUp(self):
        super().setUp()
        password = get_random_string(12)
        self.student_role = Role.objects.get(code="STUDENT")
        self.teacher_role = Role.objects.get(code="TEACHER")
        self.level2_role = Role.objects.get(code="LEVEL2_ADMIN")
        self.level1_role, _ = Role.objects.get_or_create(
            code="LEVEL1_ADMIN",
            defaults={
                "name": "校级管理员",
                "scope_dimension": "SCHOOL",
                "is_active": True,
            },
        )
        self.level1_role.scope_dimension = "SCHOOL"
        self.level1_role.is_active = True
        self.level1_role.save(update_fields=["scope_dimension", "is_active"])

        self.leader = User.objects.create_user(
            username="expense-leader",
            password=password,
            role_fk=self.student_role,
            real_name="Leader",
            employee_id="E1001",
            college="CS",
        )
        self.reviewer = User.objects.create_user(
            username="expense-reviewer",
            password=password,
            role_fk=self.level2_role,
            real_name="Reviewer",
            employee_id="E2001",
            college="CS",
        )
        self.school_reviewer = User.objects.create_user(
            username="expense-school-reviewer",
            password=password,
            role_fk=self.level1_role,
            real_name="School Reviewer",
            employee_id="E3001",
            college="CS",
        )
        self.batch = ProjectBatch.objects.create(
            name="2026",
            year=2026,
            code="EXP2026",
            status=ProjectBatch.STATUS_ACTIVE,
            is_active=True,
            is_current=True,
        )
        self.project = Project.objects.create(
            project_no="EXP2026001",
            title="Expense Project",
            leader=self.leader,
            status=Project.ProjectStatus.IN_PROGRESS,
            year=2026,
            batch=self.batch,
            budget=Decimal("1000.00"),
        )

    def _expenditure(self):
        return ProjectExpenditure.objects.create(
            project=self.project,
            title="Server",
            amount=Decimal("100.00"),
            expenditure_date=datetime.date(2026, 1, 1),
            status=ProjectExpenditure.ExpenditureStatus.PENDING,
            created_by=self.leader,
            leader_review_status=ProjectExpenditure.LeaderReviewStatus.SKIPPED,
        )

    def _budget_workflow(self):
        return WorkflowConfig.objects.create(
            name="Budget Flow",
            phase=WorkflowConfig.Phase.BUDGET,
            batch=self.batch,
            version=1,
            is_active=True,
        )

    def _submit_node(self, workflow):
        return WorkflowNode.objects.create(
            workflow=workflow,
            code="BUDGET_SUBMIT",
            name="提交经费",
            node_type=WorkflowNode.NodeType.SUBMIT,
            role_fk=self.student_role,
            sort_order=1,
        )

    def _review_node(self, workflow, role, sort_order=2, code="BUDGET_REVIEW"):
        return WorkflowNode.objects.create(
            workflow=workflow,
            code=code,
            name="经费审核",
            node_type=WorkflowNode.NodeType.REVIEW,
            role_fk=role,
            sort_order=sort_order,
        )


class ExpenditureWorkflowTestCase(ExpenditureWorkflowFixtureMixin, TestCase):
    def test_start_workflow_rejects_missing_persisted_budget_workflow(self):
        expenditure = self._expenditure()

        with self.assertRaisesMessage(ValueError, "经费流程未配置可用审核节点"):
            ExpenditureWorkflowService.start_workflow(expenditure)

        expenditure.refresh_from_db()
        self.assertEqual(expenditure.status, ProjectExpenditure.ExpenditureStatus.PENDING)
        self.assertFalse(expenditure.reviews.exists())

    def test_start_workflow_rejects_no_usable_review_node(self):
        workflow = self._budget_workflow()
        self._submit_node(workflow)
        self._review_node(workflow, self.teacher_role)
        expenditure = self._expenditure()

        with self.assertRaisesMessage(ValueError, "经费流程未配置可用审核节点"):
            ExpenditureWorkflowService.start_workflow(expenditure)

        expenditure.refresh_from_db()
        self.assertEqual(expenditure.status, ProjectExpenditure.ExpenditureStatus.PENDING)
        self.assertFalse(expenditure.reviews.exists())

    def test_start_workflow_creates_first_persisted_review_node(self):
        workflow = self._budget_workflow()
        self._submit_node(workflow)
        review_node = self._review_node(workflow, self.level2_role)
        expenditure = self._expenditure()

        ExpenditureWorkflowService.start_workflow(expenditure)

        expenditure.refresh_from_db()
        self.assertEqual(expenditure.status, ProjectExpenditure.ExpenditureStatus.PENDING)
        self.assertEqual(expenditure.current_node_id, review_node.id)
        self.assertEqual(expenditure.reviews.count(), 1)
        self.assertEqual(expenditure.reviews.first().workflow_node_id, review_node.id)

    def test_approve_review_rejects_stale_workflow_node_and_rolls_back(self):
        workflow = self._budget_workflow()
        self._submit_node(workflow)
        self._review_node(workflow, self.level2_role)
        stale_workflow = WorkflowConfig.objects.create(
            name="Stale Flow",
            phase=WorkflowConfig.Phase.APPLICATION,
            batch=self.batch,
            version=1,
            is_active=True,
        )
        stale_node = self._review_node(
            stale_workflow,
            self.level2_role,
            code="STALE_REVIEW",
        )
        expenditure = self._expenditure()
        review = ProjectExpenditureReview.objects.create(
            expenditure=expenditure,
            workflow_node=stale_node,
            status=ProjectExpenditureReview.ReviewStatus.PENDING,
        )

        with self.assertRaisesMessage(ValueError, "当前审核节点不在经费流程配置中"):
            ExpenditureWorkflowService.approve_review(review, self.reviewer, "同意")

        review.refresh_from_db()
        expenditure.refresh_from_db()
        self.assertEqual(review.status, ProjectExpenditureReview.ReviewStatus.PENDING)
        self.assertEqual(expenditure.status, ProjectExpenditure.ExpenditureStatus.PENDING)

    def test_approve_review_rejects_previous_valid_node_and_rolls_back(self):
        workflow = self._budget_workflow()
        self._submit_node(workflow)
        first_node = self._review_node(
            workflow,
            self.level2_role,
            sort_order=2,
            code="BUDGET_COLLEGE_REVIEW",
        )
        second_node = self._review_node(
            workflow,
            self.level1_role,
            sort_order=3,
            code="BUDGET_SCHOOL_REVIEW",
        )
        expenditure = self._expenditure()
        expenditure.current_node_id = first_node.id
        expenditure.save(update_fields=["current_node_id"])
        stale_review = ProjectExpenditureReview.objects.create(
            expenditure=expenditure,
            workflow_node=first_node,
            status=ProjectExpenditureReview.ReviewStatus.PENDING,
        )
        stale_review.expenditure
        active_review = ProjectExpenditureReview.objects.create(
            expenditure=expenditure,
            workflow_node=second_node,
            status=ProjectExpenditureReview.ReviewStatus.PENDING,
        )
        ProjectExpenditure.objects.filter(pk=expenditure.pk).update(
            current_node_id=second_node.id
        )

        with self.assertRaisesMessage(ValueError, "审核记录不是当前经费流程节点"):
            ExpenditureWorkflowService.approve_review(
                stale_review, self.reviewer, "同意"
            )

        stale_review.refresh_from_db()
        active_review.refresh_from_db()
        expenditure.refresh_from_db()
        self.assertEqual(
            stale_review.status, ProjectExpenditureReview.ReviewStatus.PENDING
        )
        self.assertEqual(
            active_review.status, ProjectExpenditureReview.ReviewStatus.PENDING
        )
        self.assertEqual(expenditure.current_node_id, second_node.id)
        self.assertEqual(expenditure.status, ProjectExpenditure.ExpenditureStatus.PENDING)
        self.assertEqual(expenditure.reviews.count(), 2)

    def test_reject_review_rejects_previous_valid_node_and_rolls_back(self):
        workflow = self._budget_workflow()
        self._submit_node(workflow)
        first_node = self._review_node(
            workflow,
            self.level2_role,
            sort_order=2,
            code="BUDGET_COLLEGE_REVIEW",
        )
        second_node = self._review_node(
            workflow,
            self.level1_role,
            sort_order=3,
            code="BUDGET_SCHOOL_REVIEW",
        )
        expenditure = self._expenditure()
        expenditure.current_node_id = first_node.id
        expenditure.save(update_fields=["current_node_id"])
        stale_review = ProjectExpenditureReview.objects.create(
            expenditure=expenditure,
            workflow_node=first_node,
            status=ProjectExpenditureReview.ReviewStatus.PENDING,
        )
        stale_review.expenditure
        ProjectExpenditureReview.objects.create(
            expenditure=expenditure,
            workflow_node=second_node,
            status=ProjectExpenditureReview.ReviewStatus.PENDING,
        )
        ProjectExpenditure.objects.filter(pk=expenditure.pk).update(
            current_node_id=second_node.id
        )

        with self.assertRaisesMessage(ValueError, "审核记录不是当前经费流程节点"):
            ExpenditureWorkflowService.reject_review(
                stale_review, self.reviewer, "驳回"
            )

        stale_review.refresh_from_db()
        expenditure.refresh_from_db()
        self.assertEqual(
            stale_review.status, ProjectExpenditureReview.ReviewStatus.PENDING
        )
        self.assertEqual(expenditure.current_node_id, second_node.id)
        self.assertEqual(expenditure.status, ProjectExpenditure.ExpenditureStatus.PENDING)

    def test_pending_review_ignores_stale_review_for_previous_valid_node(self):
        workflow = self._budget_workflow()
        self._submit_node(workflow)
        first_node = self._review_node(
            workflow,
            self.level2_role,
            sort_order=2,
            code="BUDGET_COLLEGE_REVIEW",
        )
        second_node = self._review_node(
            workflow,
            self.level1_role,
            sort_order=3,
            code="BUDGET_SCHOOL_REVIEW",
        )
        expenditure = self._expenditure()
        ProjectExpenditureReview.objects.create(
            expenditure=expenditure,
            workflow_node=first_node,
            status=ProjectExpenditureReview.ReviewStatus.PENDING,
        )
        active_review = ProjectExpenditureReview.objects.create(
            expenditure=expenditure,
            workflow_node=second_node,
            status=ProjectExpenditureReview.ReviewStatus.PENDING,
        )
        expenditure.current_node_id = second_node.id
        expenditure.save(update_fields=["current_node_id"])

        result = ExpenditureWorkflowService.get_pending_review_for_user(
            expenditure, self.school_reviewer
        )

        self.assertEqual(result, {"type": "NODE", "review": active_review})


class ExpenditureWorkflowApiTestCase(ExpenditureWorkflowFixtureMixin, TestCase):
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.client.force_authenticate(user=self.leader)

    def test_create_rolls_back_when_budget_workflow_is_missing(self):
        response = self.client.post(
            "/api/v1/projects/expenditures/",
            {
                "project": self.project.id,
                "title": "Server",
                "amount": "100.00",
                "expenditure_date": "2026-01-01",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["message"], "经费流程未配置可用审核节点")
        self.assertFalse(ProjectExpenditure.objects.exists())

    def test_create_returns_wrapped_response(self):
        workflow = self._budget_workflow()
        self._submit_node(workflow)
        self._review_node(workflow, self.level2_role)

        response = self.client.post(
            "/api/v1/projects/expenditures/",
            {
                "project": self.project.id,
                "title": "Server",
                "amount": "100.00",
                "expenditure_date": "2026-01-01",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["code"], 201)
        self.assertEqual(response.data["message"], "录入成功")
        self.assertEqual(response.data["data"]["title"], "Server")

    def test_college_admin_cannot_create_expenditure_for_other_college_project(self):
        other_leader = User.objects.create_user(
            username="other-expense-leader",
            password=get_random_string(12),
            role_fk=self.student_role,
            real_name="Other Expense Leader",
            employee_id="E1002",
            college="Math",
        )
        other_project = Project.objects.create(
            project_no="EXP2026002",
            title="Other College Expense Project",
            leader=other_leader,
            status=Project.ProjectStatus.IN_PROGRESS,
            year=2026,
            batch=self.batch,
            budget=Decimal("1000.00"),
        )
        self.client.force_authenticate(user=self.reviewer)

        response = self.client.post(
            "/api/v1/projects/expenditures/",
            {
                "project": other_project.id,
                "title": "Other College Server",
                "amount": "100.00",
                "expenditure_date": "2026-01-01",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["message"], "项目不存在")
        self.assertFalse(ProjectExpenditure.objects.filter(project=other_project).exists())

    def test_create_expenditure_rejects_visible_archived_project_before_serializer(self):
        archived_batch = ProjectBatch.objects.create(
            name="2025 Archived",
            year=2025,
            code="EXP2025",
            status=ProjectBatch.STATUS_ARCHIVED,
            is_active=False,
            is_current=False,
        )
        archived_project = Project.objects.create(
            project_no="EXP2025001",
            title="Archived Expense Project",
            leader=self.leader,
            status=Project.ProjectStatus.CLOSED,
            year=2025,
            batch=archived_batch,
            budget=Decimal("1000.00"),
        )

        response = self.client.post(
            "/api/v1/projects/expenditures/",
            {
                "project": archived_project.id,
                "title": "Archived Server",
                "amount": "100.00",
                "expenditure_date": "2026-01-01",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["message"], "当前批次不允许操作该项目经费")
        self.assertFalse(ProjectExpenditure.objects.filter(project=archived_project).exists())

    def test_delete_soft_deletes_rejected_expenditure_and_hides_it(self):
        expenditure = self._expenditure()
        expenditure.status = ProjectExpenditure.ExpenditureStatus.REJECTED
        expenditure.save(update_fields=["status", "updated_at"])

        response = self.client.delete(f"/api/v1/projects/expenditures/{expenditure.id}/")

        self.assertEqual(response.status_code, 200)
        expenditure.refresh_from_db()
        self.assertTrue(expenditure.is_deleted)

        list_response = self.client.get(
            "/api/v1/projects/expenditures/",
            {"project": self.project.id},
        )
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(list_response.data["data"]["count"], 0)

    def test_delete_rejects_pending_expenditure(self):
        expenditure = self._expenditure()

        response = self.client.delete(f"/api/v1/projects/expenditures/{expenditure.id}/")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["message"], "审核中的经费记录不允许删除")
        expenditure.refresh_from_db()
        self.assertFalse(expenditure.is_deleted)
