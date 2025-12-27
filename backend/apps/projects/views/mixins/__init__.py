"""View mixins for project management."""

from .project_achievements_mixin import ProjectAchievementsMixin
from .project_closure_mixin import ProjectClosureMixin
from .project_core_actions_mixin import ProjectCoreActionsMixin
from .project_level2_export_mixin import ProjectLevel2ExportMixin
from .project_members_mixin import ProjectMembersMixin
from .project_midterm_mixin import ProjectMidtermMixin
from .project_progress_mixin import ProjectProgressMixin
from .project_ranking_mixin import ProjectRankingMixin
from .project_self_mixin import ProjectSelfMixin
from .project_workflow_mixin import ProjectWorkflowMixin

__all__ = [
    "ProjectAchievementsMixin",
    "ProjectClosureMixin",
    "ProjectCoreActionsMixin",
    "ProjectLevel2ExportMixin",
    "ProjectMembersMixin",
    "ProjectMidtermMixin",
    "ProjectProgressMixin",
    "ProjectRankingMixin",
    "ProjectSelfMixin",
    "ProjectWorkflowMixin",
]
