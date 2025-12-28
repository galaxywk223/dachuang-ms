"""
Project archive helpers.
"""

from typing import Iterable, List, Optional

from ..models import ProjectArchive
from ..serializers import ProjectSerializer


ARCHIVE_ATTACHMENT_FIELDS = (
    "proposal_file",
    "attachment_file",
    "contract_file",
    "task_book_file",
    "mid_term_report",
    "final_report",
    "achievement_file",
)


def build_archive_snapshot(project, request=None):
    return ProjectSerializer(project, context={"request": request}).data


def build_archive_attachments(project):
    attachments = []
    for field in ARCHIVE_ATTACHMENT_FIELDS:
        file_obj = getattr(project, field, None)
        if file_obj:
            attachments.append({"field": field, "name": file_obj.name})
    return attachments


def ensure_project_archive(project, request=None) -> Optional[ProjectArchive]:
    if hasattr(project, "archive"):
        return None
    snapshot = build_archive_snapshot(project, request=request)
    attachments = build_archive_attachments(project)
    return ProjectArchive.objects.create(
        project=project,
        snapshot=snapshot,
        attachments=attachments,
    )


def archive_projects(projects: Iterable, request=None) -> List[ProjectArchive]:
    created = []
    for project in projects:
        archive = ensure_project_archive(project, request=request)
        if archive:
            created.append(archive)
    return created
