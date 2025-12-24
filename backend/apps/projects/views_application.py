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
from .services import ProjectService
from apps.reviews.models import Review
from apps.reviews.services import ReviewService
from .serializers import ProjectSerializer
from apps.dictionaries.models import DictionaryItem
from apps.system_settings.services import SystemSettingService
from django.contrib.auth import get_user_model
from django.utils import timezone
import json


def _generate_project_no(year, college_code=""):
    """
    生成项目编号：年份 + 学院代码 + 序号
    """
    return ProjectService.generate_project_no(year, college_code)


def _to_bool(val, default=True):
    """
    将字符串/布尔转换为布尔，兼容 'true'/'false'/'0'/'1'
    """
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.strip().lower() not in {"false", "0", "no", "n", "off"}
    return default


def _normalize_list(value):
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, list) else []
        except json.JSONDecodeError:
            return []
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return []


def _get_active_projects_qs(batch=None):
    queryset = Project.objects.exclude(
        status__in=[
            Project.ProjectStatus.DRAFT,
            Project.ProjectStatus.TEACHER_REJECTED,
            Project.ProjectStatus.COMPLETED,
            Project.ProjectStatus.CLOSED,
            Project.ProjectStatus.TERMINATED,
        ]
    )
    if batch:
        queryset = queryset.filter(batch=batch)
    return queryset


def _get_current_batch():
    return SystemSettingService.get_current_batch()


def _check_application_window(batch=None):
    ok, msg = SystemSettingService.check_window(
        "APPLICATION_WINDOW", timezone.now().date(), batch=batch
    )
    return ok, msg or "当前不在申报时间范围内"


def _validate_limits(user, advisors_data, members_data, project=None, batch=None):
    limits = SystemSettingService.get_setting("LIMIT_RULES", batch=batch)
    max_advisors = int(limits.get("max_advisors", 2) or 0)
    max_members = int(limits.get("max_members", 5) or 0)
    max_teacher_active = int(limits.get("max_teacher_active", 0) or 0)
    max_student_member = int(limits.get("max_student_member", 1) or 0)
    advisor_title_required = bool(limits.get("advisor_title_required", False))
    teacher_excellent_bonus = int(limits.get("teacher_excellent_bonus", 0) or 0)

    if max_advisors and len(advisors_data) > max_advisors:
        return False, f"指导教师人数不能超过{max_advisors}人"

    if max_members and len(members_data) > max_members:
        return False, f"项目成员人数不能超过{max_members}人"

    active_projects = _get_active_projects_qs(batch=batch)
    if project:
        active_projects = active_projects.exclude(id=project.id)

    # 指导教师数量限制
    if max_teacher_active:
        excellent_project_ids = []
        if teacher_excellent_bonus:
            from apps.reviews.models import Review

            excellent_project_ids = list(
                Review.objects.filter(
                    review_type=Review.ReviewType.CLOSURE,
                    review_level=Review.ReviewLevel.LEVEL1,
                    status=Review.ReviewStatus.APPROVED,
                    closure_rating=Review.ClosureRating.EXCELLENT,
                ).values_list("project_id", flat=True)
            )

        for advisor in advisors_data:
            advisor_id = (
                advisor.get("user")
                or advisor.get("user_id")
                or advisor.get("id")
            )
            if not advisor_id:
                continue
            count = active_projects.filter(advisors__user_id=advisor_id).distinct().count()
            bonus = 0
            if teacher_excellent_bonus and excellent_project_ids:
                bonus = (
                    ProjectAdvisor.objects.filter(
                        user_id=advisor_id, project_id__in=excellent_project_ids
                    )
                    .distinct()
                    .count()
                    * teacher_excellent_bonus
                )
            if count >= (max_teacher_active + bonus):
                return False, "指导教师在研项目数量已达上限"

    # 指导教师职称校验
    if advisor_title_required:
        for advisor in advisors_data:
            title = advisor.get("title")
            if not title:
                return False, "指导教师职称信息不能为空"

    # 学生成员参与上限
    if max_student_member:
        for member in members_data:
            member_id = (
                member.get("user")
                or member.get("user_id")
                or member.get("id")
            )
            if not member_id:
                continue
            count = active_projects.filter(projectmember__user_id=member_id).distinct().count()
            if count >= max_student_member:
                return False, "项目成员已参与项目数量达到上限"

    return True, ""


def _get_or_create_user_by_identity(employee_id=None, name=None, role=None, phone=None, email=None, department=None):
    """
    依据工号/学号或姓名查找/创建用户，用于草稿保存需要回显指导教师/成员。
    避免缺少用户导致草稿无法回显。
    """
    User = get_user_model()
    user = None
    if employee_id:
        user = User.objects.filter(employee_id=employee_id).first()
    if not user and name:
        user = User.objects.filter(real_name=name).first()

    if user:
        updated_fields = []
        if phone and user.phone != phone:
            user.phone = phone
            updated_fields.append("phone")
        if email and user.email != email:
            user.email = email
            updated_fields.append("email")
        if department and user.department != department:
            user.department = department
            updated_fields.append("department")
        if updated_fields:
            user.save(update_fields=updated_fields)
        return user.id

    # Create placeholder user
    username = employee_id or f"temp_{int(timezone.now().timestamp())}"
    employee_id_val = employee_id or username
    real_name = name or employee_id_val
    role_val = role or User.UserRole.STUDENT
    user = User(
        username=username,
        employee_id=employee_id_val,
        real_name=real_name,
        role=role_val,
        phone=phone or "",
        email=email or "",
        department=department or "",
    )
    user.set_unusable_password()
    user.save()
    return user.id


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
            current_batch = _get_current_batch()
            if not is_draft:
                ok, msg = _check_application_window(current_batch)
                if not ok:
                    return Response(
                        {"code": 400, "message": msg},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # Override backend-controlled fields
            data["leader"] = user.id
            data["status"] = (
                Project.ProjectStatus.DRAFT if is_draft else Project.ProjectStatus.SUBMITTED
            )

            # Sync leader contact info to User profile for draft echo
            leader_updates = []
            if data.get("leader_contact"):
                user.phone = data.get("leader_contact")
                leader_updates.append("phone")
            if data.get("leader_email"):
                user.email = data.get("leader_email")
                leader_updates.append("email")
            if data.get("major_code"):
                user.major = data.get("major_code")
                leader_updates.append("major")
            if leader_updates:
                user.save(update_fields=leader_updates)

            # Ensure defaults for required fields if missing
            # Note: We assume DictionaryItems for defaults exist. In a real app, handle DoesNotExist.
            if not data.get("level"):
                default_level = (
                    DictionaryItem.objects.filter(dict_type__code="project_level")
                    .order_by("sort_order", "id")
                    .first()
                )
                if default_level:
                    data["level"] = default_level.value
            if not data.get("category"):
                default_category = (
                    DictionaryItem.objects.filter(dict_type__code="project_type")
                    .order_by("sort_order", "id")
                    .first()
                )
                if default_category:
                    data["category"] = default_category.value

            advisors_data = _normalize_list(request.data.get("advisors", []))
            members_data = _normalize_list(request.data.get("members", []))
            expected_results_data = request.data.get("expected_results_data")
            if expected_results_data is not None:
                data["expected_results_data"] = _normalize_list(expected_results_data)

            ok, msg = _validate_limits(
                user, advisors_data, members_data, batch=current_batch
            )
            if not ok:
                return Response(
                    {"code": 400, "message": msg},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 序列化并验证
            serializer = ProjectSerializer(
                data=data, context={"request": request, "is_draft": is_draft}
            )
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

            if current_batch and not project.batch:
                project.batch = current_batch
            if project.batch:
                project.year = project.batch.year

            if not is_draft:
                project.submitted_at = timezone.now()
                if not project.project_no:
                    project.project_no = _generate_project_no(
                        project.year or timezone.now().year, user.college
                    )
            project.save()
            # 创建导师审核记录（避免重复）
            if not is_draft and not Review.objects.filter(
                project=project,
                review_type=Review.ReviewType.APPLICATION,
                review_level=Review.ReviewLevel.TEACHER,
                status=Review.ReviewStatus.PENDING,
            ).exists():
                ReviewService.create_teacher_review(project)

            # 添加指导教师
            advisors_data = advisors_data or []
            for idx, advisor_data in enumerate(advisors_data):
                # Try to get user_id directly or by employee_id/name
                user_id = advisor_data.get("user") or advisor_data.get("user_id") or advisor_data.get("id")
                job_number = advisor_data.get("job_number") or advisor_data.get("employee_id")
                name = advisor_data.get("name")
                contact = advisor_data.get("contact")
                email = advisor_data.get("email")
                title = advisor_data.get("title")
                
                if not user_id:
                    user_id = _get_or_create_user_by_identity(
                        employee_id=job_number,
                        name=name,
                        role=None,
                        phone=contact,
                        email=email,
                        department=title,
                    )

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
            members_data = members_data or []
            for member_data in members_data:
                user_id = (
                    member_data.get("user")
                    or member_data.get("user_id")
                    or member_data.get("id")
                )
                student_id = member_data.get("student_id")
                name = member_data.get("name")
                if not user_id:
                    user_id = _get_or_create_user_by_identity(
                        employee_id=student_id,
                        name=name,
                        role=None,
                    )

                if not user_id or str(user_id) == str(user.id):
                    continue  # Skip invalid entries or duplicate leader

                ProjectMember.objects.get_or_create(
                    project=project,
                    user_id=user_id,
                    defaults={
                        "role": ProjectMember.MemberRole.MEMBER,
                        "contribution": member_data.get("contribution", ""),
                    },
                )

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

    # 只能编辑草稿或导师退回的项目
    if project.status not in [
        Project.ProjectStatus.DRAFT,
        Project.ProjectStatus.TEACHER_REJECTED,
    ]:
        return Response(
            {"code": 400, "message": "只能编辑草稿或导师退回的项目"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    data = request.data.copy()
    is_draft = _to_bool(data.get("is_draft", True))

    try:
        with transaction.atomic():
            current_batch = _get_current_batch()
            if not is_draft:
                ok, msg = _check_application_window(current_batch)
                if not ok:
                    return Response(
                        {"code": 400, "message": msg},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # Verify and update fields
            data["status"] = (
                Project.ProjectStatus.DRAFT if is_draft else Project.ProjectStatus.SUBMITTED
            )

            # Sync leader contact info to User profile for draft echo
            leader_updates = []
            if data.get("leader_contact"):
                user.phone = data.get("leader_contact")
                leader_updates.append("phone")
            if data.get("leader_email"):
                user.email = data.get("leader_email")
                leader_updates.append("email")
            if data.get("major_code"):
                user.major = data.get("major_code")
                leader_updates.append("major")
            if leader_updates:
                user.save(update_fields=leader_updates)
            
            advisors_data = _normalize_list(request.data.get("advisors", []))
            members_data = _normalize_list(request.data.get("members", []))
            expected_results_data = request.data.get("expected_results_data")
            if expected_results_data is not None:
                data["expected_results_data"] = _normalize_list(expected_results_data)

            ok, msg = _validate_limits(
                user, advisors_data, members_data, project, batch=current_batch
            )
            if not ok:
                return Response(
                    {"code": 400, "message": msg},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Use partial update to respect existing fields if not provided
            serializer = ProjectSerializer(
                project,
                data=data,
                partial=True,
                context={"request": request, "is_draft": is_draft},
            )
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

            if current_batch and not project.batch:
                project.batch = current_batch
            if project.batch:
                project.year = project.batch.year

            if not is_draft:
                project.submitted_at = timezone.now()
                if not project.project_no:
                    project.project_no = _generate_project_no(
                        project.year or timezone.now().year, user.college
                    )
            project.save()
            # 创建导师审核记录（避免重复）
            if not is_draft and not Review.objects.filter(
                project=project,
                review_type=Review.ReviewType.APPLICATION,
                review_level=Review.ReviewLevel.TEACHER,
                status=Review.ReviewStatus.PENDING,
            ).exists():
                ReviewService.create_teacher_review(project)

            # 更新指导教师（先删除旧的）
            project.advisors.all().delete()
            advisors_data = advisors_data or []
            for idx, advisor_data in enumerate(advisors_data):
                # Try to get user_id directly or by employee_id/name
                user_id = advisor_data.get("user") or advisor_data.get("user_id") or advisor_data.get("id")
                job_number = advisor_data.get("job_number") or advisor_data.get("employee_id")
                name = advisor_data.get("name")
                contact = advisor_data.get("contact")
                email = advisor_data.get("email")
                title = advisor_data.get("title")
                
                if not user_id:
                    user_id = _get_or_create_user_by_identity(
                        employee_id=job_number,
                        name=name,
                        role=None,
                        phone=contact,
                        email=email,
                        department=title,
                    )

                if user_id:
                     ProjectAdvisor.objects.create(
                        project=project,
                        user_id=user_id,
                        order=idx,
                     )

            # 更新项目成员（保留负责人，重建其余成员）
            ProjectMember.objects.filter(project=project).exclude(
                role=ProjectMember.MemberRole.LEADER
            ).delete()

            members_data = members_data or []
            for member_data in members_data:
                user_id = (
                    member_data.get("user")
                    or member_data.get("user_id")
                    or member_data.get("id")
                )
                student_id = member_data.get("student_id")
                name = member_data.get("name")
                if not user_id:
                    user_id = _get_or_create_user_by_identity(
                        employee_id=student_id,
                        name=name,
                        role=None,
                    )

                if not user_id or str(user_id) == str(user.id):
                    continue  # Skip invalid entries or duplicate leader

                ProjectMember.objects.get_or_create(
                    project=project,
                    user_id=user_id,
                    defaults={
                        "role": ProjectMember.MemberRole.MEMBER,
                        "contribution": member_data.get("contribution", ""),
                    },
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


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def withdraw_project_application(request, pk):
    """
    撤回项目申报（仅负责人、仅限已提交状态）
    """
    user = request.user

    try:
        project = Project.objects.get(pk=pk, leader=user)
    except Project.DoesNotExist:
        return Response(
            {"code": 404, "message": "项目不存在或无权限访问"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if project.status not in [
        Project.ProjectStatus.SUBMITTED,
        Project.ProjectStatus.TEACHER_AUDITING,
    ]:
        return Response(
            {"code": 400, "message": "当前状态不允许撤回"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    from apps.reviews.models import Review

    with transaction.atomic():
        # 删除未处理的申报审核记录
        Review.objects.filter(
            project=project,
            review_type=Review.ReviewType.APPLICATION,
            status=Review.ReviewStatus.PENDING,
        ).delete()

        project.status = Project.ProjectStatus.DRAFT
        project.submitted_at = None
        project.save(update_fields=["status", "submitted_at", "updated_at"])

    return Response({"code": 200, "message": "撤回成功"})


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
