"""
项目成果管理相关视图（管理员）
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from ...models import Project, ProjectAchievement
from apps.system_settings.services import SystemSettingService
from ...serializers import ProjectAchievementSerializer

class AchievementManagementViewSet(viewsets.ModelViewSet):
    """
    成果管理视图集（管理员）
    """
    queryset = ProjectAchievement.objects.all()
    serializer_class = ProjectAchievementSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        current_batch = SystemSettingService.get_current_batch()
        if not current_batch:
            return ProjectAchievement.objects.none()
        queryset = (
            ProjectAchievement.objects.filter(project__batch=current_batch)
            .order_by("-created_at")
        )
        
        # 权限控制：非校级管理员只能看到本学院项目的成果
        user = self.request.user
        if user.is_admin and not user.is_level1_admin:
            queryset = queryset.filter(project__leader__college=user.college)

        # Search by project title or achievement title
        search = self.request.query_params.get("search", "")
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(project__title__icontains=search)
            )
            
        # Filter by year (project created year)
        year = self.request.query_params.get("year", "")
        if year and year.isdigit():
             queryset = queryset.filter(project__created_at__year=int(year))
             
        # Filter by college
        college = self.request.query_params.get("college", "")
        if college:
             queryset = queryset.filter(project__leader__college=college)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # 已有的成果数据
        achievements_data = list(self.get_serializer(queryset, many=True).data)

        # 补充：将已申请结题但尚无成果记录的项目也展示出来
        closure_statuses = [
            Project.ProjectStatus.CLOSURE_SUBMITTED,
            Project.ProjectStatus.CLOSURE_LEVEL2_REVIEWING,
            Project.ProjectStatus.CLOSURE_LEVEL2_APPROVED,
            Project.ProjectStatus.CLOSURE_LEVEL2_REJECTED,
            Project.ProjectStatus.CLOSURE_LEVEL1_REVIEWING,
            Project.ProjectStatus.CLOSURE_LEVEL1_APPROVED,
            Project.ProjectStatus.CLOSURE_LEVEL1_REJECTED,
            Project.ProjectStatus.CLOSED,
        ]

        current_batch = SystemSettingService.get_current_batch()
        if not current_batch:
            return Response(
                {"count": 0, "next": None, "previous": None, "results": []}
            )

        projects_qs = Project.objects.filter(
            status__in=closure_statuses, batch=current_batch
        )

        # 同步查询参数过滤
        search = request.query_params.get("search", "")
        if search:
            projects_qs = projects_qs.filter(
                Q(title__icontains=search) | Q(project_no__icontains=search)
            )
        year = request.query_params.get("year", "")
        if year and year.isdigit():
            projects_qs = projects_qs.filter(created_at__year=int(year))
        college = request.query_params.get("college", "")
        if college:
            projects_qs = projects_qs.filter(leader__college=college)

        # 去除已有成果的项目，避免重复
        project_ids_with_achievements = queryset.values_list("project_id", flat=True)
        projects_qs = projects_qs.exclude(id__in=project_ids_with_achievements)

        fallback_items = []
        for p in projects_qs.select_related("leader"):
            fallback_items.append(
                {
                    "id": f"project-{p.id}",
                    "project": p.id,
                    "project_no": p.project_no,
                    "project_title": p.title,
                    "leader": p.leader.id if p.leader else None,
                    "leader_name": p.leader.real_name if p.leader else "",
                    "college": p.leader.college if p.leader else "",
                    "achievement_type": None,
                    "achievement_type_display": "结题申请",
                    "title": p.title,
                    "description": p.description or "",
                    "publication_date": None,
                    "award_date": None,
                    "created_at": p.closure_applied_at or p.updated_at,
                    "updated_at": p.updated_at,
                }
            )

        combined = achievements_data + fallback_items
        combined_sorted = sorted(
            combined,
            key=lambda x: x.get("created_at") or x.get("updated_at") or "",
            reverse=True,
        )

        page = self.paginate_queryset(combined_sorted)
        if page is not None:
            return self.get_paginated_response(page)

        return Response(combined_sorted)

    @action(methods=["get"], detail=False, url_path="export")
    def export_data(self, request):
        try:
            from apps.utils.export import generate_excel
            from django.http import HttpResponse
            from datetime import datetime
        except ImportError:
            return Response(
                {"code": 500, "message": "Export module not found"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        queryset = self.filter_queryset(self.get_queryset())
        
        headers = {
            "project_no": "项目编号",
            "project_title": "项目名称",
            "leader": "负责人",
            "college": "学院",
            "type": "成果类型",
            "title": "成果名称",
            "description": "描述",
            "date": "发表/获奖日期",
        }
        
        data = []
        for ach in queryset:
            date_str = ""
            if ach.publication_date:
                date_str = str(ach.publication_date)
            elif ach.award_date:
                date_str = str(ach.award_date)

            data.append({
                "project_no": ach.project.project_no,
                "project_title": ach.project.title,
                "leader": ach.project.leader.real_name if ach.project.leader else "",
                "college": ach.project.leader.college if ach.project.leader else "",
                "type": ach.achievement_type.label if ach.achievement_type else "",
                "title": ach.title,
                "description": ach.description,
                "date": date_str,
            })

        excel_file = generate_excel(data, headers)
        filename = f"achievements_export_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
        
        response = HttpResponse(
            excel_file.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response
