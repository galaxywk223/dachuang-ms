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
from .serializers import ProjectSerializer, ProjectAdvisorSerializer


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_project_application(request):
    """
    创建项目申请（草稿或提交）
    """
    user = request.user
    data = request.data
    is_draft = data.get("is_draft", True)  # 默认保存为草稿

    try:
        with transaction.atomic():
            # 创建项目基本信息
            project_data = {
                "title": data.get("title", ""),
                "description": data.get("description", ""),
                "category": data.get("category"),
                "level": data.get("level"),
                "is_key_field": data.get("is_key_field", False),
                "college": data.get("college", ""),
                "major_code": data.get("major_code", ""),
                "self_funding": data.get("self_funding", 0),
                "leader_student_id": data.get("leader_student_id", ""),
                "leader_contact": data.get("leader_contact", ""),
                "leader_email": data.get("leader_email", ""),
                "category_description": data.get("category_description", ""),
                "leader": user.id,
                "status": Project.ProjectStatus.DRAFT
                if is_draft
                else Project.ProjectStatus.SUBMITTED,
            }

            # 序列化并验证
            serializer = ProjectSerializer(data=project_data)
            if not serializer.is_valid():
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

            # 添加指导教师
            advisors_data = data.get("advisors", [])
            for idx, advisor_data in enumerate(advisors_data):
                if advisor_data.get("name"):  # 只添加填写了姓名的指导教师
                    ProjectAdvisor.objects.create(
                        project=project,
                        name=advisor_data.get("name", ""),
                        title=advisor_data.get("title", ""),
                        department=advisor_data.get("department", ""),
                        contact=advisor_data.get("contact", ""),
                        email=advisor_data.get("email", ""),
                        order=idx,
                    )

            # 添加项目负责人为成员
            ProjectMember.objects.create(
                project=project,
                user=user,
                role=ProjectMember.MemberRole.LEADER,
                student_id=data.get("leader_student_id", ""),
                department=user.real_name,
            )

            # 添加其他成员
            members_data = data.get("members", [])
            for member_data in members_data:
                if member_data.get("student_id") and member_data.get("name"):
                    # TODO: 根据学号查找用户，这里暂时跳过
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

    data = request.data
    is_draft = data.get("is_draft", True)

    try:
        with transaction.atomic():
            # 更新项目基本信息
            project_data = {
                "title": data.get("title", project.title),
                "description": data.get("description", project.description),
                "category": data.get("category", project.category),
                "level": data.get("level", project.level),
                "is_key_field": data.get("is_key_field", project.is_key_field),
                "college": data.get("college", project.college),
                "major_code": data.get("major_code", project.major_code),
                "self_funding": data.get("self_funding", project.self_funding),
                "leader_student_id": data.get(
                    "leader_student_id", project.leader_student_id
                ),
                "leader_contact": data.get("leader_contact", project.leader_contact),
                "leader_email": data.get("leader_email", project.leader_email),
                "category_description": data.get(
                    "category_description", project.category_description
                ),
                "status": Project.ProjectStatus.DRAFT
                if is_draft
                else Project.ProjectStatus.SUBMITTED,
            }

            serializer = ProjectSerializer(project, data=project_data, partial=True)
            if not serializer.is_valid():
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

            # 更新指导教师（先删除旧的）
            project.advisors.all().delete()
            advisors_data = data.get("advisors", [])
            for idx, advisor_data in enumerate(advisors_data):
                if advisor_data.get("name"):
                    ProjectAdvisor.objects.create(
                        project=project,
                        name=advisor_data.get("name", ""),
                        title=advisor_data.get("title", ""),
                        department=advisor_data.get("department", ""),
                        contact=advisor_data.get("contact", ""),
                        email=advisor_data.get("email", ""),
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
