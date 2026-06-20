from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.crypto import get_random_string

from apps.projects.models import Project, ProjectPhaseInstance
from apps.projects.services.phase_service import ProjectPhaseService
from apps.system_settings.models import ProjectBatch
from apps.users.models import Role


User = get_user_model()


class ProjectPhaseServiceTestCase(TestCase):
    def setUp(self):
        password = get_random_string(12)
        student_role = Role.objects.get(code="STUDENT")
        self.student = User.objects.create_user(
            username="phase-student",
            password=password,
            role_fk=student_role,
            real_name="Phase Student",
            employee_id="P1001",
        )
        self.batch = ProjectBatch.objects.create(
            name="2026",
            year=2026,
            code="PHASE2026",
            status=ProjectBatch.STATUS_ACTIVE,
            is_active=True,
            is_current=True,
        )
        self.project = Project.objects.create(
            project_no="PHASE2026001",
            title="Phase Project",
            leader=self.student,
            status=Project.ProjectStatus.IN_PROGRESS,
            year=2026,
            batch=self.batch,
        )

    def test_ensure_current_reuses_in_progress_attempt(self):
        phase = ProjectPhaseService.ensure_current(
            self.project,
            ProjectPhaseInstance.Phase.MID_TERM,
            step="STUDENT_SUBMIT",
            created_by=self.student,
        )

        same_phase = ProjectPhaseService.ensure_current(
            self.project,
            ProjectPhaseInstance.Phase.MID_TERM,
            step="TEACHER_REVIEW",
            created_by=self.student,
        )

        phase.refresh_from_db()
        self.assertEqual(same_phase.id, phase.id)
        self.assertEqual(phase.attempt_no, 1)
        self.assertEqual(phase.step, "TEACHER_REVIEW")
        self.assertEqual(phase.state, ProjectPhaseInstance.State.IN_PROGRESS)

    def test_ensure_current_starts_new_attempt_after_returned_attempt(self):
        returned = ProjectPhaseInstance.objects.create(
            project=self.project,
            phase=ProjectPhaseInstance.Phase.MID_TERM,
            attempt_no=1,
            step="TEACHER_REVIEW",
            state=ProjectPhaseInstance.State.RETURNED,
            created_by=self.student,
        )

        current = ProjectPhaseService.ensure_current(
            self.project,
            ProjectPhaseInstance.Phase.MID_TERM,
            step="STUDENT_SUBMIT",
            created_by=self.student,
        )

        returned.refresh_from_db()
        self.assertNotEqual(current.id, returned.id)
        self.assertEqual(current.attempt_no, 2)
        self.assertEqual(current.state, ProjectPhaseInstance.State.IN_PROGRESS)
        self.assertEqual(returned.state, ProjectPhaseInstance.State.RETURNED)
        self.assertEqual(returned.step, "TEACHER_REVIEW")

    def test_ensure_current_starts_new_attempt_after_completed_attempt(self):
        completed = ProjectPhaseInstance.objects.create(
            project=self.project,
            phase=ProjectPhaseInstance.Phase.CLOSURE,
            attempt_no=1,
            step="COMPLETED",
            state=ProjectPhaseInstance.State.COMPLETED,
            created_by=self.student,
        )

        current = ProjectPhaseService.ensure_current(
            self.project,
            ProjectPhaseInstance.Phase.CLOSURE,
            step="STUDENT_SUBMIT",
            created_by=self.student,
        )

        completed.refresh_from_db()
        self.assertNotEqual(current.id, completed.id)
        self.assertEqual(current.attempt_no, 2)
        self.assertEqual(current.state, ProjectPhaseInstance.State.IN_PROGRESS)
        self.assertEqual(completed.state, ProjectPhaseInstance.State.COMPLETED)
        self.assertEqual(completed.step, "COMPLETED")
