from django.contrib.auth import get_user_model
from decimal import Decimal
from django.test import TestCase
from rest_framework.test import APIClient

from apps.projects.models import Project, ProjectChangeRequest, ProjectPhaseInstance
from apps.reviews.models import ExpertGroup, Review
from apps.reviews.services import ReviewService
from apps.reviews.views.review import _parse_approved_budget
from apps.system_settings.models import ProjectBatch, WorkflowConfig, WorkflowNode
from apps.utils.pagination import non_negative_int
from apps.users.models import Role


User = get_user_model()


class ReviewApiValidationTestCase(TestCase):
    def setUp(self):
        role, _ = Role.objects.get_or_create(
            code="LEVEL2_ADMIN",
            defaults={"name": "学院管理员", "scope_dimension": "COLLEGE"},
        )
        level1_role, _ = Role.objects.get_or_create(
            code="LEVEL1_ADMIN",
            defaults={"name": "校级管理员", "scope_dimension": "SCHOOL"},
        )
        role.scope_dimension = "COLLEGE"
        role.is_active = True
        role.save(update_fields=["scope_dimension", "is_active"])
        level1_role.scope_dimension = "SCHOOL"
        level1_role.is_active = True
        level1_role.save(update_fields=["scope_dimension", "is_active"])
        self.admin = User.objects.create_user(
            username="review_admin",
            password="password123",
            role_fk=role,
            real_name="审核管理员",
            employee_id="R20001",
            college="计算机学院",
        )
        self.level1_admin = User.objects.create_user(
            username="review_level1_admin",
            password="password123",
            role_fk=level1_role,
            real_name="校级审核管理员",
            employee_id="R10001",
        )
        student_role, _ = Role.objects.get_or_create(
            code="STUDENT",
            defaults={"name": "学生"},
        )
        self.student = User.objects.create_user(
            username="review_student",
            password="password123",
            role_fk=student_role,
            real_name="项目负责人",
            employee_id="RS10001",
            college="计算机学院",
        )
        self.batch = ProjectBatch.objects.create(
            name="2026",
            year=2026,
            code="RV2026",
            status=ProjectBatch.STATUS_ACTIVE,
            is_active=True,
            is_current=True,
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

    def _workflow_node(self, batch):
        workflow = WorkflowConfig.objects.create(
            name=f"Batch Review Workflow {batch.id}",
            phase=WorkflowConfig.Phase.APPLICATION,
            batch=batch,
            version=1,
            is_active=True,
        )
        return WorkflowNode.objects.create(
            workflow=workflow,
            code="COLLEGE_REVIEW",
            name="学院审核",
            node_type=WorkflowNode.NodeType.APPROVAL,
            role_fk=self.admin.role_fk,
            sort_order=1,
        )

    def _pending_review(self, batch, project_no):
        project = Project.objects.create(
            project_no=project_no,
            title=f"{project_no} Project",
            leader=self.student,
            status=Project.ProjectStatus.COLLEGE_AUDITING,
            year=batch.year,
            batch=batch,
        )
        node = self._workflow_node(batch)
        phase_instance = ProjectPhaseInstance.objects.create(
            project=project,
            phase=ProjectPhaseInstance.Phase.APPLICATION,
            attempt_no=1,
            step=node.code,
            current_node_id=node.id,
            state=ProjectPhaseInstance.State.IN_PROGRESS,
            created_by=self.student,
        )
        return Review.objects.create(
            project=project,
            phase_instance=phase_instance,
            workflow_node=node,
            review_type=Review.ReviewType.APPLICATION,
            status=Review.ReviewStatus.PENDING,
        )

    def _pending_review_with_reject_chain(self, project_no):
        workflow = WorkflowConfig.objects.create(
            name=f"Batch Reject Workflow {project_no}",
            phase=WorkflowConfig.Phase.APPLICATION,
            batch=self.batch,
            version=1,
            is_active=True,
        )
        submit_node = WorkflowNode.objects.create(
            workflow=workflow,
            code="SUBMIT",
            name="学生提交",
            node_type=WorkflowNode.NodeType.SUBMIT,
            role_fk=Role.objects.get(code="STUDENT"),
            sort_order=1,
        )
        teacher_node = WorkflowNode.objects.create(
            workflow=workflow,
            code="TEACHER_REVIEW",
            name="导师审核",
            node_type=WorkflowNode.NodeType.REVIEW,
            role_fk=Role.objects.get(code="TEACHER"),
            sort_order=2,
            allowed_reject_to=submit_node.id,
        )
        college_node = WorkflowNode.objects.create(
            workflow=workflow,
            code="COLLEGE_REVIEW",
            name="学院审核",
            node_type=WorkflowNode.NodeType.APPROVAL,
            role_fk=self.admin.role_fk,
            sort_order=3,
            allowed_reject_to=teacher_node.id,
        )
        other_node = WorkflowNode.objects.create(
            workflow=workflow,
            code="OTHER_REVIEW",
            name="其他审核",
            node_type=WorkflowNode.NodeType.APPROVAL,
            role_fk=self.admin.role_fk,
            sort_order=4,
            allowed_reject_to=college_node.id,
        )
        project = Project.objects.create(
            project_no=project_no,
            title=f"{project_no} Project",
            leader=self.student,
            status=Project.ProjectStatus.COLLEGE_AUDITING,
            year=self.batch.year,
            batch=self.batch,
        )
        phase_instance = ProjectPhaseInstance.objects.create(
            project=project,
            phase=ProjectPhaseInstance.Phase.APPLICATION,
            attempt_no=1,
            step=college_node.code,
            current_node_id=college_node.id,
            state=ProjectPhaseInstance.State.IN_PROGRESS,
            created_by=self.student,
        )
        review = Review.objects.create(
            project=project,
            phase_instance=phase_instance,
            workflow_node=college_node,
            review_type=Review.ReviewType.APPLICATION,
            status=Review.ReviewStatus.PENDING,
        )
        return review, teacher_node, other_node

    def test_assign_batch_rejects_invalid_target_node_id(self):
        self.assertEqual(ExpertGroup.GroupScope.COLLEGE, "COLLEGE")
        group = ExpertGroup.objects.create(
            name="专家组",
            scope=ExpertGroup.GroupScope.COLLEGE,
            created_by=self.admin,
        )

        response = self.client.post(
            "/api/v1/reviews/assignments/assign_batch/",
            {
                "project_ids": [1],
                "group_id": group.id,
                "target_node_id": "bad",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["message"], "Invalid target_node_id")

    def test_submit_to_level1_rejects_invalid_project_id(self):
        response = self.client.post(
            "/api/v1/reviews/submit-to-level1/",
            {"project_id": "invalid"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["message"], "项目ID不合法")

    def test_batch_review_rejects_invalid_review_ids(self):
        response = self.client.post(
            "/api/v1/reviews/batch-review/",
            {"review_ids": ["invalid"], "action": "approve"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["message"], "review_ids不合法")

    def test_batch_review_scopes_reviews_to_current_batch(self):
        archived_batch = ProjectBatch.objects.create(
            name="2025",
            year=2025,
            code="RV2025-BATCH",
            status=ProjectBatch.STATUS_ARCHIVED,
            is_active=True,
            is_current=False,
        )
        current_review = self._pending_review(self.batch, "RV20260002")
        archived_review = self._pending_review(archived_batch, "RV20250002")

        response = self.client.post(
            "/api/v1/reviews/batch-review/",
            {
                "review_ids": [current_review.id, archived_review.id],
                "action": "approve",
                "comments": "同意",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"]["success"], 1)
        current_review.refresh_from_db()
        archived_review.refresh_from_db()
        self.assertEqual(current_review.status, Review.ReviewStatus.APPROVED)
        self.assertEqual(archived_review.status, Review.ReviewStatus.PENDING)

    def test_reject_review_rejects_disallowed_target_node(self):
        review, _teacher_node, other_node = self._pending_review_with_reject_chain(
            "RV20260009"
        )

        response = self.client.post(
            f"/api/v1/reviews/{review.id}/review/",
            {
                "action": "reject",
                "comments": "退回",
                "target_node_id": other_node.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["message"], "退回目标不属于当前节点可退回范围")
        review.refresh_from_db()
        self.assertEqual(review.status, Review.ReviewStatus.PENDING)

    def test_batch_review_honors_target_node_id_for_reject(self):
        review, teacher_node, _other_node = self._pending_review_with_reject_chain(
            "RV20260010"
        )

        response = self.client.post(
            "/api/v1/reviews/batch-review/",
            {
                "review_ids": [review.id],
                "action": "reject",
                "comments": "退回导师",
                "target_node_id": teacher_node.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"]["success"], 1)
        self.assertEqual(response.data["data"]["failed"], [])
        review.refresh_from_db()
        self.assertEqual(review.status, Review.ReviewStatus.REJECTED)
        new_phase = ProjectPhaseInstance.objects.filter(
            project=review.project,
            phase=ProjectPhaseInstance.Phase.APPLICATION,
            state=ProjectPhaseInstance.State.IN_PROGRESS,
        ).latest("attempt_no")
        self.assertEqual(new_phase.current_node_id, teacher_node.id)

    def test_batch_review_reports_disallowed_target_node(self):
        review, _teacher_node, other_node = self._pending_review_with_reject_chain(
            "RV20260011"
        )

        response = self.client.post(
            "/api/v1/reviews/batch-review/",
            {
                "review_ids": [review.id],
                "action": "reject",
                "comments": "退回",
                "target_node_id": other_node.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"]["success"], 0)
        self.assertEqual(
            response.data["data"]["failed"],
            [{"id": review.id, "reason": "退回目标不属于当前节点可退回范围"}],
        )
        review.refresh_from_db()
        self.assertEqual(review.status, Review.ReviewStatus.PENDING)

    def test_revise_rejected_review_updates_comment_without_rejecting_again(self):
        review = self._pending_review(self.batch, "RV20260004")
        review.status = Review.ReviewStatus.REJECTED
        review.reviewer = self.admin
        review.comments = "原驳回意见"
        review.save(update_fields=["status", "reviewer", "comments"])

        response = self.client.post(
            f"/api/v1/reviews/{review.id}/revise/",
            {"action": "reject", "comments": "修订后的驳回意见"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        review.refresh_from_db()
        self.assertEqual(review.status, Review.ReviewStatus.REJECTED)
        self.assertEqual(review.comments, "修订后的驳回意见")

    def test_revise_rejects_status_switch_without_mutation(self):
        review = self._pending_review(self.batch, "RV20260005")
        review.status = Review.ReviewStatus.REJECTED
        review.reviewer = self.admin
        review.comments = "原驳回意见"
        review.save(update_fields=["status", "reviewer", "comments"])

        response = self.client.post(
            f"/api/v1/reviews/{review.id}/revise/",
            {"action": "approve", "comments": "改为通过"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["message"], "审核结果修订不能切换通过/驳回状态")
        review.refresh_from_db()
        self.assertEqual(review.status, Review.ReviewStatus.REJECTED)
        self.assertEqual(review.comments, "原驳回意见")

    def test_level1_approval_does_not_save_budget_when_workflow_fails(self):
        workflow = WorkflowConfig.objects.create(
            name="Level1 Application Workflow",
            phase=WorkflowConfig.Phase.APPLICATION,
            batch=self.batch,
            version=2,
            is_active=True,
        )
        level1_node = WorkflowNode.objects.create(
            workflow=workflow,
            code="SCHOOL_REVIEW",
            name="校级审核",
            node_type=WorkflowNode.NodeType.APPROVAL,
            role_fk=self.level1_admin.role_fk,
            sort_order=1,
        )
        project = Project.objects.create(
            project_no="RV20260003",
            title="Stale Level1 Project",
            leader=self.student,
            status=Project.ProjectStatus.LEVEL1_AUDITING,
            year=self.batch.year,
            batch=self.batch,
            approved_budget=Decimal("100.00"),
        )
        phase_instance = ProjectPhaseInstance.objects.create(
            project=project,
            phase=ProjectPhaseInstance.Phase.APPLICATION,
            attempt_no=1,
            step=level1_node.code,
            current_node_id=None,
            state=ProjectPhaseInstance.State.IN_PROGRESS,
            created_by=self.student,
        )
        review = Review.objects.create(
            project=project,
            phase_instance=phase_instance,
            workflow_node=level1_node,
            review_type=Review.ReviewType.APPLICATION,
            status=Review.ReviewStatus.PENDING,
        )
        self.client.force_authenticate(user=self.level1_admin)

        response = self.client.post(
            f"/api/v1/reviews/{review.id}/review/",
            {
                "action": "approve",
                "comments": "同意",
                "approved_budget": "200.00",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["message"], "流程状态异常：缺少当前节点")
        project.refresh_from_db()
        review.refresh_from_db()
        self.assertEqual(project.approved_budget, Decimal("100.00"))
        self.assertEqual(review.status, Review.ReviewStatus.PENDING)

    def test_custom_school_approval_requires_approved_budget(self):
        custom_school_role, _ = Role.objects.get_or_create(
            code="SCHOOL_APPLICATION_REVIEW",
            defaults={"name": "校级立项审核", "scope_dimension": "SCHOOL"},
        )
        custom_school_role.scope_dimension = "SCHOOL"
        custom_school_role.is_active = True
        custom_school_role.save(update_fields=["scope_dimension", "is_active"])
        custom_school_admin = User.objects.create_user(
            username="review_custom_school_admin",
            password="password123",
            role_fk=custom_school_role,
            real_name="校级立项审核",
            employee_id="R10002",
        )
        project = Project.objects.create(
            project_no="RV20260008",
            title="Custom School Budget Project",
            leader=self.student,
            status=Project.ProjectStatus.LEVEL1_AUDITING,
            year=2026,
            batch=self.batch,
        )
        workflow = WorkflowConfig.objects.create(
            name="Custom School Budget Workflow",
            phase=WorkflowConfig.Phase.APPLICATION,
            batch=self.batch,
            version=5,
            is_active=True,
        )
        node = WorkflowNode.objects.create(
            workflow=workflow,
            code="CUSTOM_SCHOOL_REVIEW",
            name="自定义校级审核",
            node_type=WorkflowNode.NodeType.APPROVAL,
            role_fk=custom_school_role,
            sort_order=1,
        )
        phase_instance = ProjectPhaseInstance.objects.create(
            project=project,
            phase=ProjectPhaseInstance.Phase.APPLICATION,
            attempt_no=1,
            step=node.code,
            current_node_id=node.id,
            state=ProjectPhaseInstance.State.IN_PROGRESS,
            created_by=self.student,
        )
        review = Review.objects.create(
            project=project,
            phase_instance=phase_instance,
            workflow_node=node,
            review_type=Review.ReviewType.APPLICATION,
            status=Review.ReviewStatus.PENDING,
        )
        self.client.force_authenticate(user=custom_school_admin)

        response = self.client.post(
            f"/api/v1/reviews/{review.id}/review/",
            {"action": "approve", "comments": "同意立项"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["message"], "请填写批准经费")
        review.refresh_from_db()
        self.assertEqual(review.status, Review.ReviewStatus.PENDING)

    def test_review_list_tolerates_invalid_project_filter(self):
        response = self.client.get(
            "/api/v1/reviews/",
            {"project": "invalid"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 0)

    def test_custom_college_admin_review_list_is_college_scoped(self):
        custom_role, _ = Role.objects.get_or_create(
            code="COLLEGE_SECRETARY",
            defaults={"name": "学院秘书", "scope_dimension": "COLLEGE"},
        )
        custom_role.scope_dimension = "COLLEGE"
        custom_role.is_active = True
        custom_role.save(update_fields=["scope_dimension", "is_active"])
        custom_admin = User.objects.create_user(
            username="review_custom_college_admin",
            password="password123",
            role_fk=custom_role,
            real_name="学院秘书",
            employee_id="R30001",
            college="计算机学院",
        )
        student_role = Role.objects.get(code="STUDENT")
        other_student = User.objects.create_user(
            username="review_other_college_student",
            password="password123",
            role_fk=student_role,
            real_name="外院负责人",
            employee_id="RS20001",
            college="数学学院",
        )
        workflow = WorkflowConfig.objects.create(
            name="Custom College Workflow",
            phase=WorkflowConfig.Phase.APPLICATION,
            batch=self.batch,
            version=4,
            is_active=True,
        )
        review_node = WorkflowNode.objects.create(
            workflow=workflow,
            code="CUSTOM_COLLEGE_REVIEW",
            name="自定义学院审核",
            node_type=WorkflowNode.NodeType.APPROVAL,
            role_fk=custom_role,
            sort_order=1,
        )
        own_project = Project.objects.create(
            project_no="RV20260007",
            title="Own College Project",
            leader=self.student,
            status=Project.ProjectStatus.COLLEGE_AUDITING,
            year=self.batch.year,
            batch=self.batch,
        )
        other_project = Project.objects.create(
            project_no="RV20260008",
            title="Other College Project",
            leader=other_student,
            status=Project.ProjectStatus.COLLEGE_AUDITING,
            year=self.batch.year,
            batch=self.batch,
        )
        for project in (own_project, other_project):
            phase_instance = ProjectPhaseInstance.objects.create(
                project=project,
                phase=ProjectPhaseInstance.Phase.APPLICATION,
                attempt_no=1,
                step=review_node.code,
                current_node_id=review_node.id,
                state=ProjectPhaseInstance.State.IN_PROGRESS,
                created_by=project.leader,
            )
            Review.objects.create(
                project=project,
                phase_instance=phase_instance,
                workflow_node=review_node,
                review_type=Review.ReviewType.APPLICATION,
                status=Review.ReviewStatus.PENDING,
            )
        self.client.force_authenticate(user=custom_admin)

        response = self.client.get("/api/v1/reviews/")

        self.assertEqual(response.status_code, 200)
        project_ids = {item["project"] for item in response.data["results"]}
        self.assertIn(own_project.id, project_ids)
        self.assertNotIn(other_project.id, project_ids)

    def test_reject_targets_returns_role_code(self):
        student_role = Role.objects.get(code="STUDENT")
        project = Project.objects.create(
            project_no="RV20260006",
            title="Reject Target Project",
            leader=self.student,
            status=Project.ProjectStatus.COLLEGE_AUDITING,
            year=self.batch.year,
            batch=self.batch,
        )
        workflow = WorkflowConfig.objects.create(
            name="Reject Target Workflow",
            phase=WorkflowConfig.Phase.APPLICATION,
            batch=self.batch,
            version=3,
            is_active=True,
        )
        submit_node = WorkflowNode.objects.create(
            workflow=workflow,
            code="SUBMIT",
            name="学生提交",
            node_type=WorkflowNode.NodeType.SUBMIT,
            role_fk=student_role,
            sort_order=1,
        )
        review_node = WorkflowNode.objects.create(
            workflow=workflow,
            code="COLLEGE_REVIEW",
            name="学院审核",
            node_type=WorkflowNode.NodeType.APPROVAL,
            role_fk=self.admin.role_fk,
            sort_order=2,
            allowed_reject_to=submit_node.id,
        )
        phase_instance = ProjectPhaseInstance.objects.create(
            project=project,
            phase=ProjectPhaseInstance.Phase.APPLICATION,
            attempt_no=1,
            step=review_node.code,
            current_node_id=review_node.id,
            state=ProjectPhaseInstance.State.IN_PROGRESS,
            created_by=self.student,
        )
        review = Review.objects.create(
            project=project,
            phase_instance=phase_instance,
            workflow_node=review_node,
            review_type=Review.ReviewType.APPLICATION,
            status=Review.ReviewStatus.PENDING,
        )

        response = self.client.get(f"/api/v1/reviews/{review.id}/reject-targets/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"][0]["id"], submit_node.id)
        self.assertEqual(response.data["data"][0]["role"], "STUDENT")

    def test_pending_counts_scopes_change_requests_to_current_batch(self):
        archived_batch = ProjectBatch.objects.create(
            name="2025",
            year=2025,
            code="RV2025",
            status=ProjectBatch.STATUS_ARCHIVED,
            is_active=True,
            is_current=False,
        )
        current_project = Project.objects.create(
            project_no="RV20260001",
            title="Current Change Project",
            leader=self.student,
            status=Project.ProjectStatus.IN_PROGRESS,
            year=2026,
            batch=self.batch,
        )
        archived_project = Project.objects.create(
            project_no="RV20250001",
            title="Archived Change Project",
            leader=self.student,
            status=Project.ProjectStatus.IN_PROGRESS,
            year=2025,
            batch=archived_batch,
        )
        ProjectChangeRequest.objects.create(
            project=current_project,
            request_type=ProjectChangeRequest.ChangeType.CHANGE,
            status=ProjectChangeRequest.ChangeStatus.LEVEL2_REVIEWING,
            reason="current",
            created_by=self.student,
        )
        ProjectChangeRequest.objects.create(
            project=archived_project,
            request_type=ProjectChangeRequest.ChangeType.CHANGE,
            status=ProjectChangeRequest.ChangeStatus.LEVEL2_REVIEWING,
            reason="archived",
            created_by=self.student,
        )

        response = self.client.get("/api/v1/reviews/statistics/pending-counts/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"]["change"], 1)

    def test_pending_counts_uses_custom_school_scope_for_change_requests(self):
        custom_school_role, _ = Role.objects.get_or_create(
            code="SCHOOL_REVIEW_STATS",
            defaults={"name": "校级审核统计员", "scope_dimension": "SCHOOL"},
        )
        custom_school_role.scope_dimension = "SCHOOL"
        custom_school_role.is_active = True
        custom_school_role.save(update_fields=["scope_dimension", "is_active"])
        custom_school_admin = User.objects.create_user(
            username="custom_school_review_stats",
            password="password123",
            role_fk=custom_school_role,
            real_name="校级审核统计员",
            employee_id="RS20001",
        )
        current_project = Project.objects.create(
            project_no="RV20260007",
            title="Custom School Change Project",
            leader=self.student,
            status=Project.ProjectStatus.IN_PROGRESS,
            year=2026,
            batch=self.batch,
        )
        ProjectChangeRequest.objects.create(
            project=current_project,
            request_type=ProjectChangeRequest.ChangeType.CHANGE,
            status=ProjectChangeRequest.ChangeStatus.LEVEL1_REVIEWING,
            reason="school",
            created_by=self.student,
        )
        ProjectChangeRequest.objects.create(
            project=current_project,
            request_type=ProjectChangeRequest.ChangeType.CHANGE,
            status=ProjectChangeRequest.ChangeStatus.LEVEL2_REVIEWING,
            reason="college",
            created_by=self.student,
        )
        self.client.force_authenticate(user=custom_school_admin)

        response = self.client.get("/api/v1/reviews/statistics/pending-counts/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"]["change"], 1)

    def test_pending_counts_uses_legacy_level1_scope_for_change_requests(self):
        self.level1_admin.role_fk.scope_dimension = None
        self.level1_admin.role_fk.save(update_fields=["scope_dimension"])
        self.level1_admin.refresh_from_db()
        current_project = Project.objects.create(
            project_no="RV20260008",
            title="Legacy School Change Project",
            leader=self.student,
            status=Project.ProjectStatus.IN_PROGRESS,
            year=2026,
            batch=self.batch,
        )
        ProjectChangeRequest.objects.create(
            project=current_project,
            request_type=ProjectChangeRequest.ChangeType.CHANGE,
            status=ProjectChangeRequest.ChangeStatus.LEVEL1_REVIEWING,
            reason="legacy school",
            created_by=self.student,
        )
        ProjectChangeRequest.objects.create(
            project=current_project,
            request_type=ProjectChangeRequest.ChangeType.CHANGE,
            status=ProjectChangeRequest.ChangeStatus.LEVEL2_REVIEWING,
            reason="legacy college",
            created_by=self.student,
        )
        self.client.force_authenticate(user=self.level1_admin)

        response = self.client.get("/api/v1/reviews/statistics/pending-counts/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"]["change"], 1)

    def test_score_details_reject_non_finite_weight(self):
        with self.assertRaisesMessage(ValueError, "评分明细权重格式错误"):
            ReviewService._normalize_score_details(
                None,
                None,
                [{"title": "创新性", "score": 80, "weight": "Infinity"}],
            )

    def test_review_min_comment_setting_tolerates_invalid_value(self):
        self.assertEqual(non_negative_int("invalid"), 0)
        self.assertEqual(non_negative_int("-5"), 0)
        self.assertEqual(non_negative_int("12"), 12)

    def test_parse_approved_budget_accepts_decimal_value(self):
        self.assertEqual(_parse_approved_budget("1200.50"), Decimal("1200.50"))

    def test_parse_approved_budget_rejects_missing_value(self):
        with self.assertRaisesMessage(ValueError, "请填写批准经费"):
            _parse_approved_budget("")

    def test_parse_approved_budget_rejects_non_finite_value(self):
        for value in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(value=value):
                with self.assertRaisesMessage(ValueError, "批准经费格式不正确"):
                    _parse_approved_budget(value)

    def test_parse_approved_budget_rejects_negative_value(self):
        with self.assertRaisesMessage(ValueError, "批准经费不能为负数"):
            _parse_approved_budget("-1")
