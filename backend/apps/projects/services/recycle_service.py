"""
Recycle bin helpers.
"""

from django.utils import timezone

from apps.projects.models import (
    Project,
    ProjectAchievement,
    ProjectExpenditure,
    ProjectProgress,
    ProjectRecycleBin,
)


class ProjectRecycleService:
    @staticmethod
    def add_item(
        *,
        project,
        resource_type,
        resource_id=None,
        payload=None,
        attachments=None,
        deleted_by=None,
    ):
        return ProjectRecycleBin.objects.create(
            project=project,
            resource_type=resource_type,
            resource_id=resource_id,
            payload=payload or {},
            attachments=attachments or [],
            deleted_by=deleted_by,
        )

    @staticmethod
    def restore_item(item: ProjectRecycleBin, user=None):
        if item.is_restored:
            return False, "已恢复"
        payload = item.payload or {}

        if item.resource_type == ProjectRecycleBin.ResourceType.ACHIEVEMENT:
            obj = ProjectAchievement.objects.create(
                project=item.project,
                achievement_type_id=payload.get("achievement_type"),
                title=payload.get("title", ""),
                description=payload.get("description", ""),
                authors=payload.get("authors", ""),
                journal=payload.get("journal", ""),
                publication_date=payload.get("publication_date") or None,
                doi=payload.get("doi", ""),
                patent_no=payload.get("patent_no", ""),
                patent_type=payload.get("patent_type", ""),
                applicant=payload.get("applicant", ""),
                copyright_no=payload.get("copyright_no", ""),
                copyright_owner=payload.get("copyright_owner", ""),
                competition_name=payload.get("competition_name", ""),
                award_level=payload.get("award_level", ""),
                award_date=payload.get("award_date") or None,
                extra_data=payload.get("extra_data") or {},
            )
            attachment = payload.get("attachment")
            if attachment:
                obj.attachment = attachment
                obj.save(update_fields=["attachment"])

        elif item.resource_type == ProjectRecycleBin.ResourceType.EXPENDITURE:
            ProjectExpenditure.objects.create(
                project=item.project,
                title=payload.get("title", ""),
                amount=payload.get("amount", 0),
                expenditure_date=payload.get("expenditure_date"),
                proof_file=payload.get("proof_file") or None,
                created_by_id=payload.get("created_by"),
            )

        elif item.resource_type == ProjectRecycleBin.ResourceType.PROGRESS:
            ProjectProgress.objects.create(
                project=item.project,
                title=payload.get("title", ""),
                content=payload.get("content", ""),
                attachment=payload.get("attachment") or None,
                created_by_id=payload.get("created_by"),
            )

        elif item.resource_type in [
            ProjectRecycleBin.ResourceType.MID_TERM,
            ProjectRecycleBin.ResourceType.CLOSURE,
            ProjectRecycleBin.ResourceType.APPLICATION,
        ]:
            project = item.project
            project.status = payload.get("status", project.status)
            project.submitted_at = payload.get("submitted_at")
            project.mid_term_submitted_at = payload.get("mid_term_submitted_at")
            project.closure_applied_at = payload.get("closure_applied_at")
            project.proposal_file = (
                payload.get("proposal_file") or project.proposal_file
            )
            project.attachment_file = (
                payload.get("attachment_file") or project.attachment_file
            )
            project.mid_term_report = (
                payload.get("mid_term_report") or project.mid_term_report
            )
            project.final_report = payload.get("final_report") or project.final_report
            project.achievement_file = (
                payload.get("achievement_file") or project.achievement_file
            )
            project.save()

        else:
            return False, "未知的资源类型"

        item.is_restored = True
        item.restored_by = user
        item.restored_at = timezone.now()
        item.save(update_fields=["is_restored", "restored_by", "restored_at"])
        return True, "恢复成功"

    @staticmethod
    def snapshot_application(project: Project):
        return {
            "status": project.status,
            "submitted_at": project.submitted_at,
            "proposal_file": project.proposal_file.name
            if project.proposal_file
            else "",
            "attachment_file": project.attachment_file.name
            if project.attachment_file
            else "",
        }

    @staticmethod
    def snapshot_midterm(project: Project):
        return {
            "status": project.status,
            "mid_term_submitted_at": project.mid_term_submitted_at,
            "mid_term_report": project.mid_term_report.name
            if project.mid_term_report
            else "",
        }

    @staticmethod
    def snapshot_closure(project: Project):
        return {
            "status": project.status,
            "closure_applied_at": project.closure_applied_at,
            "final_report": project.final_report.name if project.final_report else "",
            "achievement_file": project.achievement_file.name
            if project.achievement_file
            else "",
        }
