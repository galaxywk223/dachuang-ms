"""
项目申报服务
"""

import json
import logging

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from rest_framework import status

from apps.reviews.models import Review
from apps.system_settings.services import SystemSettingService
from apps.utils.pagination import non_negative_int

from ..models import Project, ProjectAdvisor, ProjectMember, ProjectPhaseInstance
from ..serializers import ProjectSerializer
from ..services import ProjectService
from ..services.phase_service import ProjectPhaseService
from ..services.validation_service import ProjectValidationService


logger = logging.getLogger(__name__)


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
        if value == "":
            return []
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as exc:
            raise ValueError("列表数据格式错误") from exc
        value = parsed
    if isinstance(value, list):
        if not all(isinstance(item, dict) for item in value):
            raise ValueError("列表数据格式错误")
        return value
    if value is None:
        return []
    raise ValueError("列表数据格式错误")


def _normalize_nullable_fk_fields(data, fields):
    for field in fields:
        if field not in data:
            continue
        value = data.get(field)
        if value is None:
            continue
        if isinstance(value, str) and value.strip().lower() in {"", "null"}:
            data[field] = None


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
    """
    检查申报时间窗口 - 使用阶段窗口配置
    """
    from apps.system_settings.services.workflow_service import WorkflowService

    if not batch:
        batch = _get_current_batch()

    return WorkflowService.check_phase_window(
        "APPLICATION", batch, timezone.now().date()
    )


def _validate_limits(user, advisors_data, members_data, project=None, batch=None):
    limits = SystemSettingService.get_setting("LIMIT_RULES", batch=batch)
    max_advisors = non_negative_int(limits.get("max_advisors"), 2)
    max_members = non_negative_int(limits.get("max_members"), 5)
    max_teacher_active = non_negative_int(limits.get("max_teacher_active"), 0)
    max_student_member = non_negative_int(limits.get("max_student_member"), 1)

    if max_advisors and len(advisors_data) > max_advisors:
        return False, f"指导教师人数不能超过{max_advisors}人"

    if max_members and len(members_data) > max_members:
        return False, f"项目成员人数不能超过{max_members}人"

    active_projects = _get_active_projects_qs(batch=batch)
    active_projects_all = _get_active_projects_qs(batch=None)
    if project:
        active_projects = active_projects.exclude(id=project.id)
        active_projects_all = active_projects_all.exclude(id=project.id)

    for advisor in advisors_data:
        advisor_id = advisor.get("user") or advisor.get("user_id") or advisor.get("id")
        if not advisor_id:
            continue
        count = active_projects.filter(advisors__user_id=advisor_id).distinct().count()
        historical_unfinished = (
            active_projects_all.filter(advisors__user_id=advisor_id).distinct().exists()
        )
        if historical_unfinished:
            return False, "指导教师存在未结题项目，无法继续指导新项目"
        if max_teacher_active and count >= max_teacher_active:
            return False, "指导教师在研项目数量已达上限"

    if max_student_member:
        for member in members_data:
            member_id = member.get("user") or member.get("user_id") or member.get("id")
            if not member_id:
                continue
            count = (
                active_projects.filter(projectmember__user_id=member_id)
                .distinct()
                .count()
            )
            historical_unfinished = (
                active_projects_all.filter(projectmember__user_id=member_id)
                .distinct()
                .exists()
            )
            if historical_unfinished:
                return False, "成员存在未结题项目，无法继续参与新项目"
            if count >= max_student_member:
                return False, "项目成员已参与项目数量达到上限"

    return True, ""


def _get_or_create_user_by_identity(
    employee_id=None, name=None, role=None, phone=None, email=None, department=None
):
    """
    依据工号/学号或姓名查找用户，用于草稿保存需要回显指导教师/成员。
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

    return None


class ProjectApplicationService:
    @staticmethod
    def create_application(request):
        user = request.user
        if not user.is_student:
            return (
                {"code": 403, "message": "只有学生可以申报项目"},
                status.HTTP_403_FORBIDDEN,
            )
        data = request.data.copy()
        is_draft = _to_bool(data.get("is_draft", True))

        try:
            with transaction.atomic():
                current_batch = _get_current_batch()
                if not current_batch:
                    return (
                        {"code": 400, "message": "当前没有进行中的批次，无法申报项目"},
                        status.HTTP_400_BAD_REQUEST,
                    )
                if not is_draft:
                    ok, msg = _check_application_window(current_batch)
                    if not ok:
                        return (
                            {"code": 400, "message": msg},
                            status.HTTP_400_BAD_REQUEST,
                        )

                data["leader"] = user.id
                data["status"] = (
                    Project.ProjectStatus.DRAFT
                    if is_draft
                    else Project.ProjectStatus.SUBMITTED
                )

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

                _normalize_nullable_fk_fields(
                    data, ["level", "category", "source"]
                )

                advisors_data = _normalize_list(request.data.get("advisors", []))
                members_data = _normalize_list(request.data.get("members", []))
                expected_results_data = request.data.get("expected_results_data")
                if expected_results_data is not None:
                    data["expected_results_data"] = json.dumps(
                        _normalize_list(expected_results_data)
                    )

                ok, msg = _validate_limits(
                    user, advisors_data, members_data, batch=current_batch
                )
                if not ok:
                    return (
                        {"code": 400, "message": msg},
                        status.HTTP_400_BAD_REQUEST,
                    )

                serializer = ProjectSerializer(
                    data=data, context={"request": request, "is_draft": is_draft}
                )
                if not serializer.is_valid():
                    return (
                        {
                            "code": 400,
                            "message": "数据验证失败",
                            "errors": serializer.errors,
                        },
                        status.HTTP_400_BAD_REQUEST,
                    )

                project = serializer.save()

                # 如果不是草稿，则进行智能校验
                if not is_draft:
                    # 临时设置advisors和members列表供校验使用
                    project._advisors_list = advisors_data
                    project._members_list = members_data

                    validation_result = (
                        ProjectValidationService.validate_project_application(
                            project, user, is_update=False
                        )
                    )
                    if not validation_result["is_valid"]:
                        # 校验失败，删除项目并返回错误
                        project.delete()
                        return (
                            {
                                "code": 400,
                                "message": "项目申报校验失败",
                                "errors": validation_result["errors"],
                            },
                            status.HTTP_400_BAD_REQUEST,
                        )

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

                if not is_draft:
                    current_phase = ProjectPhaseService.get_current(
                        project, ProjectPhaseInstance.Phase.APPLICATION
                    )
                    if (
                        current_phase
                        and current_phase.state == ProjectPhaseInstance.State.RETURNED
                    ):
                        ProjectPhaseService.start_new_attempt(
                            project,
                            ProjectPhaseInstance.Phase.APPLICATION,
                            created_by=request.user,
                        )
                    from apps.reviews.services import ReviewService

                    ReviewService.start_phase_review(
                        project,
                        ProjectPhaseInstance.Phase.APPLICATION,
                        created_by=request.user,
                    )

                project.advisors.all().delete()
                for idx, advisor_data in enumerate(advisors_data or []):
                    user_id = (
                        advisor_data.get("user")
                        or advisor_data.get("user_id")
                        or advisor_data.get("id")
                    )
                    job_number = advisor_data.get("job_number") or advisor_data.get(
                        "employee_id"
                    )
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
                            project=project, user_id=user_id, order=idx
                        )

                ProjectMember.objects.filter(project=project).exclude(
                    role=ProjectMember.MemberRole.LEADER
                ).delete()

                for member_data in members_data or []:
                    member_user_id = (
                        member_data.get("user")
                        or member_data.get("user_id")
                        or member_data.get("id")
                    )
                    student_id = member_data.get("student_id")
                    name = member_data.get("name")
                    if not member_user_id:
                        member_user_id = _get_or_create_user_by_identity(
                            employee_id=student_id, name=name, role=None
                        )

                    if not member_user_id or str(member_user_id) == str(user.id):
                        continue

                    ProjectMember.objects.get_or_create(
                        project=project,
                        user_id=member_user_id,
                        defaults={
                            "role": ProjectMember.MemberRole.MEMBER,
                            "contribution": member_data.get("contribution", ""),
                        },
                    )

                return (
                    {
                        "code": 201,
                        "message": "保存成功" if is_draft else "提交成功",
                        "data": ProjectSerializer(project).data,
                    },
                    status.HTTP_201_CREATED,
                )
        except ValueError as exc:
            return (
                {"code": 400, "message": str(exc)},
                status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            logger.exception("Project application creation failed for user %s", user.id)
            return (
                {"code": 500, "message": "操作失败，请稍后重试"},
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @staticmethod
    def update_application(request, pk):
        user = request.user
        if not user.is_student:
            return (
                {"code": 403, "message": "只有学生可以修改项目申报"},
                status.HTTP_403_FORBIDDEN,
            )

        try:
            project = Project.objects.get(pk=pk, leader=user)
        except Project.DoesNotExist:
            return (
                {"code": 404, "message": "项目不存在或无权限访问"},
                status.HTTP_404_NOT_FOUND,
            )

        if project.status not in [
            Project.ProjectStatus.DRAFT,
            Project.ProjectStatus.TEACHER_REJECTED,
            Project.ProjectStatus.APPLICATION_RETURNED,
        ]:
            return (
                {"code": 400, "message": "只能编辑草稿或退回修改的项目"},
                status.HTTP_400_BAD_REQUEST,
            )

        data = request.data.copy()
        is_draft = _to_bool(data.get("is_draft", True))

        try:
            with transaction.atomic():
                current_batch = _get_current_batch()
                if not current_batch or project.batch_id != current_batch.id:
                    return (
                        {"code": 400, "message": "当前批次不允许操作该项目"},
                        status.HTTP_400_BAD_REQUEST,
                    )
                if not is_draft:
                    ok, msg = _check_application_window(current_batch)
                    if not ok:
                        return (
                            {"code": 400, "message": msg},
                            status.HTTP_400_BAD_REQUEST,
                        )

                data["status"] = (
                    Project.ProjectStatus.DRAFT
                    if is_draft
                    else Project.ProjectStatus.SUBMITTED
                )

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

                _normalize_nullable_fk_fields(
                    data, ["level", "category", "source"]
                )

                advisors_data = _normalize_list(request.data.get("advisors", []))
                members_data = _normalize_list(request.data.get("members", []))
                expected_results_data = request.data.get("expected_results_data")
                if expected_results_data is not None:
                    data["expected_results_data"] = json.dumps(
                        _normalize_list(expected_results_data)
                    )

                ok, msg = _validate_limits(
                    user, advisors_data, members_data, project, batch=current_batch
                )
                if not ok:
                    return (
                        {"code": 400, "message": msg},
                        status.HTTP_400_BAD_REQUEST,
                    )

                serializer = ProjectSerializer(
                    project,
                    data=data,
                    partial=True,
                    context={"request": request, "is_draft": is_draft},
                )
                if not serializer.is_valid():
                    return (
                        {
                            "code": 400,
                            "message": "数据验证失败",
                            "errors": serializer.errors,
                        },
                        status.HTTP_400_BAD_REQUEST,
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

                if not is_draft:
                    current_phase = ProjectPhaseService.get_current(
                        project, ProjectPhaseInstance.Phase.APPLICATION
                    )
                    if (
                        current_phase
                        and current_phase.state == ProjectPhaseInstance.State.RETURNED
                    ):
                        ProjectPhaseService.start_new_attempt(
                            project,
                            ProjectPhaseInstance.Phase.APPLICATION,
                            created_by=request.user,
                        )
                    from apps.reviews.services import ReviewService

                    ReviewService.start_phase_review(
                        project,
                        ProjectPhaseInstance.Phase.APPLICATION,
                        created_by=request.user,
                    )

                project.advisors.all().delete()
                for idx, advisor_data in enumerate(advisors_data or []):
                    user_id = (
                        advisor_data.get("user")
                        or advisor_data.get("user_id")
                        or advisor_data.get("id")
                    )
                    job_number = advisor_data.get("job_number") or advisor_data.get(
                        "employee_id"
                    )
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
                            project=project, user_id=user_id, order=idx
                        )

                ProjectMember.objects.filter(project=project).exclude(
                    role=ProjectMember.MemberRole.LEADER
                ).delete()

                for member_data in members_data or []:
                    member_user_id = (
                        member_data.get("user")
                        or member_data.get("user_id")
                        or member_data.get("id")
                    )
                    student_id = member_data.get("student_id")
                    name = member_data.get("name")
                    if not member_user_id:
                        member_user_id = _get_or_create_user_by_identity(
                            employee_id=student_id, name=name, role=None
                        )

                    if not member_user_id or str(member_user_id) == str(user.id):
                        continue

                    ProjectMember.objects.get_or_create(
                        project=project,
                        user_id=member_user_id,
                        defaults={
                            "role": ProjectMember.MemberRole.MEMBER,
                            "contribution": member_data.get("contribution", ""),
                        },
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
            logger.exception("Project application update failed for project %s", pk)
            return (
                {"code": 500, "message": "操作失败，请稍后重试"},
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @staticmethod
    def withdraw_application(request, pk):
        user = request.user
        if not user.is_student:
            return (
                {"code": 403, "message": "只有学生可以撤回项目申报"},
                status.HTTP_403_FORBIDDEN,
            )

        try:
            project = Project.objects.get(pk=pk, leader=user)
        except Project.DoesNotExist:
            return (
                {"code": 404, "message": "项目不存在或无权限访问"},
                status.HTTP_404_NOT_FOUND,
            )

        current_batch = _get_current_batch()
        if not current_batch or project.batch_id != current_batch.id:
            return (
                {"code": 400, "message": "当前批次不允许操作该项目"},
                status.HTTP_400_BAD_REQUEST,
            )

        if project.status not in [
            Project.ProjectStatus.SUBMITTED,
            Project.ProjectStatus.TEACHER_AUDITING,
        ]:
            return (
                {"code": 400, "message": "当前状态不允许撤回"},
                status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            Review.objects.filter(
                project=project,
                review_type=Review.ReviewType.APPLICATION,
                status=Review.ReviewStatus.PENDING,
            ).delete()

            project.status = Project.ProjectStatus.DRAFT
            project.submitted_at = None
            project.save(update_fields=["status", "submitted_at", "updated_at"])

        return {"code": 200, "message": "撤回成功"}, status.HTTP_200_OK
