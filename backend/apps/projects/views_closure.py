"""
项目结题管理相关视图
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone

from .models import Project, ProjectAchievement
from .serializers import ProjectSerializer, ProjectAchievementSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_pending_closure_projects(request):
    """
    获取待结题项目列表（状态为 IN_PROGRESS）
    """
    user = request.user

    # 获取筛选参数
    title = request.query_params.get("title")
    level = request.query_params.get("level")

    # 获取分页参数
    page = int(request.query_params.get("page", 1))
    page_size = int(request.query_params.get("page_size", 10))

    # 构建查询 - 只查询进行中的项目
    projects = Project.objects.filter(
        leader=user, status=Project.ProjectStatus.IN_PROGRESS
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
    创建结题申请（将项目状态从 IN_PROGRESS 改为 CLOSURE_DRAFT 或 CLOSURE_SUBMITTED）
    """
    user = request.user

    try:
        project = Project.objects.get(pk=pk, leader=user)
    except Project.DoesNotExist:
        return Response(
            {"code": 404, "message": "项目不存在或无权限访问"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # 只有进行中的项目才能申请结题
    if project.status != Project.ProjectStatus.IN_PROGRESS:
        return Response(
            {"code": 400, "message": "只有进行中的项目才能申请结题"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    import json
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
            
            # Handle Files
            if 'final_report' in request.FILES:
                project.final_report = request.FILES['final_report']
            if 'achievement_file' in request.FILES:
                project.achievement_file = request.FILES['achievement_file']

            project.save()

            # 保存成果信息
            # 先删除旧的成果记录（如果是更新）
            if not is_draft:
                project.achievements.all().delete()
            else:
                 # Verify strategy for draft: replace all or update?
                 # Simple strategy: replace all for now to avoid syncing issues
                 project.achievements.all().delete()

            for index, achievement_data in enumerate(achievements_data):
                if achievement_data.get("title"):  # 只保存填写了标题的成果
                    ach = ProjectAchievement.objects.create(
                        project=project,
                        achievement_type=achievement_data.get("achievement_type"),
                        title=achievement_data.get("title", ""),
                        description=achievement_data.get("description", ""),
                        authors=achievement_data.get("authors", ""),
                        journal=achievement_data.get("journal", ""),
                        publication_date=achievement_data.get("publication_date") or None,
                        doi=achievement_data.get("doi", ""),
                        patent_no=achievement_data.get("patent_no", ""),
                        patent_type=achievement_data.get("patent_type", ""),
                        applicant=achievement_data.get("applicant", ""),
                        copyright_no=achievement_data.get("copyright_no", ""),
                        copyright_owner=achievement_data.get("copyright_owner", ""),
                        competition_name=achievement_data.get("competition_name", ""),
                        award_level=achievement_data.get("award_level", ""),
                        award_date=achievement_data.get("award_date") or None,
                    )
                    
                    # Handle achievement attachment
                    # Expect key "achievement_{index}" in FILES
                    file_key = f'achievement_{index}'
                    if file_key in request.FILES:
                        ach.attachment = request.FILES[file_key]
                        ach.save()

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

    import json
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
            
            # Handle Files
            if 'final_report' in request.FILES:
                project.final_report = request.FILES['final_report']
            if 'achievement_file' in request.FILES:
                project.achievement_file = request.FILES['achievement_file']

            project.save()

            # 更新成果信息（先删除旧的）
            project.achievements.all().delete()
            
            for index, achievement_data in enumerate(achievements_data):
                if achievement_data.get("title"):
                    ach = ProjectAchievement.objects.create(
                        project=project,
                        achievement_type=achievement_data.get("achievement_type"),
                        title=achievement_data.get("title", ""),
                        description=achievement_data.get("description", ""),
                        authors=achievement_data.get("authors", ""),
                        journal=achievement_data.get("journal", ""),
                        publication_date=achievement_data.get("publication_date") or None,
                        doi=achievement_data.get("doi", ""),
                        patent_no=achievement_data.get("patent_no", ""),
                        patent_type=achievement_data.get("patent_type", ""),
                        applicant=achievement_data.get("applicant", ""),
                        copyright_no=achievement_data.get("copyright_no", ""),
                        copyright_owner=achievement_data.get("copyright_owner", ""),
                        competition_name=achievement_data.get("competition_name", ""),
                        award_level=achievement_data.get("award_level", ""),
                        award_date=achievement_data.get("award_date") or None,
                    )
                    
                    # Handle achievement attachment
                    file_key = f'achievement_{index}'
                    if file_key in request.FILES:
                        ach.attachment = request.FILES[file_key]
                        ach.save()

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
        # 将状态恢复为进行中
        project.status = Project.ProjectStatus.IN_PROGRESS
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
