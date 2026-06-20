"""
项目结题服务
"""

import json
import logging

from django.db import transaction
from django.utils import timezone
from rest_framework import status

from apps.dictionaries.models import DictionaryItem
from apps.system_settings.services.workflow_service import WorkflowService
from apps.system_settings.services import SystemSettingService
from apps.utils.pagination import optional_positive_int, positive_int_query

from ..models import Project, ProjectAchievement, ProjectPhaseInstance
from ..serializers import ProjectAchievementSerializer, ProjectSerializer
from ..upload_validation import (
    validate_project_document_file,
    validate_project_support_file,
)


logger = logging.getLogger(__name__)


def _parse_json_payload(value, default):
    if value is None:
        return default
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, (dict, list)) else default
        except json.JSONDecodeError:
            return default
    return default


def _parse_achievements_payload(data):
    if "achievements_json" in data:
        raw_achievements = data["achievements_json"]
    else:
        raw_achievements = data.get("achievements", [])

    if raw_achievements in (None, ""):
        return []
    if isinstance(raw_achievements, str):
        try:
            achievements_data = json.loads(raw_achievements)
        except (TypeError, json.JSONDecodeError) as exc:
            raise ValueError("成果数据格式错误") from exc
    else:
        achievements_data = raw_achievements

    if not isinstance(achievements_data, list) or not all(
        isinstance(item, dict) for item in achievements_data
    ):
        raise ValueError("成果数据格式错误")
    return achievements_data


def _resolve_achievement_type_value(raw_value, cache):
    if raw_value is None or raw_value == "":
        return None
    if isinstance(raw_value, int) or (
        isinstance(raw_value, str) and raw_value.isdigit()
    ):
        item_id = int(raw_value)
        if item_id not in cache:
            cache[item_id] = DictionaryItem.objects.filter(id=item_id).first()
        item = cache.get(item_id)
        return item.value if item else None
    if isinstance(raw_value, str):
        return raw_value
    return None


def _resolve_achievement_type_obj(raw_value):
    if raw_value is None or raw_value == "":
        return None
    if isinstance(raw_value, int) or (
        isinstance(raw_value, str) and raw_value.isdigit()
    ):
        return DictionaryItem.objects.filter(id=int(raw_value), is_active=True).first()
    if isinstance(raw_value, str):
        return DictionaryItem.objects.filter(
            dict_type__code="achievement_type", value=raw_value, is_active=True
        ).first()
    return None


def _validate_closure_achievements(achievements_data):
    for achievement_data in achievements_data or []:
        title = achievement_data.get("title")
        if not title:
            continue
        ach_type_val = achievement_data.get("achievement_type")
        if ach_type_val is None:
            ach_type_val = achievement_data.get("achievement_type_value")
        if not _resolve_achievement_type_obj(ach_type_val):
            raise ValueError("成果类型不存在")


def _upsert_project_achievements(project, achievements_data, files):
    existing = {str(a.id): a for a in project.achievements.all()}
    seen_ids = set()

    for index, achievement_data in enumerate(achievements_data or []):
        if not isinstance(achievement_data, dict):
            continue

        title = achievement_data.get("title")
        if not title:
            continue

        raw_id = achievement_data.get("id")
        ach_id = None
        if raw_id is not None and raw_id != "":
            try:
                ach_id = int(raw_id)
            except (TypeError, ValueError):
                ach_id = None

        ach_type_val = achievement_data.get("achievement_type")
        if ach_type_val is None:
            ach_type_val = achievement_data.get("achievement_type_value")
        ach_type_obj = _resolve_achievement_type_obj(ach_type_val)

        payload = {
            "achievement_type": ach_type_obj,
            "title": title or "",
            "description": achievement_data.get("description", ""),
            "extra_data": _parse_json_payload(achievement_data.get("extra_data"), {}),
            "authors": achievement_data.get("authors", ""),
            "journal": achievement_data.get("journal", ""),
            "publication_date": achievement_data.get("publication_date") or None,
            "doi": achievement_data.get("doi", ""),
            "patent_no": achievement_data.get("patent_no", ""),
            "patent_type": achievement_data.get("patent_type", ""),
            "applicant": achievement_data.get("applicant", ""),
            "copyright_no": achievement_data.get("copyright_no", ""),
            "copyright_owner": achievement_data.get("copyright_owner", ""),
            "competition_name": achievement_data.get("competition_name", ""),
            "award_level": achievement_data.get("award_level", ""),
            "award_date": achievement_data.get("award_date") or None,
        }

        instance = None
        if ach_id is not None:
            instance = existing.get(str(ach_id))

        if instance:
            for key, val in payload.items():
                setattr(instance, key, val)
            instance.save()
            seen_ids.add(str(instance.id))
        else:
            instance = ProjectAchievement.objects.create(project=project, **payload)
            seen_ids.add(str(instance.id))

        file_key = f"achievement_{index}"
        if file_key in files:
            instance.attachment = validate_project_support_file(
                files[file_key],
                label="成果附件",
                max_size_mb=20,
                empty_as_none=True,
                error_class=ValueError,
            )
            instance.save(update_fields=["attachment"])

    for existing_id, existing_obj in existing.items():
        if existing_id not in seen_ids:
            existing_obj.delete()


def _validate_expected_results(project, achievements_data):
    expected_list = project.expected_results_data or []
    if not expected_list:
        return True, ""

    type_cache = {}
    actual_counts = {}
    for item in achievements_data or []:
        type_value = _resolve_achievement_type_value(
            item.get("achievement_type"), type_cache
        )
        if not type_value:
            continue
        actual_counts[type_value] = actual_counts.get(type_value, 0) + 1

    for expected in expected_list:
        if not isinstance(expected, dict):
            continue
        raw_type = expected.get("achievement_type")
        type_value = _resolve_achievement_type_value(raw_type, type_cache)
        if not type_value:
            continue
        try:
            expected_count = int(
                expected.get("expected_count") or expected.get("count") or 0
            )
        except (TypeError, ValueError):
            expected_count = 0
        if expected_count <= 0:
            continue
        actual = actual_counts.get(type_value, 0)
        if actual < expected_count:
            label = None
            item = DictionaryItem.objects.filter(
                dict_type__code="achievement_type", value=type_value
            ).first()
            if item:
                label = item.label
            label = label or type_value
            return (
                False,
                f"预期成果未完成：{label} 需{expected_count}项，当前{actual}项",
            )

    return True, ""


def _assign_closure_uploads(project, files):
    if "final_report" in files:
        project.final_report = validate_project_document_file(
            files["final_report"],
            label="结题报告",
            max_size_mb=2,
            error_class=ValueError,
        )
    if "achievement_file" in files:
        project.achievement_file = validate_project_support_file(
            files["achievement_file"],
            label="支撑附件",
            max_size_mb=20,
            empty_as_none=True,
            error_class=ValueError,
        )


class ProjectClosureService:
    @staticmethod
    def _has_school_admin_scope(user):
        return user.is_school_admin or user.is_level1_admin

    @staticmethod
    def _get_current_batch():
        return SystemSettingService.get_current_batch()

    @staticmethod
    def pending(request):
        user = request.user
        if not user.is_student:
            return (
                {"code": 403, "message": "只有学生可以查看待结题项目"},
                status.HTTP_403_FORBIDDEN,
            )
        title = request.query_params.get("title")
        level = request.query_params.get("level")
        page = positive_int_query(request.query_params, "page", 1)
        page_size = positive_int_query(request.query_params, "page_size", 10, 100)

        current_batch = ProjectClosureService._get_current_batch()
        if not current_batch:
            return (
                {
                    "code": 200,
                    "message": "获取成功",
                    "data": [],
                    "total": 0,
                    "page": page,
                    "page_size": page_size,
                },
                status.HTTP_200_OK,
            )

        projects = Project.objects.filter(
            leader=user,
            batch=current_batch,
            status__in=[
                Project.ProjectStatus.READY_FOR_CLOSURE,
                Project.ProjectStatus.CLOSURE_RETURNED,
                Project.ProjectStatus.CLOSURE_LEVEL2_REJECTED,
                Project.ProjectStatus.CLOSURE_LEVEL1_REJECTED,
            ],
        )

        if title:
            projects = projects.filter(title__icontains=title)
        if level:
            parsed_level = optional_positive_int(level)
            if parsed_level is None:
                projects = projects.none()
            else:
                projects = projects.filter(level_id=parsed_level)

        projects = projects.order_by("-created_at")
        total = projects.count()
        start = (page - 1) * page_size
        end = start + page_size
        projects = projects[start:end]

        serializer = ProjectSerializer(projects, many=True)
        return (
            {
                "code": 200,
                "message": "获取成功",
                "data": serializer.data,
                "total": total,
                "page": page,
                "page_size": page_size,
            },
            status.HTTP_200_OK,
        )

    @staticmethod
    def applied(request):
        user = request.user
        title = request.query_params.get("title")
        level = request.query_params.get("level")
        page = positive_int_query(request.query_params, "page", 1)
        page_size = positive_int_query(request.query_params, "page_size", 10, 100)

        current_batch = ProjectClosureService._get_current_batch()
        if not current_batch:
            return (
                {
                    "code": 200,
                    "message": "获取成功",
                    "data": [],
                    "total": 0,
                    "page": page,
                    "page_size": page_size,
                },
                status.HTTP_200_OK,
            )

        closure_statuses = [
            Project.ProjectStatus.CLOSURE_SUBMITTED,
            Project.ProjectStatus.CLOSURE_LEVEL2_REVIEWING,
            Project.ProjectStatus.CLOSURE_LEVEL2_APPROVED,
            Project.ProjectStatus.CLOSURE_LEVEL2_REJECTED,
            Project.ProjectStatus.CLOSURE_LEVEL1_REVIEWING,
            Project.ProjectStatus.CLOSURE_LEVEL1_APPROVED,
            Project.ProjectStatus.CLOSURE_LEVEL1_REJECTED,
            Project.ProjectStatus.COMPLETED,
            Project.ProjectStatus.CLOSED,
        ]

        if user.is_college_admin:
            projects = Project.objects.filter(
                leader__college=user.college,
                status__in=closure_statuses,
                batch=current_batch,
            )
        elif ProjectClosureService._has_school_admin_scope(user):
            projects = Project.objects.filter(
                status__in=closure_statuses, batch=current_batch
            )
        elif user.is_student:
            projects = Project.objects.filter(
                leader=user, status__in=closure_statuses, batch=current_batch
            )
        else:
            return (
                {"code": 403, "message": "无权限查看结题申请"},
                status.HTTP_403_FORBIDDEN,
            )

        if title:
            projects = projects.filter(title__icontains=title)
        if level:
            parsed_level = optional_positive_int(level)
            if parsed_level is None:
                projects = projects.none()
            else:
                projects = projects.filter(level_id=parsed_level)

        projects = projects.order_by("-closure_applied_at")
        total = projects.count()
        start = (page - 1) * page_size
        end = start + page_size
        projects = projects[start:end]

        serializer = ProjectSerializer(projects, many=True)
        return (
            {
                "code": 200,
                "message": "获取成功",
                "data": serializer.data,
                "total": total,
                "page": page,
                "page_size": page_size,
            },
            status.HTTP_200_OK,
        )

    @staticmethod
    def drafts(request):
        user = request.user
        if not user.is_student:
            return (
                {"code": 403, "message": "只有学生可以查看结题草稿"},
                status.HTTP_403_FORBIDDEN,
            )
        title = request.query_params.get("title")
        page = positive_int_query(request.query_params, "page", 1)
        page_size = positive_int_query(request.query_params, "page_size", 10, 100)

        current_batch = ProjectClosureService._get_current_batch()
        if not current_batch:
            return (
                {
                    "code": 200,
                    "message": "获取成功",
                    "data": [],
                    "total": 0,
                    "page": page,
                    "page_size": page_size,
                },
                status.HTTP_200_OK,
            )

        projects = Project.objects.filter(
            leader=user,
            status=Project.ProjectStatus.CLOSURE_DRAFT,
            batch=current_batch,
        )

        if title:
            projects = projects.filter(title__icontains=title)

        projects = projects.order_by("-updated_at")
        total = projects.count()
        start = (page - 1) * page_size
        end = start + page_size
        projects = projects[start:end]

        serializer = ProjectSerializer(projects, many=True)
        return (
            {
                "code": 200,
                "message": "获取成功",
                "data": serializer.data,
                "total": total,
                "page": page,
                "page_size": page_size,
            },
            status.HTTP_200_OK,
        )

    @staticmethod
    def create_application(request, pk):
        user = request.user
        if not user.is_student:
            return (
                {"code": 403, "message": "只有学生可以申请结题"},
                status.HTTP_403_FORBIDDEN,
            )
        current_batch = ProjectClosureService._get_current_batch()
        if not current_batch:
            return (
                {"code": 400, "message": "当前没有可用批次"},
                status.HTTP_400_BAD_REQUEST,
            )

        try:
            project = Project.objects.get(pk=pk, leader=user, batch=current_batch)
        except Project.DoesNotExist:
            return (
                {"code": 404, "message": "项目不存在或无权限访问"},
                status.HTTP_404_NOT_FOUND,
            )

        allowed_statuses = {
            Project.ProjectStatus.READY_FOR_CLOSURE,
            Project.ProjectStatus.CLOSURE_RETURNED,
            Project.ProjectStatus.CLOSURE_DRAFT,
            Project.ProjectStatus.CLOSURE_LEVEL2_REJECTED,
            Project.ProjectStatus.CLOSURE_LEVEL1_REJECTED,
        }
        if project.status not in allowed_statuses:
            return (
                {"code": 400, "message": "当前项目状态无法申请结题"},
                status.HTTP_400_BAD_REQUEST,
            )

        data = request.data
        is_draft = data.get("is_draft")
        if isinstance(is_draft, str):
            is_draft = is_draft.lower() == "true"

        try:
            achievements_data = _parse_achievements_payload(data)
            _validate_closure_achievements(achievements_data)
            with transaction.atomic():
                if not is_draft:
                    ok, msg = WorkflowService.check_phase_window(
                        "CLOSURE", project.batch, timezone.now().date()
                    )
                    if not ok:
                        return (
                            {
                                "code": 400,
                                "message": msg or "当前不在结题提交时间范围内",
                            },
                            status.HTTP_400_BAD_REQUEST,
                        )

                    ok, msg = _validate_expected_results(project, achievements_data)
                    if not ok:
                        return (
                            {"code": 400, "message": msg},
                            status.HTTP_400_BAD_REQUEST,
                        )

                project.status = (
                    Project.ProjectStatus.CLOSURE_DRAFT
                    if is_draft
                    else Project.ProjectStatus.CLOSURE_SUBMITTED
                )
                if not is_draft:
                    project.closure_applied_at = timezone.now()

                if data.get("expected_results"):
                    project.expected_results = data.get("expected_results")

                _assign_closure_uploads(project, request.FILES)

                project.save()

                _upsert_project_achievements(project, achievements_data, request.FILES)

                if not is_draft:
                    from apps.reviews.services import ReviewService

                    ReviewService.start_phase_review(
                        project,
                        ProjectPhaseInstance.Phase.CLOSURE,
                        created_by=user,
                    )

                return (
                    {
                        "code": 200,
                        "message": "保存成功" if is_draft else "提交成功",
                        "data": ProjectSerializer(project).data,
                    },
                    status.HTTP_200_OK,
                )
        except ValueError as exc:
            return (
                {"code": 400, "message": str(exc)},
                status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            logger.exception("Closure application creation failed for project %s", pk)
            return (
                {"code": 500, "message": "操作失败，请稍后重试"},
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @staticmethod
    def update_application(request, pk):
        user = request.user
        if not user.is_student:
            return (
                {"code": 403, "message": "只有学生可以修改结题申请"},
                status.HTTP_403_FORBIDDEN,
            )
        current_batch = ProjectClosureService._get_current_batch()
        if not current_batch:
            return (
                {"code": 400, "message": "当前没有可用批次"},
                status.HTTP_400_BAD_REQUEST,
            )

        try:
            project = Project.objects.get(pk=pk, leader=user, batch=current_batch)
        except Project.DoesNotExist:
            return (
                {"code": 404, "message": "项目不存在或无权限访问"},
                status.HTTP_404_NOT_FOUND,
            )

        if project.status != Project.ProjectStatus.CLOSURE_DRAFT:
            return (
                {"code": 400, "message": "只能编辑结题草稿状态的项目"},
                status.HTTP_400_BAD_REQUEST,
            )

        data = request.data
        is_draft = data.get("is_draft")
        if isinstance(is_draft, str):
            is_draft = is_draft.lower() == "true"

        try:
            achievements_data = _parse_achievements_payload(data)
            _validate_closure_achievements(achievements_data)
            with transaction.atomic():
                if not is_draft:
                    ok, msg = WorkflowService.check_phase_window(
                        "CLOSURE", project.batch, timezone.now().date()
                    )
                    if not ok:
                        return (
                            {
                                "code": 400,
                                "message": msg or "当前不在结题提交时间范围内",
                            },
                            status.HTTP_400_BAD_REQUEST,
                        )

                    ok, msg = _validate_expected_results(project, achievements_data)
                    if not ok:
                        return (
                            {"code": 400, "message": msg},
                            status.HTTP_400_BAD_REQUEST,
                        )

                project.status = (
                    Project.ProjectStatus.CLOSURE_DRAFT
                    if is_draft
                    else Project.ProjectStatus.CLOSURE_SUBMITTED
                )
                if not is_draft:
                    project.closure_applied_at = timezone.now()

                if data.get("expected_results"):
                    project.expected_results = data.get("expected_results")

                _assign_closure_uploads(project, request.FILES)

                project.save()

                _upsert_project_achievements(project, achievements_data, request.FILES)

                if not is_draft:
                    from apps.reviews.services import ReviewService

                    ReviewService.start_phase_review(
                        project,
                        ProjectPhaseInstance.Phase.CLOSURE,
                        created_by=user,
                    )

                return (
                    {
                        "code": 200,
                        "message": "保存成功" if is_draft else "提交成功",
                        "data": ProjectSerializer(project).data,
                    },
                    status.HTTP_200_OK,
                )
        except ValueError as exc:
            return (
                {"code": 400, "message": str(exc)},
                status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            logger.exception("Closure application update failed for project %s", pk)
            return (
                {"code": 500, "message": "操作失败，请稍后重试"},
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @staticmethod
    def delete(request, pk):
        user = request.user
        if not user.is_student:
            return (
                {"code": 403, "message": "只有学生可以删除结题草稿"},
                status.HTTP_403_FORBIDDEN,
            )
        current_batch = ProjectClosureService._get_current_batch()
        if not current_batch:
            return (
                {"code": 400, "message": "当前没有可用批次"},
                status.HTTP_400_BAD_REQUEST,
            )

        try:
            project = Project.objects.get(pk=pk, leader=user, batch=current_batch)
        except Project.DoesNotExist:
            return (
                {"code": 404, "message": "项目不存在或无权限访问"},
                status.HTTP_404_NOT_FOUND,
            )

        if project.status != Project.ProjectStatus.CLOSURE_DRAFT:
            return (
                {"code": 400, "message": "只能删除结题草稿"},
                status.HTTP_400_BAD_REQUEST,
            )

        try:
            project.status = Project.ProjectStatus.READY_FOR_CLOSURE
            project.save()
            return {"code": 200, "message": "删除成功"}, status.HTTP_200_OK
        except Exception:
            logger.exception("Closure draft deletion failed for project %s", pk)
            return (
                {"code": 500, "message": "删除失败，请稍后重试"},
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @staticmethod
    def achievements(request, pk):
        user = request.user
        if not user.is_student:
            return (
                {"code": 403, "message": "只有学生可以查看结题成果"},
                status.HTTP_403_FORBIDDEN,
            )
        current_batch = ProjectClosureService._get_current_batch()
        if not current_batch:
            return (
                {"code": 400, "message": "当前没有可用批次"},
                status.HTTP_400_BAD_REQUEST,
            )

        try:
            project = Project.objects.get(pk=pk, leader=user, batch=current_batch)
        except Project.DoesNotExist:
            return (
                {"code": 404, "message": "项目不存在或无权限访问"},
                status.HTTP_404_NOT_FOUND,
            )

        achievements = project.achievements.all()
        serializer = ProjectAchievementSerializer(
            achievements, many=True, context={"request": request}
        )
        return (
            {"code": 200, "message": "获取成功", "data": serializer.data},
            status.HTTP_200_OK,
        )
