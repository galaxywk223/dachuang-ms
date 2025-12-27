"""
项目结题管理相关视图
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone

from ..models import Project, ProjectAchievement
from ..serializers import ProjectSerializer, ProjectAchievementSerializer
from apps.reviews.models import Review
from apps.reviews.services import ReviewService
from apps.dictionaries.models import DictionaryItem
from apps.system_settings.services import SystemSettingService
import json


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


def _resolve_achievement_type_value(raw_value, cache):
    if raw_value is None or raw_value == "":
        return None
    if isinstance(raw_value, int) or (isinstance(raw_value, str) and raw_value.isdigit()):
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
    if isinstance(raw_value, int) or (isinstance(raw_value, str) and raw_value.isdigit()):
        return DictionaryItem.objects.filter(id=int(raw_value)).first()
    if isinstance(raw_value, str):
        return DictionaryItem.objects.filter(dict_type__code="achievement_type", value=raw_value).first()
    return None


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
            instance.attachment = files[file_key]
            instance.save(update_fields=["attachment"])  # keep other fields

    # Delete achievements removed by user
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

    expected_type_values = set()
    for expected in expected_list:
        if not isinstance(expected, dict):
            continue
        raw_type = expected.get("achievement_type")
        type_value = _resolve_achievement_type_value(raw_type, type_cache)
        if not type_value:
            continue
        expected_type_values.add(type_value)
        try:
            expected_count = int(expected.get("expected_count") or expected.get("count") or 0)
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
            return False, f"预期成果未完成：{label} 需{expected_count}项，当前{actual}项"

    return True, ""


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_pending_closure_projects(request):
    """
    获取待结题项目列表（中期审核通过后待结题）
    """
    user = request.user

    # 获取筛选参数
    title = request.query_params.get("title")
    level = request.query_params.get("level")

    # 获取分页参数
    page = int(request.query_params.get("page", 1))
    page_size = int(request.query_params.get("page_size", 10))

    # 构建查询 - 待结题项目
    projects = Project.objects.filter(
        leader=user,
        status__in=[
            Project.ProjectStatus.READY_FOR_CLOSURE,
            Project.ProjectStatus.MID_TERM_APPROVED,  # legacy
            Project.ProjectStatus.CLOSURE_RETURNED,
            Project.ProjectStatus.CLOSURE_LEVEL2_REJECTED,
            Project.ProjectStatus.CLOSURE_LEVEL1_REJECTED,
        ],
    )

    # 应用筛选
    if title:
        projects = projects.filter(title__icontains=title)
    if level:
        projects = projects.filter(level=level)

    # 排序
    projects = projects.order_by("-created_at")

    # 总数
    total = projects.count()

    # 分页
    start = (page - 1) * page_size
    end = start + page_size
    projects = projects[start:end]

    # 序列化
    serializer = ProjectSerializer(projects, many=True)

    return Response(
        {
            "code": 200,
            "message": "获取成功",
            "data": serializer.data,
            "total": total,
            "page": page,
            "page_size": page_size,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_applied_closure_projects(request):
    """
    获取已申请结题的项目列表
    """
    user = request.user

    # 获取筛选参数
    title = request.query_params.get("title")
    level = request.query_params.get("level")

    # 获取分页参数
    page = int(request.query_params.get("page", 1))
    page_size = int(request.query_params.get("page_size", 10))

    # 构建查询 - 查询结题相关状态
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

    if user.is_level2_admin:
        projects = Project.objects.filter(
            leader__college=user.college, status__in=closure_statuses
        )
    elif user.is_level1_admin:
        projects = Project.objects.filter(status__in=closure_statuses)
    else:
        projects = Project.objects.filter(leader=user, status__in=closure_statuses)

    # 应用筛选
    if title:
        projects = projects.filter(title__icontains=title)
    if level:
        projects = projects.filter(level=level)

    # 排序
    projects = projects.order_by("-closure_applied_at")

    # 总数
    total = projects.count()

    # 分页
    start = (page - 1) * page_size
    end = start + page_size
    projects = projects[start:end]

    # 序列化
    serializer = ProjectSerializer(projects, many=True)

    return Response(
        {
            "code": 200,
            "message": "获取成功",
            "data": serializer.data,
            "total": total,
            "page": page,
            "page_size": page_size,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_closure_drafts(request):
    """
    获取结题草稿箱
    """
    user = request.user

    # 获取筛选参数
    title = request.query_params.get("title")

    # 获取分页参数
    page = int(request.query_params.get("page", 1))
    page_size = int(request.query_params.get("page_size", 10))

    # 构建查询 - 只查询结题草稿
    projects = Project.objects.filter(
        leader=user, status=Project.ProjectStatus.CLOSURE_DRAFT
    )

    # 应用筛选
    if title:
        projects = projects.filter(title__icontains=title)

    # 排序
    projects = projects.order_by("-updated_at")

    # 总数
    total = projects.count()

    # 分页
    start = (page - 1) * page_size
    end = start + page_size
    projects = projects[start:end]

    # 序列化
    serializer = ProjectSerializer(projects, many=True)

    return Response(
        {
            "code": 200,
            "message": "获取成功",
            "data": serializer.data,
            "total": total,
            "page": page,
            "page_size": page_size,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_closure_application(request, pk):
    """
    创建结题申请（将项目状态从 待结题 改为 CLOSURE_DRAFT 或 CLOSURE_SUBMITTED）
    """
    user = request.user

    try:
        project = Project.objects.get(pk=pk, leader=user)
    except Project.DoesNotExist:
        return Response(
            {"code": 404, "message": "项目不存在或无权限访问"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # 允许进行中/结题驳回的项目重新发起结题
    allowed_statuses = {
        Project.ProjectStatus.READY_FOR_CLOSURE,
        Project.ProjectStatus.MID_TERM_APPROVED,  # legacy
        Project.ProjectStatus.CLOSURE_RETURNED,
        Project.ProjectStatus.CLOSURE_DRAFT,
        Project.ProjectStatus.CLOSURE_LEVEL2_REJECTED,
        Project.ProjectStatus.CLOSURE_LEVEL1_REJECTED,
    }
    if project.status not in allowed_statuses:
        return Response(
            {"code": 400, "message": "当前项目状态无法申请结题"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    data = request.data
    is_draft = data.get("is_draft")
    if isinstance(is_draft, str):
        is_draft = is_draft.lower() == 'true'
    
    # Handle achievements list (might be JSON string in multipart)
    achievements_data = []
    if 'achievements_json' in data:
        try:
            achievements_data = json.loads(data['achievements_json'])
        except json.JSONDecodeError:
            pass
    else:
        achievements_data = data.get("achievements", [])

    try:
        with transaction.atomic():
            if not is_draft:
                ok, msg = SystemSettingService.check_window(
                    "CLOSURE_WINDOW", timezone.now().date(), batch=project.batch
                )
                if not ok:
                    return Response(
                        {"code": 400, "message": msg or "当前不在结题提交时间范围内"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            if not is_draft:
                ok, msg = _validate_expected_results(project, achievements_data)
                if not ok:
                    return Response(
                        {"code": 400, "message": msg},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # 更新项目状态
            project.status = (
                Project.ProjectStatus.CLOSURE_DRAFT
                if is_draft
                else Project.ProjectStatus.CLOSURE_SUBMITTED
            )

            if not is_draft:
                project.closure_applied_at = timezone.now()

            # 更新结题相关字段
            if data.get("research_content"):
                project.research_content = data.get("research_content")
            if data.get("expected_results"):
                project.expected_results = data.get("expected_results")
            
            if "achievement_summary" in data:
                project.achievement_summary = data.get("achievement_summary") or ""

            # Handle Files
            if 'final_report' in request.FILES:
                project.final_report = request.FILES['final_report']
            if 'achievement_file' in request.FILES:
                project.achievement_file = request.FILES['achievement_file']

            project.save()

            # 保存/更新成果信息（保留已有附件，未重新上传则不覆盖）
            _upsert_project_achievements(project, achievements_data, request.FILES)

            # 非草稿时创建/确保导师结题审核记录
            if not is_draft:
                existing_review = Review.objects.filter(
                    project=project,
                    review_type=Review.ReviewType.CLOSURE,
                    review_level=Review.ReviewLevel.TEACHER,
                    status=Review.ReviewStatus.PENDING,
                ).first()
                if not existing_review:
                    ReviewService.create_closure_teacher_review(project)

            return Response(
                {
                    "code": 200,
                    "message": "保存成功" if is_draft else "提交成功",
                    "data": ProjectSerializer(project).data,
                },
                status=status.HTTP_200_OK,
            )

    except Exception as e:
        return Response(
            {"code": 500, "message": f"操作失败: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_closure_application(request, pk):
    """
    更新结题申请（编辑草稿）
    """
    user = request.user

    try:
        project = Project.objects.get(pk=pk, leader=user)
    except Project.DoesNotExist:
        return Response(
            {"code": 404, "message": "项目不存在或无权限访问"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # 只能编辑结题草稿状态的项目
    if project.status != Project.ProjectStatus.CLOSURE_DRAFT:
        return Response(
            {"code": 400, "message": "只能编辑结题草稿状态的项目"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    data = request.data
    is_draft = data.get("is_draft")
    if isinstance(is_draft, str):
        is_draft = is_draft.lower() == 'true'

    # Handle achievements list
    achievements_data = []
    if 'achievements_json' in data:
        try:
            achievements_data = json.loads(data['achievements_json'])
        except json.JSONDecodeError:
            pass
    else:
        achievements_data = data.get("achievements", [])

    try:
        with transaction.atomic():
            if not is_draft:
                ok, msg = SystemSettingService.check_window(
                    "CLOSURE_WINDOW", timezone.now().date(), batch=project.batch
                )
                if not ok:
                    return Response(
                        {"code": 400, "message": msg or "当前不在结题提交时间范围内"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            if not is_draft:
                ok, msg = _validate_expected_results(project, achievements_data)
                if not ok:
                    return Response(
                        {"code": 400, "message": msg},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # 更新项目状态
            project.status = (
                Project.ProjectStatus.CLOSURE_DRAFT
                if is_draft
                else Project.ProjectStatus.CLOSURE_SUBMITTED
            )

            if not is_draft:
                project.closure_applied_at = timezone.now()

            # 更新结题相关字段
            if data.get("research_content"):
                project.research_content = data.get("research_content")
            if data.get("expected_results"):
                project.expected_results = data.get("expected_results")
            
            if "achievement_summary" in data:
                project.achievement_summary = data.get("achievement_summary") or ""

            # Handle Files
            if 'final_report' in request.FILES:
                project.final_report = request.FILES['final_report']
            if 'achievement_file' in request.FILES:
                project.achievement_file = request.FILES['achievement_file']

            project.save()

            # 保存/更新成果信息（保留已有附件，未重新上传则不覆盖）
            _upsert_project_achievements(project, achievements_data, request.FILES)

            # 非草稿时创建/确保导师结题审核记录
            if not is_draft:
                existing_review = Review.objects.filter(
                    project=project,
                    review_type=Review.ReviewType.CLOSURE,
                    review_level=Review.ReviewLevel.TEACHER,
                    status=Review.ReviewStatus.PENDING,
                ).first()
                if not existing_review:
                    ReviewService.create_closure_teacher_review(project)

            return Response(
                {
                    "code": 200,
                    "message": "保存成功" if is_draft else "提交成功",
                    "data": ProjectSerializer(project).data,
                },
                status=status.HTTP_200_OK,
            )

    except Exception as e:
        return Response(
            {"code": 500, "message": f"操作失败: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_closure_draft(request, pk):
    """
    删除结题草稿
    """
    user = request.user

    try:
        project = Project.objects.get(pk=pk, leader=user)
    except Project.DoesNotExist:
        return Response(
            {"code": 404, "message": "项目不存在或无权限访问"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # 只能删除结题草稿
    if project.status != Project.ProjectStatus.CLOSURE_DRAFT:
        return Response(
            {"code": 400, "message": "只能删除结题草稿"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        # 将状态恢复为待结题
        project.status = Project.ProjectStatus.READY_FOR_CLOSURE
        project.save()

        return Response({"code": 200, "message": "删除成功"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"code": 500, "message": f"删除失败: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_project_achievements(request, pk):
    """
    获取项目的成果列表
    """
    user = request.user

    try:
        project = Project.objects.get(pk=pk, leader=user)
    except Project.DoesNotExist:
        return Response(
            {"code": 404, "message": "项目不存在或无权限访问"},
            status=status.HTTP_404_NOT_FOUND,
        )

    achievements = project.achievements.all()
    serializer = ProjectAchievementSerializer(achievements, many=True)

    return Response(
        {"code": 200, "message": "获取成功", "data": serializer.data},
        status=status.HTTP_200_OK,
    )
