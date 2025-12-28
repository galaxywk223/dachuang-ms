from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from django.db import transaction
from django.utils import timezone

from apps.projects.models import Project, ProjectPhaseInstance
from apps.system_settings.services import WorkflowService


@dataclass(frozen=True)
class PhaseContext:
    phase: str
    initial_step: str


PHASE_CONTEXTS: dict[str, PhaseContext] = {
    ProjectPhaseInstance.Phase.APPLICATION: PhaseContext(
        phase=ProjectPhaseInstance.Phase.APPLICATION,
        initial_step="TEACHER_REVIEW",
    ),
    ProjectPhaseInstance.Phase.MID_TERM: PhaseContext(
        phase=ProjectPhaseInstance.Phase.MID_TERM,
        initial_step="TEACHER_REVIEW",
    ),
    ProjectPhaseInstance.Phase.CLOSURE: PhaseContext(
        phase=ProjectPhaseInstance.Phase.CLOSURE,
        initial_step="TEACHER_REVIEW",
    ),
}


class ProjectPhaseService:
    @staticmethod
    def _get_context(phase: str) -> PhaseContext:
        if phase not in PHASE_CONTEXTS:
            raise ValueError(f"Unsupported phase: {phase}")
        return PHASE_CONTEXTS[phase]

    @staticmethod
    def get_current(project: Project, phase: str) -> Optional[ProjectPhaseInstance]:
        return (
            ProjectPhaseInstance.objects.filter(project=project, phase=phase)
            .order_by("-attempt_no", "-id")
            .first()
        )

    @staticmethod
    @transaction.atomic
    def ensure_current(
        project: Project,
        phase: str,
        *,
        created_by=None,
        step: Optional[str] = None,
    ) -> ProjectPhaseInstance:
        context = ProjectPhaseService._get_context(phase)
        if step is None:
            initial_node = WorkflowService.get_initial_node(phase, project.batch)
            if initial_node:
                step = initial_node.code
        current = ProjectPhaseService.get_current(project, phase)
        if current:
            if step and current.step != step:
                current.step = step
                current.save(update_fields=["step", "updated_at"])
            return current

        return ProjectPhaseInstance.objects.create(
            project=project,
            phase=context.phase,
            attempt_no=1,
            step=step or context.initial_step,
            state=ProjectPhaseInstance.State.IN_PROGRESS,
            created_by=created_by,
        )

    @staticmethod
    @transaction.atomic
    def start_new_attempt(
        project: Project,
        phase: str,
        *,
        created_by=None,
        step: Optional[str] = None,
    ) -> ProjectPhaseInstance:
        context = ProjectPhaseService._get_context(phase)
        if step is None:
            initial_node = WorkflowService.get_initial_node(phase, project.batch)
            if initial_node:
                step = initial_node.code
        current = ProjectPhaseService.get_current(project, phase)
        next_attempt = 1 if not current else int(current.attempt_no) + 1
        return ProjectPhaseInstance.objects.create(
            project=project,
            phase=context.phase,
            attempt_no=next_attempt,
            step=step or context.initial_step,
            state=ProjectPhaseInstance.State.IN_PROGRESS,
            created_by=created_by,
        )

    @staticmethod
    @transaction.atomic
    def mark_returned(
        instance: ProjectPhaseInstance,
        *,
        return_to: str = ProjectPhaseInstance.ReturnTo.STUDENT,
        reason: str = "",
    ) -> ProjectPhaseInstance:
        instance.state = ProjectPhaseInstance.State.RETURNED
        instance.return_to = return_to
        instance.returned_reason = reason or ""
        instance.returned_at = timezone.now()
        instance.save(
            update_fields=[
                "state",
                "return_to",
                "returned_reason",
                "returned_at",
                "updated_at",
            ]
        )
        return instance

    @staticmethod
    @transaction.atomic
    def mark_completed(instance: ProjectPhaseInstance, *, step: Optional[str] = None) -> ProjectPhaseInstance:
        instance.state = ProjectPhaseInstance.State.COMPLETED
        if step is not None:
            instance.step = step
        instance.save(update_fields=["state", "step", "updated_at"])
        return instance
