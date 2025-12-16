"""
项目管理相关视图（管理员）
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from .models import Project, ProjectAchievement
from .serializers import ProjectSerializer, ProjectAchievementSerializer


class ProjectManagementViewSet(viewsets.ModelViewSet):
    """
    项目管理视图集（管理员）
    """

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        获取项目列表，支持筛选
        """
        queryset = Project.objects.all().order_by("-created_at")

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
            queryset = queryset.filter(level=level)

        # 按类别筛选
        category = self.request.query_params.get("category", "")
        if category:
            queryset = queryset.filter(category=category)

        # 按状态筛选
        project_status = self.request.query_params.get("status", "")
        if project_status:
            queryset = queryset.filter(status=project_status)

        return queryset

    def list(self, request, *args, **kwargs):
        """
        获取项目列表（分页）
        """
        queryset = self.get_queryset()

        # 分页
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))

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

    def update(self, request, *args, **kwargs):
        """
        更新项目信息
        """
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({"code": 200, "message": "更新成功", "data": serializer.data})

    def destroy(self, request, *args, **kwargs):
        """
        删除项目
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"code": 200, "message": "删除成功"})

    @action(methods=["get"], detail=False, url_path="statistics")
    def get_statistics(self, request):
        """
        获取项目统计数据
        """
        total_projects = Project.objects.count()
        approved_projects = Project.objects.filter(
            status__in=["IN_PROGRESS", "COMPLETED"]
        ).count()
        pending_review = Project.objects.filter(
            status__in=["SUBMITTED", "MIDTERM_SUBMITTED", "CLOSURE_SUBMITTED"]
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

    @action(methods=["get"], detail=False, url_path="export")
    def export_data(self, request):
        """
        批量导出数据
        """
        try:
            from apps.utils.export import generate_excel
            from django.http import HttpResponse
            from datetime import datetime
        except ImportError:
            return Response(
                {"code": 500, "message": "Export module not found"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        queryset = self.get_queryset()
        
        # Support selecting specific IDs
        ids = request.query_params.get("ids", "")
        if ids:
            id_list = [int(i) for i in ids.split(",") if i.isdigit()]
            if id_list:
                queryset = queryset.filter(id__in=id_list)

        headers = {
            "project_no": "项目编号",
            "title": "项目名称",
            "level": "级别",
            "category": "类别",
            "status": "状态",
            "leader": "负责人",
            "college": "学院",
            "created_at": "创建时间",
        }
        
        data = []
        for p in queryset:
            data.append({
                "project_no": p.project_no,
                "title": p.title,
                "level": p.level.label if p.level else "",
                "category": p.category.label if p.category else "",
                "status": p.get_status_display(),
                "leader": p.leader.real_name if p.leader else "",
                "college": p.leader.college if p.leader else "",
                "created_at": p.created_at,
            })

        excel_file = generate_excel(data, headers)
        filename = f"projects_export_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
        
        response = HttpResponse(
            excel_file.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    @action(methods=["get"], detail=False, url_path="batch-download")
    def batch_download_attachments(self, request):
        """
        批量下载附件
        """
        try:
            from apps.utils.export import generate_zip
            from django.http import HttpResponse
            from datetime import datetime
        except ImportError:
             return Response(
                {"code": 500, "message": "Export module not found"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        queryset = self.get_queryset()

        # Support selecting specific IDs
        ids = request.query_params.get("ids", "")
        if ids:
            id_list = [int(i) for i in ids.split(",") if i.isdigit()]
            if id_list:
                queryset = queryset.filter(id__in=id_list)
        
        files_to_zip = []
        for p in queryset:
            # 申请书
            if p.proposal_file:
                try:
                    ext = p.proposal_file.name.split('.')[-1]
                    files_to_zip.append((p.proposal_file.path, f"{p.project_no}_{p.title}/申请书.{ext}"))
                except Exception:
                    pass

            # 结题报告
            if p.final_report:
                try:
                    files_to_zip.append((p.final_report.path, f"{p.project_no}_{p.title}/结题报告.pdf"))
                except Exception:
                    pass
            
            # 成果附件 (zip/rar/pdf)
            if p.achievement_file:
                try:
                    ext = p.achievement_file.name.split('.')[-1]
                    files_to_zip.append((p.achievement_file.path, f"{p.project_no}_{p.title}/成果附件.{ext}"))
                except Exception:
                    pass
            
            # 独立的成果附件 (ProjectAchievement)
            for ach in p.achievements.all():
                 if ach.attachment:
                     try:
                        ext = ach.attachment.name.split('.')[-1]
                        files_to_zip.append((ach.attachment.path, f"{p.project_no}_{p.title}/成果/{ach.title}.{ext}"))
                     except Exception:
                        pass
        
        if not files_to_zip:
             return Response({"code": 400, "message": "当前筛选条件下没有可下载的附件"}, status=status.HTTP_400_BAD_REQUEST)
             
        zip_file = generate_zip(files_to_zip)
        filename = f"attachments_{datetime.now().strftime('%Y%m%d%H%M%S')}.zip"
        
        response = HttpResponse(
            zip_file.read(),
            content_type="application/zip",
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response


class AchievementManagementViewSet(viewsets.ModelViewSet):
    """
    成果管理视图集（管理员）
    """
    queryset = ProjectAchievement.objects.all()
    serializer_class = ProjectAchievementSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = ProjectAchievement.objects.all().order_by("-created_at")
        
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
        
        page = self.paginate_queryset(queryset)
        if page is not None:
             serializer = self.get_serializer(page, many=True)
             return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

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
