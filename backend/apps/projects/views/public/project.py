"""
项目视图
"""

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ...models import Project, ProjectMember
from ...serializers import (
    ProjectSerializer,
    ProjectListSerializer,
)
from apps.projects.models import ProjectPhaseInstance
from apps.reviews.models import Review

from ..mixins import (
    ProjectAchievementsMixin,
    ProjectClosureMixin,
    ProjectCoreActionsMixin,
    ProjectLevel2ExportMixin,
    ProjectMembersMixin,
    ProjectMidtermMixin,
    ProjectProgressMixin,
    ProjectRankingMixin,
    ProjectSelfMixin,
    ProjectWorkflowMixin,
)


class ProjectViewSet(
    ProjectWorkflowMixin,
    ProjectLevel2ExportMixin,
    ProjectCoreActionsMixin,
    ProjectMembersMixin,
    ProjectProgressMixin,
    ProjectMidtermMixin,
    ProjectClosureMixin,
    ProjectAchievementsMixin,
    ProjectRankingMixin,
    ProjectSelfMixin,
    viewsets.ModelViewSet,
):
    """
    项目管理视图集
    """

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["status", "level", "leader__college", "leader", "batch", "year"]
    search_fields = ["project_no", "title", "advisors__user__real_name"]
    ordering_fields = ["created_at", "updated_at", "submitted_at"]

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

        # 学生只能看到自己参与的项目
        if user.is_student:
            queryset = queryset.filter(Q(leader=user) | Q(members=user)).distinct()
        elif (
            teacher_scope
            and str(teacher_scope).lower() in ("true", "1", "yes")
            and user.is_teacher
        ):
            queryset = queryset.filter(
                Q(advisors__user=user) | Q(reviews__reviewer=user)
            ).distinct()
        # 非校级管理员只能看到自己学院的项目
        elif user.is_admin and not user.is_level1_admin:
            queryset = queryset.filter(leader__college=user.college)
        # 一级管理员可以看到所有项目
        elif user.is_level1_admin:
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

        exclude_review_type = self.request.query_params.get("exclude_assigned_review_type")
        exclude_review_level = self.request.query_params.get("exclude_assigned_review_level")
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
            if exclude_review_level:
                assigned_reviews = assigned_reviews.filter(review_level=exclude_review_level)
            queryset = queryset.annotate(_has_assigned=Exists(assigned_reviews)).filter(_has_assigned=False)

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
