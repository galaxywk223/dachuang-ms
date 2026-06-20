from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.projects.models import Project, ProjectChangeRequest, ProjectChangeReview
from apps.projects.services.change_service import ProjectChangeService
from apps.projects.views.public.changes import ProjectChangeRequestViewSet
from apps.dictionaries.models import DictionaryItem, DictionaryType
from apps.system_settings.models import ProjectBatch, WorkflowConfig, WorkflowNode
from apps.users.models import Role


User = get_user_model()


class ProjectChangeServiceTestCase(TestCase):
    def setUp(self):
        self.student_role = self._role("STUDENT", "学生")
        self.college_admin_role = self._role("LEVEL2_ADMIN", "院级管理员", "COLLEGE")
        self.admin_role = self._role("LEVEL1_ADMIN", "校级管理员", "SCHOOL")
        college_type, _ = DictionaryType.objects.get_or_create(
            code="college",
            defaults={"name": "学院", "is_system": True},
        )
        self.college_item, _ = DictionaryItem.objects.get_or_create(
            dict_type=college_type,
            value="计算机学院",
            defaults={"label": "计算机学院", "sort_order": 1},
        )
        self.student = User.objects.create_user(
            username="change_student",
            password="password123",
            role_fk=self.student_role,
            real_name="异动负责人",
            employee_id="CH10001",
            college="计算机学院",
        )
        self.college_admin = User.objects.create_user(
            username="change_college_admin",
            password="password123",
            role_fk=self.college_admin_role,
            real_name="异动院级管理员",
            employee_id="CH15001",
            college="计算机学院",
            managed_scope_value=self.college_item,
        )
        self.admin = User.objects.create_user(
            username="change_admin",
            password="password123",
            role_fk=self.admin_role,
            real_name="异动管理员",
            employee_id="CH20001",
        )
        self.batch = ProjectBatch.objects.create(
            name="2026",
            year=2026,
            code="CH2026",
            status=ProjectBatch.STATUS_ACTIVE,
            is_active=True,
            is_current=True,
        )
        self.project = Project.objects.create(
            project_no="CH20260001",
            title="异动测试项目",
            leader=self.student,
            status=Project.ProjectStatus.IN_PROGRESS,
            year=2026,
            batch=self.batch,
        )
        self.workflow = WorkflowConfig.objects.create(
            name="Change Workflow",
            phase="CHANGE",
            batch=self.batch,
            version=1,
            is_active=True,
        )
        self.college_node = WorkflowNode.objects.create(
            workflow=self.workflow,
            code="COLLEGE_REVIEW",
            name="院级审核",
            node_type=WorkflowNode.NodeType.APPROVAL,
            role_fk=self.college_admin_role,
            sort_order=1,
        )
        self.node = WorkflowNode.objects.create(
            workflow=self.workflow,
            code="SCHOOL_REVIEW",
            name="校级审核",
            node_type=WorkflowNode.NodeType.APPROVAL,
            role_fk=self.admin_role,
            sort_order=2,
        )
        self.custom_college_role = self._role(
            "CHANGE_COLLEGE_SECRETARY", "异动学院秘书", "COLLEGE"
        )
        self.custom_college_admin = User.objects.create_user(
            username="change_custom_college_admin",
            password="password123",
            role_fk=self.custom_college_role,
            real_name="异动学院秘书",
            employee_id="CH16001",
            college="计算机学院",
            managed_scope_value=self.college_item,
        )

    def _role(self, code, name, scope_dimension=None):
        role, _ = Role.objects.get_or_create(code=code, defaults={"name": name})
        role.name = name
        role.scope_dimension = scope_dimension
        role.is_active = True
        role.save(update_fields=["name", "scope_dimension", "is_active"])
        return role

    def _make_change_review(self, *, request_status, review_status):
        change_request = ProjectChangeRequest.objects.create(
            project=self.project,
            request_type=ProjectChangeRequest.ChangeType.CHANGE,
            status=request_status,
            reason="change",
            change_data={"title": "更新后的项目标题"},
            created_by=self.student,
        )
        review = ProjectChangeReview.objects.create(
            change_request=change_request,
            workflow_node=self.node,
            status=review_status,
        )
        return change_request, review

    def test_approve_review_rejects_non_pending_review(self):
        change_request, review = self._make_change_review(
            request_status=ProjectChangeRequest.ChangeStatus.LEVEL1_REVIEWING,
            review_status=ProjectChangeReview.ReviewStatus.APPROVED,
        )

        with self.assertRaisesMessage(ValueError, "审核记录已处理，无法重复审核"):
            ProjectChangeService.approve_review(review, self.admin, "")

        change_request.refresh_from_db()
        self.project.refresh_from_db()
        self.assertEqual(
            change_request.status,
            ProjectChangeRequest.ChangeStatus.LEVEL1_REVIEWING,
        )
        self.assertEqual(self.project.title, "异动测试项目")

    def test_reject_review_rejects_finished_change_request(self):
        change_request, review = self._make_change_review(
            request_status=ProjectChangeRequest.ChangeStatus.APPROVED,
            review_status=ProjectChangeReview.ReviewStatus.PENDING,
        )

        with self.assertRaisesMessage(ValueError, "异动流程已结束，无法处理该审核记录"):
            ProjectChangeService.reject_review(review, self.admin, "")

        change_request.refresh_from_db()
        review.refresh_from_db()
        self.assertEqual(change_request.status, ProjectChangeRequest.ChangeStatus.APPROVED)
        self.assertEqual(review.status, ProjectChangeReview.ReviewStatus.PENDING)

    def test_approve_review_rejects_previous_valid_node_and_rolls_back(self):
        change_request = ProjectChangeRequest.objects.create(
            project=self.project,
            request_type=ProjectChangeRequest.ChangeType.CHANGE,
            status=ProjectChangeRequest.ChangeStatus.LEVEL2_REVIEWING,
            reason="change",
            change_data={"title": "更新后的项目标题"},
            created_by=self.student,
        )
        stale_review = ProjectChangeReview.objects.create(
            change_request=change_request,
            workflow_node=self.college_node,
            status=ProjectChangeReview.ReviewStatus.PENDING,
        )
        stale_review.change_request
        active_review = ProjectChangeReview.objects.create(
            change_request=change_request,
            workflow_node=self.node,
            status=ProjectChangeReview.ReviewStatus.PENDING,
        )
        ProjectChangeRequest.objects.filter(pk=change_request.pk).update(
            status=ProjectChangeRequest.ChangeStatus.LEVEL1_REVIEWING
        )

        with self.assertRaisesMessage(ValueError, "审核记录不是当前异动流程节点"):
            ProjectChangeService.approve_review(
                stale_review, self.college_admin, "同意"
            )

        stale_review.refresh_from_db()
        active_review.refresh_from_db()
        change_request.refresh_from_db()
        self.project.refresh_from_db()
        self.assertEqual(stale_review.status, ProjectChangeReview.ReviewStatus.PENDING)
        self.assertEqual(active_review.status, ProjectChangeReview.ReviewStatus.PENDING)
        self.assertEqual(
            change_request.status,
            ProjectChangeRequest.ChangeStatus.LEVEL1_REVIEWING,
        )
        self.assertEqual(self.project.title, "异动测试项目")
        self.assertEqual(change_request.reviews.count(), 2)

    def test_reject_review_rejects_previous_valid_node_and_rolls_back(self):
        change_request = ProjectChangeRequest.objects.create(
            project=self.project,
            request_type=ProjectChangeRequest.ChangeType.CHANGE,
            status=ProjectChangeRequest.ChangeStatus.LEVEL2_REVIEWING,
            reason="change",
            change_data={"title": "更新后的项目标题"},
            created_by=self.student,
        )
        stale_review = ProjectChangeReview.objects.create(
            change_request=change_request,
            workflow_node=self.college_node,
            status=ProjectChangeReview.ReviewStatus.PENDING,
        )
        stale_review.change_request
        ProjectChangeReview.objects.create(
            change_request=change_request,
            workflow_node=self.node,
            status=ProjectChangeReview.ReviewStatus.PENDING,
        )
        ProjectChangeRequest.objects.filter(pk=change_request.pk).update(
            status=ProjectChangeRequest.ChangeStatus.LEVEL1_REVIEWING
        )

        with self.assertRaisesMessage(ValueError, "审核记录不是当前异动流程节点"):
            ProjectChangeService.reject_review(
                stale_review, self.college_admin, "驳回"
            )

        stale_review.refresh_from_db()
        change_request.refresh_from_db()
        self.assertEqual(stale_review.status, ProjectChangeReview.ReviewStatus.PENDING)
        self.assertEqual(
            change_request.status,
            ProjectChangeRequest.ChangeStatus.LEVEL1_REVIEWING,
        )

    def test_pending_review_lookup_ignores_stale_previous_valid_node(self):
        change_request = ProjectChangeRequest.objects.create(
            project=self.project,
            request_type=ProjectChangeRequest.ChangeType.CHANGE,
            status=ProjectChangeRequest.ChangeStatus.LEVEL1_REVIEWING,
            reason="change",
            change_data={},
            created_by=self.student,
        )
        ProjectChangeReview.objects.create(
            change_request=change_request,
            workflow_node=self.college_node,
            status=ProjectChangeReview.ReviewStatus.PENDING,
        )
        active_review = ProjectChangeReview.objects.create(
            change_request=change_request,
            workflow_node=self.node,
            status=ProjectChangeReview.ReviewStatus.PENDING,
        )

        review = ProjectChangeRequestViewSet()._get_pending_review(
            change_request, self.admin
        )

        self.assertEqual(review, active_review)

    def test_submit_request_supports_custom_college_scoped_role(self):
        custom_workflow = WorkflowConfig.objects.create(
            name="Custom Change Workflow",
            phase="CHANGE",
            batch=self.batch,
            version=2,
            is_active=True,
        )
        custom_node = WorkflowNode.objects.create(
            workflow=custom_workflow,
            code="CUSTOM_COLLEGE_REVIEW",
            name="自定义学院审核",
            node_type=WorkflowNode.NodeType.APPROVAL,
            role_fk=self.custom_college_role,
            sort_order=1,
        )
        change_request = ProjectChangeRequest.objects.create(
            project=self.project,
            request_type=ProjectChangeRequest.ChangeType.CHANGE,
            status=ProjectChangeRequest.ChangeStatus.DRAFT,
            reason="custom role change",
            change_data={},
            created_by=self.student,
        )

        ProjectChangeService.submit_request(change_request)

        change_request.refresh_from_db()
        self.assertEqual(
            change_request.status,
            ProjectChangeRequest.ChangeStatus.LEVEL2_REVIEWING,
        )
        review = ProjectChangeReview.objects.get(change_request=change_request)
        self.assertEqual(review.workflow_node_id, custom_node.id)

    def test_lock_request_only_locks_change_request_row(self):
        change_request = ProjectChangeRequest.objects.create(
            project=self.project,
            request_type=ProjectChangeRequest.ChangeType.CHANGE,
            status=ProjectChangeRequest.ChangeStatus.DRAFT,
            reason="lock scope",
            change_data={},
            created_by=self.student,
        )

        queryset = (
            ProjectChangeRequest.objects.select_for_update(of=("self",))
            .select_related("project")
            .filter(pk=change_request.pk)
        )
        sql = str(queryset.query)

        self.assertIn("FOR UPDATE OF", sql)
        self.assertIn('"project_change_requests"', sql)
        self.assertNotIn('"projects_project"', sql.split("FOR UPDATE OF", 1)[1])

    def test_submit_request_rejects_stale_closed_project_draft(self):
        change_request = ProjectChangeRequest.objects.create(
            project=self.project,
            request_type=ProjectChangeRequest.ChangeType.CHANGE,
            status=ProjectChangeRequest.ChangeStatus.DRAFT,
            reason="stale closed project change",
            change_data={},
            created_by=self.student,
        )
        self.project.status = Project.ProjectStatus.CLOSED
        self.project.save(update_fields=["status", "updated_at"])

        with self.assertRaisesMessage(ValueError, "项目已结题或终止，无法申请异动"):
            ProjectChangeService.submit_request(change_request)

        change_request.refresh_from_db()
        self.assertEqual(change_request.status, ProjectChangeRequest.ChangeStatus.DRAFT)
        self.assertIsNone(change_request.submitted_at)
        self.assertFalse(
            ProjectChangeReview.objects.filter(change_request=change_request).exists()
        )

    def test_submit_request_rejects_non_current_batch_project(self):
        archived_batch = ProjectBatch.objects.create(
            name="2025",
            year=2025,
            code="CH2025",
            status=ProjectBatch.STATUS_ARCHIVED,
            is_active=True,
            is_current=False,
        )
        archived_project = Project.objects.create(
            project_no="CH20250001",
            title="历史批次异动项目",
            leader=self.student,
            status=Project.ProjectStatus.IN_PROGRESS,
            year=2025,
            batch=archived_batch,
        )
        change_request = ProjectChangeRequest.objects.create(
            project=archived_project,
            request_type=ProjectChangeRequest.ChangeType.CHANGE,
            status=ProjectChangeRequest.ChangeStatus.DRAFT,
            reason="stale batch change",
            change_data={},
            created_by=self.student,
        )

        with self.assertRaisesMessage(ValueError, "当前批次不允许提交该异动申请"):
            ProjectChangeService.submit_request(change_request)

        change_request.refresh_from_db()
        self.assertEqual(change_request.status, ProjectChangeRequest.ChangeStatus.DRAFT)
        self.assertIsNone(change_request.submitted_at)
        self.assertFalse(
            ProjectChangeReview.objects.filter(change_request=change_request).exists()
        )

    def test_pending_review_lookup_supports_custom_college_scoped_role(self):
        custom_node = WorkflowNode.objects.create(
            workflow=self.workflow,
            code="CUSTOM_COLLEGE_REVIEW",
            name="自定义学院审核",
            node_type=WorkflowNode.NodeType.APPROVAL,
            role_fk=self.custom_college_role,
            sort_order=3,
        )
        change_request = ProjectChangeRequest.objects.create(
            project=self.project,
            request_type=ProjectChangeRequest.ChangeType.CHANGE,
            status=ProjectChangeRequest.ChangeStatus.LEVEL2_REVIEWING,
            reason="custom role change",
            change_data={},
            created_by=self.student,
        )
        active_review = ProjectChangeReview.objects.create(
            change_request=change_request,
            workflow_node=custom_node,
            status=ProjectChangeReview.ReviewStatus.PENDING,
        )

        review = ProjectChangeRequestViewSet()._get_pending_review(
            change_request, self.custom_college_admin
        )

        self.assertEqual(review, active_review)

    def test_pending_review_lookup_falls_back_to_college_for_legacy_college_admin(self):
        legacy_admin = User.objects.create_user(
            username="change_legacy_college_admin",
            password="password123",
            role_fk=self.college_admin_role,
            real_name="旧学院管理员",
            employee_id="CH15002",
            college="计算机学院",
        )
        change_request = ProjectChangeRequest.objects.create(
            project=self.project,
            request_type=ProjectChangeRequest.ChangeType.CHANGE,
            status=ProjectChangeRequest.ChangeStatus.LEVEL2_REVIEWING,
            reason="legacy college admin change",
            change_data={},
            created_by=self.student,
        )
        active_review = ProjectChangeReview.objects.create(
            change_request=change_request,
            workflow_node=self.college_node,
            status=ProjectChangeReview.ReviewStatus.PENDING,
        )

        review = ProjectChangeRequestViewSet()._get_pending_review(
            change_request, legacy_admin
        )

        self.assertEqual(review, active_review)
