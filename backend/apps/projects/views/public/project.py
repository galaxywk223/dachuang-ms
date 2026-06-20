"""
项目视图
"""

from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ...models import Project, ProjectMember
from ...serializers import (
    ProjectSerializer,
    ProjectListSerializer,
)
from apps.projects.models import ProjectPhaseInstance
from apps.reviews.models import Review
from apps.system_settings.models import ProjectBatch
from apps.system_settings.services import SystemSettingService
from apps.utils.downloads import file_field_download_response
from apps.utils.pagination import optional_positive_int

from ..mixins import (
    ProjectAchievementsMixin,
    ProjectClosureMixin,
    ProjectCoreActionsMixin,
    ProjectLevel2ExportMixin,
    ProjectMembersMixin,
    ProjectMidtermMixin,
    ProjectSelfMixin,
    ProjectWorkflowMixin,
)

PROJECT_DOWNLOAD_FIELDS = {
    "proposal_file",
    "attachment_file",
    "mid_term_report",
    "final_report",
    "achievement_file",
}

PUBLIC_PROJECT_UPDATE_FORBIDDEN_FIELDS = {
    "approved_budget",
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


def _has_school_admin_scope(user):
    return user.is_school_admin or user.is_level1_admin


class ProjectViewSet(
    ProjectWorkflowMixin,
    ProjectLevel2ExportMixin,
    ProjectCoreActionsMixin,
    ProjectMembersMixin,
    ProjectMidtermMixin,
    ProjectClosureMixin,
    ProjectAchievementsMixin,
    ProjectSelfMixin,
    viewsets.ModelViewSet,
):
    """
    项目管理视图集
    """

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["status", "leader__college"]
    search_fields = ["project_no", "title", "advisors__user__real_name"]
    ordering_fields = ["created_at", "updated_at", "submitted_at"]

    def _ensure_user_can_write_project(self, project):
        """
        项目本体写操作仅允许负责人或管理员执行。

        备注：经费管理在 ProjectExpenditureViewSet 单独放行。
        """
        user = self.request.user
        if getattr(user, "is_admin", False):
            return None
        if project.leader_id == user.id:
            return None
        return Response(
            {"code": 403, "message": "只有项目负责人或管理员可以操作该项目"},
            status=status.HTTP_403_FORBIDDEN,
        )

    def _ensure_current_batch_write(self, project):
        current_batch = SystemSettingService.get_current_batch()
        if current_batch and project.batch_id == current_batch.id:
            return None
        return Response(
            {"code": 400, "message": "当前批次不允许操作该项目"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def _sanitize_public_project_update_data(self, request):
        data = request.data.copy()
        for field in PUBLIC_PROJECT_UPDATE_FORBIDDEN_FIELDS:
            data.pop(field, None)
        return data

    def _perform_public_project_update(self, request, project, partial):
        serializer = self.get_serializer(
            project,
            data=self._sanitize_public_project_update_data(request),
            partial=partial,
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(project, "_prefetched_objects_cache", None):
            project._prefetched_objects_cache = {}

        return Response(serializer.data)

    def get_serializer_class(self):
        if self.action == "list":
            return ProjectListSerializer
        return ProjectSerializer

    def get_queryset(self):
        """
        根据用户角色过滤项目
        """
        from django.db.models import Q, OuterRef, Subquery, Exists

        user = self.request.user
        queryset = super().get_queryset()
        teacher_scope = self.request.query_params.get("teacher_scope")

        include_archived = self.request.query_params.get("include_archived")
        history_batch_id = self.request.query_params.get("history_batch_id")

        if history_batch_id:
            parsed_batch_id = optional_positive_int(history_batch_id)
            if parsed_batch_id is None:
                return queryset.none()
            batch = ProjectBatch.objects.filter(
                id=parsed_batch_id,
                status=ProjectBatch.STATUS_ARCHIVED,
                is_deleted=False,
            ).first()
            if not batch:
                return queryset.none()
            queryset = queryset.filter(batch=batch)
        elif include_archived and str(include_archived).lower() in ("true", "1", "yes"):
            # If include_archived is True, do not filter by batch (show all non-deleted)
            queryset = queryset.filter(batch__is_deleted=False)
        else:
            current_batch = SystemSettingService.get_current_batch()
            if not current_batch:
                return queryset.none()
            queryset = queryset.filter(batch=current_batch, batch__is_deleted=False)

        # 学生只能看到自己参与的项目
        if user.is_student:
            queryset = queryset.filter(Q(leader=user) | Q(members=user)).distinct()
        elif (
            teacher_scope
            and str(teacher_scope).lower() in ("true", "1", "yes")
            and (user.is_teacher or user.is_admin)
        ):
            queryset = queryset.filter(Q(advisors__user=user)).distinct()
        # 非校级管理员只能看到自己学院的项目
        elif user.is_admin and not _has_school_admin_scope(user):
            queryset = queryset.filter(leader__college=user.college)
        # 一级管理员可以看到所有项目
        elif _has_school_admin_scope(user):
            pass
        # 指导教师只能看到自己指导的项目
        elif user.is_teacher:
            queryset = queryset.filter(
                Q(advisors__user=user) | Q(reviews__reviewer=user)
            ).distinct()
        elif user.is_expert:
            queryset = queryset.none()
        else:
            queryset = queryset.none()

        status_in = self.request.query_params.get("status_in")
        if status_in:
            status_list = [s.strip() for s in status_in.split(",") if s.strip()]
            queryset = queryset.filter(status__in=status_list)

        exclude_review_type = self.request.query_params.get(
            "exclude_assigned_review_type"
        )
        exclude_role = self.request.query_params.get("exclude_assigned_role")
        if exclude_review_type:
            current_phase_qs = ProjectPhaseInstance.objects.filter(
                project_id=OuterRef("pk"),
                phase=exclude_review_type,
            ).order_by("-attempt_no", "-id")
            queryset = queryset.annotate(
                _current_phase_instance_id=Subquery(current_phase_qs.values("id")[:1])
            )
            assigned_reviews = Review.objects.filter(
                project_id=OuterRef("pk"),
                review_type=exclude_review_type,
                reviewer__isnull=False,
                phase_instance_id=OuterRef("_current_phase_instance_id"),
            )
            if exclude_role:
                assigned_reviews = assigned_reviews.filter(
                    workflow_node__role_fk__code=exclude_role
                )
            queryset = queryset.annotate(_has_assigned=Exists(assigned_reviews)).filter(
                _has_assigned=False
            )

        phase = self.request.query_params.get("phase")
        phase_step = self.request.query_params.get("phase_step")
        phase_state = self.request.query_params.get("phase_state")
        if phase:
            current_phase_qs = ProjectPhaseInstance.objects.filter(
                project_id=OuterRef("pk"),
                phase=phase,
            ).order_by("-attempt_no", "-id")
            queryset = queryset.annotate(
                _phase_step=Subquery(current_phase_qs.values("step")[:1]),
                _phase_state=Subquery(current_phase_qs.values("state")[:1]),
            )
            if phase_step:
                queryset = queryset.filter(_phase_step=phase_step)
            if phase_state:
                queryset = queryset.filter(_phase_state=phase_state)

        level = self.request.query_params.get("level")
        if level:
            parsed_level = optional_positive_int(level)
            if parsed_level is None:
                return queryset.none()
            queryset = queryset.filter(level_id=parsed_level)

        leader = self.request.query_params.get("leader")
        if leader:
            parsed_leader = optional_positive_int(leader)
            if parsed_leader is None:
                return queryset.none()
            queryset = queryset.filter(leader_id=parsed_leader)

        year = self.request.query_params.get("year")
        if year:
            parsed_year = optional_positive_int(year)
            if parsed_year is None:
                return queryset.none()
            queryset = queryset.filter(year=parsed_year)

        return queryset

    def list(self, request, *args, **kwargs):
        """
        统一返回结构，方便前端处理
        """
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return Response(
                {
                    "code": 200,
                    "message": "获取成功",
                    "data": {
                        "results": serializer.data,
                        "count": self.paginator.page.paginator.count,
                    },
                }
            )

        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "code": 200,
                "message": "获取成功",
                "data": {"results": serializer.data, "count": len(serializer.data)},
            }
        )

    def retrieve(self, request, *args, **kwargs):
        """
        项目详情统一返回结构
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"code": 200, "message": "获取成功", "data": serializer.data})

    @action(
        detail=True,
        methods=["get"],
        url_path=r"files/(?P<field_name>[^/.]+)/download",
    )
    def download_file(self, request, pk=None, field_name=None):
        project = self.get_object()
        if field_name not in PROJECT_DOWNLOAD_FIELDS:
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

    def update(self, request, *args, **kwargs):
        project = self.get_object()
        denied = self._ensure_current_batch_write(project)
        if denied is not None:
            return denied
        denied = self._ensure_user_can_write_project(project)
        if denied is not None:
            return denied
        return self._perform_public_project_update(request, project, partial=False)

    def partial_update(self, request, *args, **kwargs):
        project = self.get_object()
        denied = self._ensure_current_batch_write(project)
        if denied is not None:
            return denied
        denied = self._ensure_user_can_write_project(project)
        if denied is not None:
            return denied
        return self._perform_public_project_update(request, project, partial=True)

    def destroy(self, request, *args, **kwargs):
        project = self.get_object()
        denied = self._ensure_current_batch_write(project)
        if denied is not None:
            return denied
        denied = self._ensure_user_can_write_project(project)
        if denied is not None:
            return denied
        if project.status != Project.ProjectStatus.DRAFT:
            return Response(
                {"code": 400, "message": "只有草稿项目可以直接删除"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return Response(
            {"code": 405, "message": "请通过项目申报接口创建项目"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def perform_create(self, serializer):
        """
        创建项目时设置负责人为当前用户
        """
        project = serializer.save(leader=self.request.user)
        # 自动将负责人添加为项目成员
        ProjectMember.objects.create(
            project=project,
            user=self.request.user,
            role=ProjectMember.MemberRole.LEADER,
        )
