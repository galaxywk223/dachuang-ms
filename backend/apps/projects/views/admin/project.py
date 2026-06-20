"""
项目管理相关视图（管理员）
"""

import csv
import io
import json
from datetime import timedelta

from django.db.models import Q, Count, Sum, Avg
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ...models import Project
from apps.system_settings.services import SystemSettingService
from apps.operations.models import AsyncTaskRecord
from apps.operations.services import DataCenterService, OperationLogService
from apps.reviews.models import Review
from apps.users.permissions import IsAdmin
from apps.utils.pagination import (
    optional_positive_int,
    positive_int_list,
    positive_int_query,
)
from apps.utils.downloads import file_field_download_response
from ...serializers import ProjectSerializer
from ...models import ProjectPhaseInstance
from ...services import PublicationService
from ..mixins.project_batch_mixin import ProjectBatchMixin
from ..mixins.project_admin_export_data_mixin import ProjectAdminExportDataMixin
from ..mixins.project_admin_export_attachments_mixin import (
    ProjectAdminExportAttachmentsMixin,
)
from ..mixins.project_admin_export_documents_mixin import (
    ProjectAdminExportDocumentsMixin,
)
from ..mixins.project_admin_export_certificates_mixin import (
    ProjectAdminExportCertificatesMixin,
)

PROJECT_ADMIN_DOWNLOAD_FIELDS = {
    "proposal_file",
    "attachment_file",
    "mid_term_report",
    "final_report",
    "achievement_file",
}

ADMIN_PROJECT_UPDATE_FORBIDDEN_FIELDS = {
    "batch",
    "final_budget",
    "final_level",
    "is_deleted",
    "leader",
    "project_no",
    "publish_status",
    "published_at",
    "published_by",
    "recommendation_comment",
    "recommendation_rank",
    "recommended_budget",
    "recommended_level",
    "status",
    "submitted_at",
}

COLLEGE_ADMIN_PROJECT_UPDATE_FORBIDDEN_FIELDS = ADMIN_PROJECT_UPDATE_FORBIDDEN_FIELDS | {
    "approved_budget",
}


def _has_school_admin_scope(user):
    return user.is_school_admin or user.is_level1_admin


def _parse_project_people_payload(value):
    if value is None:
        return None
    if value == "":
        return []
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError as exc:
            raise ValueError("人员数据格式错误") from exc
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise ValueError("人员数据格式错误")
    return value


class ProjectManagementViewSet(
    ProjectAdminExportDataMixin,
    ProjectAdminExportAttachmentsMixin,
    ProjectAdminExportDocumentsMixin,
    ProjectAdminExportCertificatesMixin,
    ProjectBatchMixin,
    viewsets.ModelViewSet,
):
    """
    项目管理视图集（管理员）
    """

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def _sanitize_admin_project_update_data(self, request):
        data = request.data.copy()
        forbidden_fields = (
            ADMIN_PROJECT_UPDATE_FORBIDDEN_FIELDS
            if _has_school_admin_scope(request.user)
            else COLLEGE_ADMIN_PROJECT_UPDATE_FORBIDDEN_FIELDS
        )
        for field in forbidden_fields:
            data.pop(field, None)
        return data

    def get_queryset(self):
        """
        获取项目列表，支持筛选
        """
        queryset = Project.objects.all().order_by("-created_at")

        current_batch = SystemSettingService.get_current_batch()
        include_archived = self.request.query_params.get("include_archived")
        include_archived = str(include_archived).lower() in ("true", "1", "yes")
        batch_id = self.request.query_params.get("batch_id", "")
        if batch_id:
            parsed_batch_id = optional_positive_int(batch_id)
            if parsed_batch_id is None:
                return Project.objects.none()
            queryset = queryset.filter(batch_id=parsed_batch_id)
        elif not include_archived and self.action != "download_file":
            if not current_batch:
                return Project.objects.none()
            queryset = queryset.filter(batch=current_batch)
        queryset = queryset.filter(batch__is_deleted=False)

        # 权限控制：非校级管理员只能看到本学院的项目
        user = self.request.user
        if user.is_admin:
            if not _has_school_admin_scope(user):
                queryset = queryset.filter(leader__college=user.college)
        else:
            return Project.objects.none()

        # 搜索
        search = self.request.query_params.get("search", "")
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(project_no__icontains=search)
                | Q(leader__real_name__icontains=search)
            )

        # 按级别筛选
        level = self.request.query_params.get("level", "")
        if level:
            parsed_level = optional_positive_int(level)
            if parsed_level is None:
                return Project.objects.none()
            queryset = queryset.filter(level_id=parsed_level)

        # 按类别筛选
        category = self.request.query_params.get("category", "")
        if category:
            parsed_category = optional_positive_int(category)
            if parsed_category is None:
                return Project.objects.none()
            queryset = queryset.filter(category_id=parsed_category)

        # 按状态筛选
        project_status = self.request.query_params.get("status", "")
        if project_status:
            queryset = queryset.filter(status=project_status)

        year = self.request.query_params.get("year", "")
        if year:
            parsed_year = optional_positive_int(year)
            if parsed_year is None:
                return Project.objects.none()
            queryset = queryset.filter(year=parsed_year)

        return queryset

    def list(self, request, *args, **kwargs):
        """
        获取项目列表（分页）
        """
        queryset = self.get_queryset()

        # 分页
        page = positive_int_query(request.query_params, "page", 1)
        page_size = positive_int_query(request.query_params, "page_size", 10, 100)

        total = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size
        projects = queryset[start:end]

        serializer = self.get_serializer(projects, many=True)

        return Response(
            {
                "code": 200,
                "message": "获取成功",
                "data": {
                    "results": serializer.data,
                    "total": total,
                    "page": page,
                    "page_size": page_size,
                },
            }
        )

    def retrieve(self, request, *args, **kwargs):
        """
        获取项目详情
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"code": 200, "message": "获取成功", "data": serializer.data})

    def create(self, request, *args, **kwargs):
        return Response(
            {"code": 405, "message": "请通过项目申报或历史项目导入接口创建项目"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    @action(
        methods=["get"],
        detail=True,
        url_path=r"files/(?P<field_name>[^/.]+)/download",
    )
    def download_file(self, request, pk=None, field_name=None):
        project = self.get_object()
        if field_name not in PROJECT_ADMIN_DOWNLOAD_FIELDS:
            return Response(
                {"code": 404, "message": "项目文件类型不存在"},
                status=status.HTTP_404_NOT_FOUND,
            )
        file_field = getattr(project, field_name, None)
        if not file_field:
            return Response(
                {"code": 404, "message": "项目文件不存在"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return file_field_download_response(
            file_field,
            missing_message="项目文件不存在",
        )

    @action(methods=["get"], detail=True, url_path="timeline")
    def timeline(self, request, pk=None):
        """
        获取项目流程时间线。
        """
        project = self.get_object()
        events = [
            {
                "type": "created",
                "title": "项目创建",
                "time": project.created_at,
                "description": project.title,
            }
        ]
        if project.submitted_at:
            events.append(
                {
                    "type": "submitted",
                    "title": "项目提交",
                    "time": project.submitted_at,
                    "description": "项目进入立项审核",
                }
            )
        for phase in ProjectPhaseInstance.objects.filter(project=project).order_by(
            "created_at"
        ):
            events.append(
                {
                    "type": "phase",
                    "title": f"{phase.get_phase_display()}流程",
                    "time": phase.created_at,
                    "description": f"{phase.step or '流程节点'} - {phase.get_state_display()}",
                }
            )
        for review in Review.objects.filter(project=project).order_by("created_at"):
            events.append(
                {
                    "type": "review",
                    "title": review.get_review_type_display(),
                    "time": review.reviewed_at or review.created_at,
                    "description": review.comments or review.get_status_display(),
                    "status": review.status,
                    "reviewer": review.reviewer.real_name if review.reviewer else "",
                }
            )
        if project.published_at:
            events.append(
                {
                    "type": "published",
                    "title": "立项结果发布",
                    "time": project.published_at,
                    "description": project.get_publish_status_display(),
                }
            )
        events.sort(key=lambda item: item["time"] or project.created_at)
        return Response({"code": 200, "message": "获取成功", "data": events})

    def update(self, request, *args, **kwargs):
        """
        更新项目信息
        """
        from django.db import transaction
        from ...models import ProjectAdvisor, ProjectMember
        from apps.users.models import User
        import logging

        logger = logging.getLogger(__name__)

        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        # Extract nested data
        advisors_data = request.data.get("advisors")
        members_data = request.data.get("members")
        try:
            advisors_data = _parse_project_people_payload(advisors_data)
            members_data = _parse_project_people_payload(members_data)
        except ValueError as exc:
            return Response(
                {"code": 400, "message": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            serializer = self.get_serializer(
                instance,
                data=self._sanitize_admin_project_update_data(request),
                partial=partial,
            )
            if not serializer.is_valid():
                # Debug: 打印本次更新请求的数据与校验错误，方便前后端联调
                logger.warning(
                    "Project admin manage update validation failed: project_id=%s user_id=%s partial=%s data=%s errors=%s",
                    instance.id,
                    getattr(request.user, "id", None),
                    partial,
                    dict(request.data),
                    serializer.errors,
                )
                return Response(
                    {"code": 400, "message": "数据验证失败", "errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            self.perform_update(serializer)

            # Update Advisors if provided
            if advisors_data is not None:
                # Clear existing advisors
                instance.advisors.all().delete()

                for idx, advisor_data in enumerate(advisors_data):
                    user_id = (
                        advisor_data.get("user")
                        or advisor_data.get("user_id")
                        or advisor_data.get("id")
                    )
                    job_number = advisor_data.get("job_number") or advisor_data.get(
                        "employee_id"
                    )

                    # Try to find user if no ID
                    if not user_id and job_number:
                        u = User.objects.filter(employee_id=job_number).first()
                        if u:
                            user_id = u.id

                    if user_id:
                        ProjectAdvisor.objects.create(
                            project=instance,
                            user_id=user_id,
                            order=idx,
                        )

            # Update Members if provided
            if members_data is not None:
                # Clear existing members (except leader)
                ProjectMember.objects.filter(project=instance).exclude(
                    role=ProjectMember.MemberRole.LEADER
                ).delete()

                for idx, member_data in enumerate(members_data):
                    user_id = member_data.get("user") or member_data.get("user_id")
                    student_id = member_data.get("student_id") or member_data.get(
                        "employee_id"
                    )

                    if not user_id and student_id:
                        u = User.objects.filter(employee_id=student_id).first()
                        if u:
                            user_id = u.id

                    if user_id:
                        ProjectMember.objects.create(
                            project=instance,
                            user_id=user_id,
                            role=ProjectMember.MemberRole.MEMBER,
                            contribution=member_data.get("contribution", ""),
                        )

        return Response({"code": 200, "message": "更新成功", "data": serializer.data})

    def destroy(self, request, *args, **kwargs):
        """
        删除项目
        """
        instance = self.get_object()
        if instance.status != Project.ProjectStatus.DRAFT:
            return Response(
                {"code": 400, "message": "只有草稿项目可以直接删除"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        self.perform_destroy(instance)
        return Response({"code": 200, "message": "删除成功"})

    @action(methods=["get"], detail=False, url_path="statistics")
    def get_statistics(self, request):
        """
        获取项目统计数据
        """
        # 基础查询集（已包含权限过滤）
        base_queryset = self.get_queryset()

        total_projects = base_queryset.count()
        approved_projects = base_queryset.filter(
            status__in=["IN_PROGRESS", "COMPLETED"]
        ).count()
        pending_review = base_queryset.filter(
            status__in=[
                "SUBMITTED",
                "TEACHER_AUDITING",
                "COLLEGE_AUDITING",
                "LEVEL1_AUDITING",
                "MID_TERM_SUBMITTED",
                "MID_TERM_REVIEWING",
                "CLOSURE_SUBMITTED",
                "CLOSURE_LEVEL2_REVIEWING",
                "CLOSURE_LEVEL1_REVIEWING",
            ]
        ).count()

        return Response(
            {
                "code": 200,
                "message": "获取成功",
                "data": {
                    "total_projects": total_projects,
                    "approved_projects": approved_projects,
                    "pending_review": pending_review,
                },
            }
        )

    @action(methods=["get"], detail=False, url_path="dashboard")
    def dashboard(self, request):
        """
        管理驾驶舱：指标、阶段漏斗、学院对比、风险和经费概览。
        """
        queryset = self.get_queryset()
        now = timezone.now()

        submitted_statuses = [
            Project.ProjectStatus.SUBMITTED,
            Project.ProjectStatus.TEACHER_AUDITING,
            Project.ProjectStatus.COLLEGE_AUDITING,
            Project.ProjectStatus.LEVEL1_AUDITING,
        ]
        published_statuses = [Project.PublishStatus.PUBLISHED]
        completed_statuses = [
            Project.ProjectStatus.CLOSED,
            Project.ProjectStatus.COMPLETED,
        ]
        returned_statuses = [
            Project.ProjectStatus.APPLICATION_RETURNED,
            Project.ProjectStatus.MID_TERM_RETURNED,
            Project.ProjectStatus.CLOSURE_RETURNED,
        ]
        pending_statuses = submitted_statuses + [
            Project.ProjectStatus.MID_TERM_SUBMITTED,
            Project.ProjectStatus.MID_TERM_REVIEWING,
            Project.ProjectStatus.CLOSURE_SUBMITTED,
            Project.ProjectStatus.CLOSURE_LEVEL2_REVIEWING,
            Project.ProjectStatus.CLOSURE_LEVEL1_REVIEWING,
        ]

        budget_stats = queryset.aggregate(
            approved=Sum("approved_budget"),
            final=Sum("final_budget"),
            expenditure=Sum("expenditures__amount"),
            avg_budget=Avg("approved_budget"),
        )

        metrics = {
            "applications": queryset.exclude(status=Project.ProjectStatus.DRAFT).count(),
            "approved": queryset.filter(status=Project.ProjectStatus.IN_PROGRESS).count(),
            "returned": queryset.filter(status__in=returned_statuses).count(),
            "pending": queryset.filter(status__in=pending_statuses).count(),
            "published": queryset.filter(publish_status__in=published_statuses).count(),
            "completed": queryset.filter(status__in=completed_statuses).count(),
            "achievements": queryset.aggregate(total=Count("achievements"))["total"] or 0,
            "budget_used": float(budget_stats["expenditure"] or 0),
            "budget_approved": float(
                budget_stats["final"] or budget_stats["approved"] or 0
            ),
            "avg_budget": float(budget_stats["avg_budget"] or 0),
        }

        stage_funnel = [
            {"stage": "申报提交", "count": metrics["applications"]},
            {
                "stage": "立项审核",
                "count": queryset.filter(status__in=submitted_statuses).count(),
            },
            {"stage": "结果发布", "count": metrics["published"]},
            {
                "stage": "中期阶段",
                "count": queryset.filter(
                    status__in=[
                        Project.ProjectStatus.MID_TERM_DRAFT,
                        Project.ProjectStatus.MID_TERM_SUBMITTED,
                        Project.ProjectStatus.MID_TERM_REVIEWING,
                        Project.ProjectStatus.READY_FOR_CLOSURE,
                    ]
                ).count(),
            },
            {"stage": "结题归档", "count": metrics["completed"]},
        ]

        college_compare = list(
            queryset.values("leader__college")
            .annotate(
                total=Count("id"),
                published=Count("id", filter=Q(publish_status=Project.PublishStatus.PUBLISHED)),
                completed=Count("id", filter=Q(status__in=completed_statuses)),
            )
            .order_by("-total")[:12]
        )

        status_distribution = list(
            queryset.values("status").annotate(count=Count("id")).order_by("-count")
        )

        risks = []
        long_pending = queryset.filter(
            status__in=pending_statuses,
            updated_at__lt=now - timedelta(days=7),
        )[:10]
        for project in long_pending:
            risks.append(
                {
                    "type": "LONG_PENDING",
                    "level": "warning",
                    "project_id": project.id,
                    "project_title": project.title,
                    "message": "项目超过7天未处理",
                }
            )

        missing_materials = queryset.filter(
            status__in=[
                Project.ProjectStatus.SUBMITTED,
                Project.ProjectStatus.TEACHER_AUDITING,
                Project.ProjectStatus.COLLEGE_AUDITING,
            ],
            proposal_file="",
        )[:10]
        for project in missing_materials:
            risks.append(
                {
                    "type": "MISSING_MATERIAL",
                    "level": "danger",
                    "project_id": project.id,
                    "project_title": project.title,
                    "message": "项目缺少申报材料",
                }
            )

        return Response(
            {
                "code": 200,
                "message": "获取成功",
                "data": {
                    "metrics": metrics,
                    "stage_funnel": stage_funnel,
                    "college_compare": college_compare,
                    "status_distribution": status_distribution,
                    "risks": risks[:20],
                },
            }
        )

    @action(methods=["get"], detail=False, url_path="publication-center")
    def publication_center(self, request):
        """
        获取立项发布中心项目列表。
        """
        queryset = PublicationService.get_publication_queryset(request.user)

        search = request.query_params.get("search", "")
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(project_no__icontains=search)
                | Q(leader__real_name__icontains=search)
            )
        publish_status = request.query_params.get("publish_status", "")
        if publish_status:
            queryset = queryset.filter(publish_status=publish_status)
        college = request.query_params.get("college", "")
        if college:
            queryset = queryset.filter(leader__college=college)

        queryset = queryset.order_by(
            "recommendation_rank", "leader__college", "-updated_at"
        )
        page = positive_int_query(request.query_params, "page", 1)
        page_size = positive_int_query(request.query_params, "page_size", 10, 100)
        total = queryset.count()
        projects = queryset[(page - 1) * page_size : page * page_size]
        serializer = ProjectSerializer(projects, many=True, context={"request": request})

        return Response(
            {
                "code": 200,
                "message": "获取成功",
                "data": {
                    "results": serializer.data,
                    "total": total,
                    "page": page,
                    "page_size": page_size,
                },
            }
        )

    @action(methods=["post"], detail=False, url_path="publication/recommend")
    def save_publication_recommendations(self, request):
        """
        保存学院推荐排序、推荐级别、推荐经费和推荐意见。
        """
        items = request.data.get("items", [])
        if not isinstance(items, list) or not items:
            return Response(
                {"code": 400, "message": "请提供推荐项目列表"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            updated = PublicationService.save_recommendations(request.user, items)
        except ValueError as exc:
            return Response(
                {"code": 400, "message": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {"code": 200, "message": "保存成功", "data": {"updated": updated}}
        )

    @action(methods=["post"], detail=False, url_path="publication/confirm")
    def confirm_publication_results(self, request):
        """
        校级管理员确认最终级别和最终经费。
        """
        items = request.data.get("items", [])
        if not isinstance(items, list) or not items:
            return Response(
                {"code": 400, "message": "请提供确认项目列表"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            updated = PublicationService.confirm_projects(request.user, items)
        except PermissionError as exc:
            return Response(
                {"code": 403, "message": str(exc)},
                status=status.HTTP_403_FORBIDDEN,
            )
        except ValueError as exc:
            return Response(
                {"code": 400, "message": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {"code": 200, "message": "确认成功", "data": {"updated": updated}}
        )

    @action(methods=["post"], detail=False, url_path="publication/publish")
    def publish_establishment_results(self, request):
        """
        校级管理员批量发布立项结果。
        """
        project_ids = request.data.get("project_ids", [])
        if not isinstance(project_ids, list) or not project_ids:
            return Response(
                {"code": 400, "message": "请提供项目ID列表"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        project_ids = positive_int_list(project_ids)
        if not project_ids:
            return Response(
                {"code": 400, "message": "项目ID列表不合法"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            published = PublicationService.publish_projects(request.user, project_ids)
        except PermissionError as exc:
            return Response(
                {"code": 403, "message": str(exc)},
                status=status.HTTP_403_FORBIDDEN,
            )
        return Response(
            {"code": 200, "message": "发布成功", "data": {"published": published}}
        )

    def _publication_export_bytes(self, request):
        queryset = PublicationService.get_publication_queryset(request.user).filter(
            publish_status=Project.PublishStatus.PUBLISHED
        )
        stream = io.StringIO()
        writer = csv.writer(stream)
        writer.writerow(
            ["项目编号", "项目名称", "负责人", "学院", "最终级别", "最终经费", "发布时间"]
        )
        for project in queryset.order_by("leader__college", "recommendation_rank", "id"):
            writer.writerow(
                [
                    project.project_no,
                    project.title,
                    project.leader.real_name if project.leader else "",
                    project.leader.college if project.leader else "",
                    project.final_level.label
                    if project.final_level
                    else project.level.label
                    if project.level
                    else "",
                    project.final_budget or project.approved_budget or "",
                    project.published_at.strftime("%Y-%m-%d %H:%M")
                    if project.published_at
                    else "",
                ]
            )
        return stream.getvalue().encode("utf-8-sig"), queryset.count()

    @action(methods=["get"], detail=False, url_path="publication/export")
    def export_publication_results(self, request):
        """
        导出立项公示结果。
        """
        content, _ = self._publication_export_bytes(request)
        response = HttpResponse(content, content_type="text/csv; charset=utf-8-sig")
        response["Content-Disposition"] = 'attachment; filename="publication_results.csv"'
        return response

    @action(methods=["post"], detail=False, url_path="publication/export-task")
    def export_publication_results_task(self, request):
        """
        将立项公示结果导出为后台任务。
        """
        content, total = self._publication_export_bytes(request)
        filename = f"publication_results_{timezone.now().strftime('%Y%m%d%H%M%S')}.csv"
        task = DataCenterService.create_completed_file_task(
            request.user,
            "立项公示结果导出",
            AsyncTaskRecord.TaskType.EXPORT,
            filename,
            content,
            result={"total": total},
        )
        OperationLogService.log(
            operator=request.user,
            module="立项发布",
            action="生成公示导出任务",
            target_type="AsyncTaskRecord",
            target_id=task.id,
            target_name=task.title,
            request=request,
            detail={"total": total},
        )
        return Response(
            {
                "code": 200,
                "message": "导出任务已生成",
                "data": {
                    "id": task.id,
                    "title": task.title,
                    "status": task.status,
                    "progress": task.progress,
                    "result": task.result,
                    "result_file_url": f"/api/v1/operations/tasks/{task.id}/download/"
                    if task.result_file
                    else "",
                },
            }
        )
