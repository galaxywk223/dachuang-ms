from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from apps.dictionaries.models import DictionaryItem
from apps.notifications.models import PlatformNotice
from apps.notifications.services import NotificationService
from apps.operations.services import OperationLogService
from apps.system_settings.services import SystemSettingService
from apps.utils.pagination import optional_positive_int

from ..models import Project
from .project_service import ProjectService


class PublicationService:
    """
    立项结果发布服务。
    """

    ELIGIBLE_STATUSES = {
        Project.ProjectStatus.LEVEL1_AUDITING,
        Project.ProjectStatus.IN_PROGRESS,
    }

    @staticmethod
    def _has_school_admin_scope(user):
        return user.is_school_admin or user.is_level1_admin

    @staticmethod
    def get_scope_queryset(user):
        current_batch = SystemSettingService.get_current_batch()
        if not current_batch:
            return Project.objects.none()

        queryset = Project.objects.filter(batch=current_batch, is_deleted=False)
        if PublicationService._has_school_admin_scope(user):
            return queryset
        if user.is_admin:
            return queryset.filter(leader__college=user.college)
        return Project.objects.none()

    @staticmethod
    def get_publication_queryset(user):
        queryset = PublicationService.get_scope_queryset(user)
        return queryset.filter(
            Q(status__in=PublicationService.ELIGIBLE_STATUSES)
            | ~Q(publish_status=Project.PublishStatus.NOT_READY)
        ).select_related(
            "leader",
            "level",
            "recommended_level",
            "final_level",
            "published_by",
        )

    @staticmethod
    def _resolve_level(value):
        if value in (None, ""):
            return None
        queryset = DictionaryItem.objects.filter(dict_type__code="project_level")
        if isinstance(value, int) or (isinstance(value, str) and value.isdigit()):
            item = queryset.filter(id=int(value)).first()
            if item:
                return item
        return queryset.filter(value=str(value)).first()

    @staticmethod
    def _decimal(value, field_name):
        if value in (None, ""):
            return None
        try:
            amount = Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise ValueError(f"{field_name}格式不正确") from exc
        if not amount.is_finite():
            raise ValueError(f"{field_name}格式不正确")
        if amount < 0:
            raise ValueError(f"{field_name}不能为负数")
        return amount

    @staticmethod
    def _project_id(value):
        project_id = optional_positive_int(value)
        if project_id is None:
            raise ValueError("项目ID不合法")
        return project_id

    @staticmethod
    def _rank(value):
        if value in (None, ""):
            return None
        rank = optional_positive_int(value)
        if rank is None:
            raise ValueError("推荐排序必须为正整数")
        return rank

    @staticmethod
    def _item(value):
        if not isinstance(value, dict):
            raise ValueError("项目条目格式错误")
        return value

    @staticmethod
    def _sync_publication_notice(user, published_at):
        current_batch = SystemSettingService.get_current_batch()
        if not current_batch:
            return None

        batch_label = current_batch.name or f"{current_batch.year} 年大创项目"
        title = f"{batch_label}立项结果公示"
        content = (
            f"{batch_label}立项结果已发布。"
            "相关师生可登录系统查看项目立项结果、公示信息和后续安排。"
        )
        notice, _ = PlatformNotice.objects.update_or_create(
            title=title,
            defaults={
                "content": content,
                "target_roles": ["STUDENT", "LEVEL2_ADMIN", "TEACHER"],
                "status": PlatformNotice.NoticeStatus.PUBLISHED,
                "is_pinned": True,
                "published_at": published_at,
                "created_by": user,
            },
        )
        return notice

    @staticmethod
    @transaction.atomic
    def save_recommendations(user, items):
        queryset = PublicationService.get_publication_queryset(user)
        updated = 0
        for raw_item in items:
            item = PublicationService._item(raw_item)
            project_id = item.get("project_id") or item.get("id")
            if not project_id:
                continue
            project = queryset.filter(
                id=PublicationService._project_id(project_id)
            ).first()
            if not project:
                continue

            level = PublicationService._resolve_level(item.get("recommended_level"))
            if item.get("recommended_level") not in (None, "") and not level:
                raise ValueError("推荐级别不存在")

            rank = item.get("recommendation_rank")
            project.recommendation_rank = PublicationService._rank(rank)
            project.recommended_level = level
            project.recommended_budget = PublicationService._decimal(
                item.get("recommended_budget"), "推荐经费"
            )
            project.recommendation_comment = item.get("recommendation_comment", "")
            if project.publish_status == Project.PublishStatus.NOT_READY:
                project.publish_status = Project.PublishStatus.RECOMMENDED
            project.save(
                update_fields=[
                    "recommendation_rank",
                    "recommended_level",
                    "recommended_budget",
                    "recommendation_comment",
                    "publish_status",
                    "updated_at",
                ]
            )
            updated += 1
        OperationLogService.log(
            operator=user,
            module="立项发布",
            action="保存学院推荐",
            target_type="Project",
            detail={"updated": updated},
        )
        return updated

    @staticmethod
    @transaction.atomic
    def confirm_projects(user, items):
        if not PublicationService._has_school_admin_scope(user):
            raise PermissionError("只有校级管理员可以确认立项结果")

        queryset = PublicationService.get_scope_queryset(user).filter(
            publish_status__in=[
                Project.PublishStatus.RECOMMENDED,
                Project.PublishStatus.CONFIRMED,
            ]
        )
        updated = 0
        for raw_item in items:
            item = PublicationService._item(raw_item)
            project_id = item.get("project_id") or item.get("id")
            if not project_id:
                continue
            project = queryset.filter(
                id=PublicationService._project_id(project_id)
            ).first()
            if not project:
                continue

            level_value = item.get("final_level") or item.get("recommended_level")
            final_level = PublicationService._resolve_level(level_value)
            if level_value not in (None, "") and not final_level:
                raise ValueError("最终级别不存在")
            if not final_level:
                final_level = project.recommended_level or project.level
            final_budget = PublicationService._decimal(
                item.get("final_budget")
                if item.get("final_budget") not in (None, "")
                else item.get("recommended_budget"),
                "最终经费",
            )
            if final_budget is None:
                final_budget = project.recommended_budget or project.approved_budget

            project.final_level = final_level
            project.final_budget = final_budget
            if final_level:
                project.level = final_level
            if final_budget is not None:
                project.approved_budget = final_budget
            project.publish_status = Project.PublishStatus.CONFIRMED
            project.save(
                update_fields=[
                    "final_level",
                    "final_budget",
                    "level",
                    "approved_budget",
                    "publish_status",
                    "updated_at",
                ]
            )
            updated += 1
        OperationLogService.log(
            operator=user,
            module="立项发布",
            action="确认立项结果",
            target_type="Project",
            detail={"updated": updated},
        )
        return updated

    @staticmethod
    @transaction.atomic
    def publish_projects(user, project_ids):
        if not PublicationService._has_school_admin_scope(user):
            raise PermissionError("只有校级管理员可以发布立项结果")

        queryset = PublicationService.get_scope_queryset(user)
        projects = queryset.filter(
            id__in=project_ids,
            publish_status__in=[
                Project.PublishStatus.CONFIRMED,
                Project.PublishStatus.PUBLISHED,
            ],
        ).select_related("leader", "final_level")
        published = 0
        now = timezone.now()

        for project in projects:
            was_published = project.publish_status == Project.PublishStatus.PUBLISHED
            if not project.project_no:
                project.project_no = ProjectService.generate_project_no(
                    project.year, project.leader.college if project.leader else ""
                )
            if project.final_level:
                project.level = project.final_level
            if project.final_budget is not None:
                project.approved_budget = project.final_budget
            project.status = Project.ProjectStatus.IN_PROGRESS
            project.publish_status = Project.PublishStatus.PUBLISHED
            project.published_at = now
            project.published_by = user
            project.save(
                update_fields=[
                    "project_no",
                    "level",
                    "approved_budget",
                    "status",
                    "publish_status",
                    "published_at",
                    "published_by",
                    "updated_at",
                ]
            )
            if not was_published:
                NotificationService.notify_establishment_published(project)
            published += 1

        notice = None
        if published:
            notice = PublicationService._sync_publication_notice(user, now)

        OperationLogService.log(
            operator=user,
            module="立项发布",
            action="发布立项结果",
            target_type="Project",
            detail={
                "published": published,
                "project_ids": list(project_ids),
                "notice_id": notice.id if notice else None,
            },
        )
        return published
