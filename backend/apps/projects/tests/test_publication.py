from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.dictionaries.models import DictionaryItem, DictionaryType
from apps.notifications.models import Notification, PlatformNotice
from apps.operations.models import OperationLog
from apps.projects.models import Project
from apps.projects.services import PublicationService
from apps.system_settings.models import ProjectBatch
from apps.users.models import Role


User = get_user_model()


class PublicationServiceTestCase(TestCase):
    def setUp(self):
        self.student_role = self._role("STUDENT", "学生")
        self.level2_role = self._role("LEVEL2_ADMIN", "院级管理员", "COLLEGE")
        self.level1_role = self._role("LEVEL1_ADMIN", "校级管理员", "SCHOOL")
        self.custom_school_role = self._role("SCHOOL_PUBLISHER", "校级发布员", "SCHOOL")

        self.student = User.objects.create_user(
            username="student_pub",
            password="123456",
            role_fk=self.student_role,
            real_name="学生发布测试",
            employee_id="PUB1001",
            college="计算机学院",
        )
        self.level2_admin = User.objects.create_user(
            username="level2_pub",
            password="123456",
            role_fk=self.level2_role,
            real_name="院级发布管理员",
            employee_id="PUB2001",
            college="计算机学院",
        )
        self.level1_admin = User.objects.create_user(
            username="level1_pub",
            password="123456",
            role_fk=self.level1_role,
            real_name="校级发布管理员",
            employee_id="PUB3001",
            college="教务处",
        )
        self.custom_school_admin = User.objects.create_user(
            username="custom_school_pub",
            password="123456",
            role_fk=self.custom_school_role,
            real_name="校级发布员",
            employee_id="PUB3002",
            college="教务处",
        )

        self.batch = ProjectBatch.objects.create(
            name="2026 年大创",
            year=2026,
            code="PUB2026",
            status=ProjectBatch.STATUS_ACTIVE,
            is_active=True,
            is_current=True,
        )
        level_type, _ = DictionaryType.objects.get_or_create(
            code="project_level",
            defaults={
                "name": "项目级别",
                "is_system": True,
                "is_active": True,
            },
        )
        level_type.name = "项目级别"
        level_type.is_system = True
        level_type.is_active = True
        level_type.save(update_fields=["name", "is_system", "is_active"])
        self.school_level, _ = DictionaryItem.objects.get_or_create(
            dict_type=level_type,
            value="SCHOOL",
            defaults={
                "label": "校级",
                "sort_order": 1,
            },
        )
        self.school_level.label = "校级"
        self.school_level.sort_order = 1
        self.school_level.save(update_fields=["label", "sort_order"])
        self.project = Project.objects.create(
            title="发布流程测试项目",
            leader=self.student,
            status=Project.ProjectStatus.LEVEL1_AUDITING,
            year=2026,
            batch=self.batch,
            budget=Decimal("3000.00"),
        )

    def _role(self, code, name, scope_dimension=None):
        role, _ = Role.objects.get_or_create(code=code, defaults={"name": name})
        role.name = name
        role.scope_dimension = scope_dimension
        role.is_active = True
        role.save(update_fields=["name", "scope_dimension", "is_active"])
        return role

    def test_recommend_confirm_and_publish_establishment_result(self):
        updated = PublicationService.save_recommendations(
            self.level2_admin,
            [
                {
                    "project_id": self.project.id,
                    "recommendation_rank": 1,
                    "recommended_level": "SCHOOL",
                    "recommended_budget": "2500.00",
                    "recommendation_comment": "学院推荐立项",
                }
            ],
        )

        self.assertEqual(updated, 1)
        self.project.refresh_from_db()
        self.assertEqual(self.project.publish_status, Project.PublishStatus.RECOMMENDED)
        self.assertEqual(self.project.recommendation_rank, 1)
        self.assertEqual(self.project.recommended_level, self.school_level)
        self.assertEqual(self.project.recommended_budget, Decimal("2500.00"))

        confirmed = PublicationService.confirm_projects(
            self.level1_admin,
            [
                {
                    "project_id": self.project.id,
                    "final_level": "SCHOOL",
                    "final_budget": "2800.00",
                }
            ],
        )

        self.assertEqual(confirmed, 1)
        self.project.refresh_from_db()
        self.assertEqual(self.project.publish_status, Project.PublishStatus.CONFIRMED)
        self.assertEqual(self.project.final_level, self.school_level)
        self.assertEqual(self.project.approved_budget, Decimal("2800.00"))

        published = PublicationService.publish_projects(
            self.level1_admin, [self.project.id]
        )

        self.assertEqual(published, 1)
        self.project.refresh_from_db()
        self.assertEqual(self.project.publish_status, Project.PublishStatus.PUBLISHED)
        self.assertEqual(self.project.status, Project.ProjectStatus.IN_PROGRESS)
        self.assertEqual(self.project.published_by, self.level1_admin)
        self.assertIsNotNone(self.project.published_at)
        self.assertTrue(self.project.project_no.startswith("2026"))
        self.assertTrue(
            Notification.objects.filter(
                recipient=self.student,
                related_project=self.project,
                title="立项结果已发布",
            ).exists()
        )
        notice = PlatformNotice.objects.get(title="2026 年大创立项结果公示")
        self.assertEqual(notice.status, PlatformNotice.NoticeStatus.PUBLISHED)
        self.assertTrue(notice.is_pinned)
        self.assertEqual(
            notice.target_roles, ["STUDENT", "LEVEL2_ADMIN", "TEACHER"]
        )
        self.assertEqual(notice.created_by, self.level1_admin)
        self.assertIsNotNone(notice.published_at)
        self.assertIn("立项结果已发布", notice.content)
        self.assertTrue(
            OperationLog.objects.filter(
                module="立项发布",
                action="发布立项结果",
            ).exists()
        )

    def test_level2_admin_cannot_confirm_publication_result(self):
        with self.assertRaises(PermissionError):
            PublicationService.confirm_projects(
                self.level2_admin,
                [{"project_id": self.project.id, "final_budget": "2800.00"}],
            )

    def test_custom_school_admin_can_confirm_and_publish_publication_result(self):
        self.project.publish_status = Project.PublishStatus.RECOMMENDED
        self.project.recommended_level = self.school_level
        self.project.recommended_budget = Decimal("2500.00")
        self.project.save(
            update_fields=[
                "publish_status",
                "recommended_level",
                "recommended_budget",
            ]
        )

        confirmed = PublicationService.confirm_projects(
            self.custom_school_admin,
            [{"project_id": self.project.id, "final_budget": "2800.00"}],
        )
        published = PublicationService.publish_projects(
            self.custom_school_admin, [self.project.id]
        )

        self.assertEqual(confirmed, 1)
        self.assertEqual(published, 1)
        self.project.refresh_from_db()
        self.assertEqual(self.project.publish_status, Project.PublishStatus.PUBLISHED)
        self.assertEqual(self.project.status, Project.ProjectStatus.IN_PROGRESS)
        self.assertEqual(self.project.published_by, self.custom_school_admin)

    def test_legacy_level1_admin_without_scope_can_confirm_and_publish_publication_result(self):
        self.level1_role.scope_dimension = None
        self.level1_role.save(update_fields=["scope_dimension"])
        self.level1_admin.refresh_from_db()
        self.project.publish_status = Project.PublishStatus.RECOMMENDED
        self.project.recommended_level = self.school_level
        self.project.recommended_budget = Decimal("2500.00")
        self.project.save(
            update_fields=[
                "publish_status",
                "recommended_level",
                "recommended_budget",
            ]
        )

        confirmed = PublicationService.confirm_projects(
            self.level1_admin,
            [{"project_id": self.project.id, "final_budget": "2800.00"}],
        )
        published = PublicationService.publish_projects(
            self.level1_admin, [self.project.id]
        )

        self.assertEqual(confirmed, 1)
        self.assertEqual(published, 1)
        self.project.refresh_from_db()
        self.assertEqual(self.project.publish_status, Project.PublishStatus.PUBLISHED)
        self.assertEqual(self.project.status, Project.ProjectStatus.IN_PROGRESS)
        self.assertEqual(self.project.published_by, self.level1_admin)

    def test_publish_publication_updates_existing_notice_without_duplicates(self):
        self.project.publish_status = Project.PublishStatus.CONFIRMED
        self.project.save(update_fields=["publish_status"])

        first = PublicationService.publish_projects(self.level1_admin, [self.project.id])
        second = PublicationService.publish_projects(self.level1_admin, [self.project.id])

        self.assertEqual(first, 1)
        self.assertEqual(second, 1)
        notices = PlatformNotice.objects.filter(title="2026 年大创立项结果公示")
        self.assertEqual(notices.count(), 1)
        notice = notices.get()
        self.assertEqual(notice.status, PlatformNotice.NoticeStatus.PUBLISHED)
        self.assertTrue(notice.is_pinned)
        self.assertEqual(
            Notification.objects.filter(
                recipient=self.student,
                related_project=self.project,
                title="立项结果已发布",
            ).count(),
            1,
        )

    def test_publish_publication_does_not_create_notice_when_no_project_updated(self):
        self.project.publish_status = Project.PublishStatus.NOT_READY
        self.project.save(update_fields=["publish_status"])

        published = PublicationService.publish_projects(self.level1_admin, [self.project.id])

        self.assertEqual(published, 0)
        self.assertFalse(PlatformNotice.objects.exists())

    def test_recommendations_update_published_projects_without_status_regression(self):
        self.project.publish_status = Project.PublishStatus.PUBLISHED
        self.project.recommendation_rank = 1
        self.project.recommended_budget = Decimal("2500.00")
        self.project.save(
            update_fields=[
                "publish_status",
                "recommendation_rank",
                "recommended_budget",
            ]
        )

        updated = PublicationService.save_recommendations(
            self.level2_admin,
            [
                {
                    "project_id": self.project.id,
                    "recommendation_rank": 9,
                    "recommended_level": "SCHOOL",
                    "recommended_budget": "9999.00",
                    "recommendation_comment": "更新发布后排序",
                }
            ],
        )

        self.assertEqual(updated, 1)
        self.project.refresh_from_db()
        self.assertEqual(self.project.publish_status, Project.PublishStatus.PUBLISHED)
        self.assertEqual(self.project.recommendation_rank, 9)
        self.assertEqual(self.project.recommended_level, self.school_level)
        self.assertEqual(self.project.recommended_budget, Decimal("9999.00"))
        self.assertEqual(self.project.recommendation_comment, "更新发布后排序")

    def test_confirm_projects_ignores_published_projects(self):
        self.project.publish_status = Project.PublishStatus.PUBLISHED
        self.project.final_budget = Decimal("2800.00")
        self.project.approved_budget = Decimal("2800.00")
        self.project.save(
            update_fields=["publish_status", "final_budget", "approved_budget"]
        )

        updated = PublicationService.confirm_projects(
            self.level1_admin,
            [{"project_id": self.project.id, "final_budget": "9999.00"}],
        )

        self.assertEqual(updated, 0)
        self.project.refresh_from_db()
        self.assertEqual(self.project.final_budget, Decimal("2800.00"))
        self.assertEqual(self.project.approved_budget, Decimal("2800.00"))

    def test_recommendations_reject_invalid_project_id(self):
        with self.assertRaisesMessage(ValueError, "项目ID不合法"):
            PublicationService.save_recommendations(
                self.level2_admin,
                [{"project_id": "invalid", "recommendation_rank": 1}],
            )

    def test_publication_items_reject_non_object_entries(self):
        with self.assertRaisesMessage(ValueError, "项目条目格式错误"):
            PublicationService.save_recommendations(
                self.level2_admin,
                ["invalid"],
            )

        with self.assertRaisesMessage(ValueError, "项目条目格式错误"):
            PublicationService.confirm_projects(
                self.level1_admin,
                [self.project.id],
            )

    def test_publication_budget_rejects_non_finite_value(self):
        with self.assertRaisesMessage(ValueError, "推荐经费格式不正确"):
            PublicationService._decimal("NaN", "推荐经费")

        with self.assertRaisesMessage(ValueError, "最终经费格式不正确"):
            PublicationService._decimal("Infinity", "最终经费")

    def test_confirm_projects_rejects_unknown_final_level(self):
        self.project.publish_status = Project.PublishStatus.RECOMMENDED
        self.project.save(update_fields=["publish_status"])

        with self.assertRaisesMessage(ValueError, "最终级别不存在"):
            PublicationService.confirm_projects(
                self.level1_admin,
                [{"project_id": self.project.id, "final_level": "UNKNOWN_LEVEL"}],
        )

        self.project.refresh_from_db()
        self.assertEqual(self.project.publish_status, Project.PublishStatus.RECOMMENDED)
        self.assertIsNone(self.project.final_level)

    def test_recommendations_reject_invalid_rank(self):
        with self.assertRaisesMessage(ValueError, "推荐排序必须为正整数"):
            PublicationService.save_recommendations(
                self.level2_admin,
                [
                    {
                        "project_id": self.project.id,
                        "recommendation_rank": "invalid",
                    }
                ],
            )
