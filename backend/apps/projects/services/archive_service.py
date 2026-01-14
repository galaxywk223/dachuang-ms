"""
Project archive helpers.
"""

from typing import Iterable, List, Optional
import os
import json
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from ..models import ProjectArchive, Project, ProjectAchievement, ProjectExpenditure
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


class ArchiveService:
    """
    归档服务类
    """

    @staticmethod
    def build_archive_snapshot(project, request=None):
        """构建项目快照数据"""
        return ProjectSerializer(project, context={"request": request}).data

    @staticmethod
    def build_archive_attachments(project):
        """构建附件清单"""
        attachments = []
        for field in ARCHIVE_ATTACHMENT_FIELDS:
            file_obj = getattr(project, field, None)
            if file_obj:
                attachments.append(
                    {
                        "field": field,
                        "name": file_obj.name,
                        "size": file_obj.size if hasattr(file_obj, "size") else 0,
                        "url": file_obj.url if file_obj else "",
                    }
                )

        # 添加成果附件
        achievements = ProjectAchievement.objects.filter(project=project)
        for achievement in achievements:
            if achievement.attachment:
                attachments.append(
                    {
                        "field": f"achievement_{achievement.id}",
                        "name": achievement.attachment.name,
                        "type": "achievement",
                        "achievement_type": achievement.achievement_type.label
                        if achievement.achievement_type
                        else "",
                    }
                )

        # 添加经费凭证
        expenditures = ProjectExpenditure.objects.filter(
            project=project, is_deleted=False
        )
        for expenditure in expenditures:
            if expenditure.proof_file:
                attachments.append(
                    {
                        "field": f"expenditure_{expenditure.id}",
                        "name": expenditure.proof_file.name,
                        "type": "proof",
                        "amount": str(expenditure.amount),
                    }
                )

        return attachments

    @staticmethod
    @transaction.atomic
    def archive_project(project, request=None, archived_by=None):
        """
        归档单个项目
        :param project: 项目实例
        :param request: 请求对象（可选）
        :param archived_by: 归档操作人（可选）
        :return: ProjectArchive实例
        """
        # 检查是否已归档
        if hasattr(project, "archive") and project.archive:
            raise ValueError(f"项目 {project.project_no} 已经归档")

        # 检查项目状态
        if project.status != Project.ProjectStatus.CLOSED:
            raise ValueError(
                f"只能归档已结题的项目（当前状态：{project.get_status_display()}）"
            )

        # 构建快照和附件清单
        snapshot = ArchiveService.build_archive_snapshot(project, request=request)
        attachments = ArchiveService.build_archive_attachments(project)

        # 添加额外统计信息
        archive_metadata = {
            "archived_at": timezone.now().isoformat(),
            "archived_by": archived_by.username if archived_by else "system",
            "project_status": project.status,
            "total_attachments": len(attachments),
            "achievement_count": ProjectAchievement.objects.filter(
                project=project
            ).count(),
            "expenditure_count": ProjectExpenditure.objects.filter(
                project=project, is_deleted=False
            ).count(),
            "total_budget": str(project.approved_budget or project.budget_amount or 0),
            "team_size": project.members.filter(is_deleted=False).count()
            + 1,  # +1 for leader
        }

        # 创建归档记录
        archive = ProjectArchive.objects.create(
            project=project,
            snapshot=snapshot,
            attachments=attachments,
            metadata=archive_metadata,
        )

        return archive

    @staticmethod
    def ensure_project_archive(project, request=None):
        """确保项目已归档，如果未归档则创建归档"""
        if hasattr(project, "archive") and project.archive:
            return None

        if project.status != Project.ProjectStatus.CLOSED:
            return None

        snapshot = ArchiveService.build_archive_snapshot(project, request=request)
        attachments = ArchiveService.build_archive_attachments(project)
        return ProjectArchive.objects.create(
            project=project,
            snapshot=snapshot,
            attachments=attachments,
        )

    @staticmethod
    def archive_projects(projects: Iterable, request=None):
        """批量归档项目"""
        created = []
        failed = []

        for project in projects:
            try:
                archive = ArchiveService.ensure_project_archive(
                    project, request=request
                )
                if archive:
                    created.append(archive)
            except Exception as e:
                failed.append(
                    {
                        "project_id": project.id,
                        "project_no": project.project_no,
                        "error": str(e),
                    }
                )

        return {
            "created": created,
            "failed": failed,
            "success_count": len(created),
            "failed_count": len(failed),
        }

    @staticmethod
    def export_archive_to_json(archive, output_path=None):
        """
        将归档数据导出为JSON文件
        :param archive: ProjectArchive实例
        :param output_path: 输出文件路径（可选）
        :return: 文件路径
        """
        if not output_path:
            output_dir = os.path.join(settings.MEDIA_ROOT, "archives", "exports")
            os.makedirs(output_dir, exist_ok=True)

            timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
            project_no = archive.project.project_no if archive.project else "unknown"
            filename = f"archive_{project_no}_{timestamp}.json"
            output_path = os.path.join(output_dir, filename)

        # 构建完整的归档数据
        archive_data = {
            "archive_id": archive.id,
            "archived_at": archive.archived_at.isoformat()
            if archive.archived_at
            else None,
            "project_snapshot": archive.snapshot,
            "attachments": archive.attachments,
            "metadata": archive.metadata,
        }

        # 写入文件
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(archive_data, f, ensure_ascii=False, indent=2)

        return output_path

    @staticmethod
    def restore_from_archive(archive):
        """
        从归档恢复项目数据（查询用途，不恢复到数据库）
        :param archive: ProjectArchive实例
        :return: 项目快照数据
        """
        return {
            "project": archive.snapshot,
            "attachments": archive.attachments,
            "metadata": archive.metadata,
            "archived_at": archive.archived_at,
        }


# 向后兼容的函数接口
def build_archive_snapshot(project, request=None):
    return ArchiveService.build_archive_snapshot(project, request)


def build_archive_attachments(project):
    return ArchiveService.build_archive_attachments(project)


def ensure_project_archive(project, request=None) -> Optional[ProjectArchive]:
    return ArchiveService.ensure_project_archive(project, request)


def archive_projects(projects: Iterable, request=None) -> List[ProjectArchive]:
    result = ArchiveService.archive_projects(projects, request)
    return result["created"]
