"""
项目申请相关视图
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone

from .models import Project, ProjectAdvisor, ProjectMember
from apps.reviews.models import Review
from apps.reviews.services import ReviewService
from .serializers import ProjectSerializer, ProjectAdvisorSerializer
from apps.dictionaries.models import DictionaryItem


def _to_bool(val, default=True):
    """
    将字符串/布尔转换为布尔，兼容 'true'/'false'/'0'/'1'
    """
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.strip().lower() not in {"false", "0", "no", "n", "off"}
    return default


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_project_application(request):
    """
    创建项目申请（草稿或提交）
    """
    user = request.user
    data = request.data.copy()  # Use copy to be mutable
    is_draft = _to_bool(data.get("is_draft", True))

    try:
        with transaction.atomic():
            # Override backend-controlled fields
            data["leader"] = user.id
            data["status"] = (
                Project.ProjectStatus.DRAFT if is_draft else Project.ProjectStatus.SUBMITTED
            )

            # Ensure defaults for required fields if missing
            # Note: We assume DictionaryItems for defaults exist. In a real app, handle DoesNotExist.
            if not data.get("level"):
                try:
                    data["level"] = DictionaryItem.objects.get(dict_type__code="PROJECT_LEVEL", value="SCHOOL").id
                except DictionaryItem.DoesNotExist:
                    pass # Let serializer validation fail or handle error
            if not data.get("category"):
                 try:
                    data["category"] = DictionaryItem.objects.get(dict_type__code="PROJECT_CATEGORY", value="INNOVATION_TRAINING").id
                 except DictionaryItem.DoesNotExist:
                    pass

            # 序列化并验证
            serializer = ProjectSerializer(data=data)
            if not serializer.is_valid():
                print("Serializer Errors:", serializer.errors)  # Debug logging
                return Response(
                    {
                        "code": 400,
                        "message": "数据验证失败",
                        "errors": serializer.errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 保存项目
            project = serializer.save()

            if not is_draft:
                project.submitted_at = timezone.now()
                project.save()
                # 创建二级申报审核记录（避免重复）
                if not Review.objects.filter(
                    project=project,
                    review_type=Review.ReviewType.APPLICATION,
                    review_level=Review.ReviewLevel.LEVEL2,
                    status=Review.ReviewStatus.PENDING,
                ).exists():
                    ReviewService.create_level2_review(project)

            # 添加指导教师
            import json
            advisors_data = request.data.get("advisors", [])
            if isinstance(advisors_data, str):
                try:
                    advisors_data = json.loads(advisors_data)
                except json.JSONDecodeError:
                    advisors_data = []

            for idx, advisor_data in enumerate(advisors_data):
                # Try to get user_id directly or by employee_id/name
                user_id = advisor_data.get("user") or advisor_data.get("user_id") or advisor_data.get("id")
                
                # If no ID, but name is provided, try to find user by real_name (Risky but helpful for transition)
                if not user_id and advisor_data.get("name"):
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    potential_user = User.objects.filter(real_name=advisor_data.get("name")).first()
                    if potential_user:
                        user_id = potential_user.id
                        
                if user_id:
                     ProjectAdvisor.objects.create(
                        project=project,
                        user_id=user_id,
                        order=idx,
                     )

            # 添加项目负责人为成员
            ProjectMember.objects.create(
                project=project,
                user=user,
                role=ProjectMember.MemberRole.LEADER,
            )

            # 添加其他成员
            members_data = request.data.get("members", [])
            if isinstance(members_data, str):
                try:
                    members_data = json.loads(members_data)
                except json.JSONDecodeError:
                     members_data = []
                     
            for member_data in members_data:
                # Basic implementation: just creating records if we had a way to link users
                # Since we don't know if 'members' contains user IDs or just names
                # For now, we skip or need logic validation
                pass

            return Response(
                {
                    "code": 200,
                    "message": "保存成功" if is_draft else "提交成功",
                    "data": ProjectSerializer(project).data,
                },
                status=status.HTTP_201_CREATED,
            )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response(
            {"code": 500, "message": f"操作失败: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_project_application(request, pk):
    """
    更新项目申请
    """
    user = request.user

    try:
        project = Project.objects.get(pk=pk, leader=user)
    except Project.DoesNotExist:
        return Response(
            {"code": 404, "message": "项目不存在或无权限访问"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # 只能编辑草稿状态的项目
    if project.status != Project.ProjectStatus.DRAFT:
        return Response(
            {"code": 400, "message": "只能编辑草稿状态的项目"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    data = request.data.copy()
    is_draft = _to_bool(data.get("is_draft", True))

    try:
        with transaction.atomic():
            # Verify and update fields
            data["status"] = (
                Project.ProjectStatus.DRAFT if is_draft else Project.ProjectStatus.SUBMITTED
            )
            
            # Use partial update to respect existing fields if not provided
            serializer = ProjectSerializer(project, data=data, partial=True)
            if not serializer.is_valid():
                print("Update Serializer Errors:", serializer.errors)
                return Response(
                    {
                        "code": 400,
                        "message": "数据验证失败",
                        "errors": serializer.errors,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            project = serializer.save()

            if not is_draft:
                project.submitted_at = timezone.now()
                project.save()
                # 创建二级申报审核记录（避免重复）
                if not Review.objects.filter(
                    project=project,
                    review_type=Review.ReviewType.APPLICATION,
                    review_level=Review.ReviewLevel.LEVEL2,
                    status=Review.ReviewStatus.PENDING,
                ).exists():
                    ReviewService.create_level2_review(project)

            # 更新指导教师（先删除旧的）
            project.advisors.all().delete()
            import json
            advisors_data = request.data.get("advisors", [])
            if isinstance(advisors_data, str):
                try:
                    advisors_data = json.loads(advisors_data)
                except json.JSONDecodeError:
                    advisors_data = []
            
            for idx, advisor_data in enumerate(advisors_data):
                # Try to get user_id directly or by employee_id/name
                user_id = advisor_data.get("user") or advisor_data.get("user_id") or advisor_data.get("id")
                
                # If no ID, but name is provided, try to find user by real_name (Risky but helpful for transition)
                if not user_id and advisor_data.get("name"):
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    potential_user = User.objects.filter(real_name=advisor_data.get("name")).first()
                    if potential_user:
                        user_id = potential_user.id

                if user_id:
                     ProjectAdvisor.objects.create(
                        project=project,
                        user_id=user_id,
                        order=idx,
                     )

            return Response(
                {
                    "code": 200,
                    "message": "保存成功" if is_draft else "提交成功",
                    "data": ProjectSerializer(project).data,
                },
                status=status.HTTP_200_OK,
            )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response(
            {"code": 500, "message": f"操作失败: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_my_projects(request):
    """
    获取我的项目列表（支持分页和筛选）
    """
    user = request.user

    # 获取筛选参数
    title = request.query_params.get("title")
    level = request.query_params.get("level")
    category = request.query_params.get("category")
    status_filter = request.query_params.get("status")

    # 获取分页参数
    page = int(request.query_params.get("page", 1))
    page_size = int(request.query_params.get("page_size", 10))

    # 构建查询
    projects = Project.objects.filter(leader=user)

    # 应用筛选
    if title:
        projects = projects.filter(title__icontains=title)
    if level:
        projects = projects.filter(level=level)
    if category:
        projects = projects.filter(category=category)
    if status_filter:
        projects = projects.filter(status=status_filter)

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
def get_my_drafts(request):
    """
    获取我的草稿箱（支持分页和筛选）
    """
    user = request.user

    # 获取筛选参数
    title = request.query_params.get("title")

    # 获取分页参数
    page = int(request.query_params.get("page", 1))
    page_size = int(request.query_params.get("page_size", 10))

    # 构建查询
    drafts = Project.objects.filter(leader=user, status=Project.ProjectStatus.DRAFT)

    # 应用筛选
    if title:
        drafts = drafts.filter(title__icontains=title)

    # 排序
    drafts = drafts.order_by("-updated_at")

    # 总数
    total = drafts.count()

    # 分页
    start = (page - 1) * page_size
    end = start + page_size
    drafts = drafts[start:end]

    # 序列化
    serializer = ProjectSerializer(drafts, many=True)

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
