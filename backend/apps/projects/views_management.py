"""
项目管理相关视图（管理员）
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from .models import (
    Project,
    ProjectAchievement,
    ProjectArchive,
    ProjectPushRecord,
    ProjectMember,
)
from .serializers import (
    ProjectSerializer,
    ProjectAchievementSerializer,
    ProjectArchiveSerializer,
    ProjectPushRecordSerializer,
)
from .certificates import render_certificate_html
from .services import DocumentService, ExternalPushService
import io
import zipfile
from django.http import HttpResponse


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

        # 权限控制：二级管理员只能看到本学院的项目
        user = self.request.user
        if user.is_level2_admin:
            queryset = queryset.filter(leader__college=user.college)
        elif not user.is_level1_admin:
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
        from django.db import transaction
        import json
        from .models import ProjectAdvisor, ProjectMember
        from apps.users.models import User
        import logging

        logger = logging.getLogger(__name__)

        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        
        # Extract nested data
        advisors_data = request.data.get("advisors")
        members_data = request.data.get("members")
        
        with transaction.atomic():
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
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
                if isinstance(advisors_data, str):
                    try:
                        advisors_data = json.loads(advisors_data)
                    except json.JSONDecodeError:
                        advisors_data = []
                
                # Clear existing advisors
                instance.advisors.all().delete()
                
                for idx, advisor_data in enumerate(advisors_data):
                    user_id = advisor_data.get("user") or advisor_data.get("user_id") or advisor_data.get("id")
                    job_number = advisor_data.get("job_number") or advisor_data.get("employee_id")
                    
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
                if isinstance(members_data, str):
                    try:
                        members_data = json.loads(members_data)
                    except json.JSONDecodeError:
                        members_data = []
                
                # Clear existing members (except leader)
                ProjectMember.objects.filter(project=instance).exclude(
                    role=ProjectMember.MemberRole.LEADER
                ).delete()
                
                for member_data in members_data:
                    user_id = member_data.get("user") or member_data.get("user_id") or member_data.get("id")
                    student_id = member_data.get("student_id")
                    
                    # Try to find user if no ID
                    if not user_id and student_id:
                        u = User.objects.filter(employee_id=student_id).first()
                        if u:
                            user_id = u.id
                            
                    if not user_id or (instance.leader and user_id == instance.leader.id):
                        continue

                    ProjectMember.objects.create(
                        project=instance,
                        user_id=user_id,
                        role=ProjectMember.MemberRole.MEMBER,
                        contribution=member_data.get("contribution", "")
                    )

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

        queryset = (
            self.get_queryset()
            .select_related("leader", "level", "category", "source")
            .prefetch_related("advisors__user", "projectmember_set__user", "achievements")
        )
        
        # Support selecting specific IDs
        ids = request.query_params.get("ids", "")
        if ids:
            id_list = [int(i) for i in ids.split(",") if i.isdigit()]
            if id_list:
                queryset = queryset.filter(id__in=id_list)

        def build_file_url(file_field):
            if not file_field:
                return ""
            try:
                url = file_field.url
                return request.build_absolute_uri(url)
            except Exception:
                return ""

        # Dictionary label maps (avoid heavy serializer work for export)
        from apps.dictionaries.models import DictionaryItem

        college_label_map = dict(
            DictionaryItem.objects.filter(dict_type__code="college").values_list(
                "value", "label"
            )
        )

        headers = {
            "project_no": "项目编号",
            "title": "项目名称",
            "description": "项目简介",
            "source_code": "项目来源(代码)",
            "source_label": "项目来源",
            "level_code": "项目级别(代码)",
            "level_label": "项目级别",
            "category_code": "项目类别(代码)",
            "category_label": "项目类别",
            "is_key_field": "重点领域项目",
            "key_domain_code": "重点领域代码",
            "self_funding": "项目自筹(元)",
            "category_description": "立项类别描述",
            "start_date": "开始日期",
            "end_date": "结束日期",
            "budget": "项目经费(元)",
            "approved_budget": "批准经费(元)",
            "research_content": "研究内容",
            "research_plan": "研究方案",
            "expected_results": "预期成果",
            "innovation_points": "创新点",
            "status_code": "状态(代码)",
            "status_display": "状态",
            "ranking": "项目排名",
            "leader_name": "负责人姓名",
            "leader_employee_id": "负责人学号/工号",
            "leader_phone": "负责人电话",
            "leader_email": "负责人邮箱",
            "leader_college_code": "学院(代码)",
            "leader_college": "学院",
            "leader_major": "专业(代码)",
            "leader_grade": "年级",
            "leader_class_name": "班级",
            "leader_department": "部门",
            "advisors": "指导教师",
            "members": "项目成员",
            "achievements_count": "成果数量",
            "proposal_file_name": "申报书文件名",
            "proposal_file_url": "申报书URL",
            "attachment_file_name": "附件文件名",
            "attachment_file_url": "附件URL",
            "final_report_url": "结题报告URL",
            "achievement_file_url": "成果材料URL",
            "created_at": "创建时间",
            "updated_at": "更新时间",
            "submitted_at": "提交时间",
            "closure_applied_at": "结题申请时间",
        }

        data = []
        for p in queryset:
            leader = p.leader

            advisors_text = []
            for idx, a in enumerate(p.advisors.all()):
                order = a.order + 1 if a.order is not None else idx + 1
                title = a.user.title or ""
                advisors_text.append(
                    f"{order}. {a.user.real_name}({a.user.employee_id})"
                    + (f"/{title}" if title else "")
                )

            members_text = []
            for m in p.projectmember_set.all():
                role_display = "负责人" if m.role == "LEADER" else "成员"
                members_text.append(f"{role_display}: {m.user.real_name}({m.user.employee_id})")

            leader_college_code = leader.college if leader else ""
            leader_college_label = (
                college_label_map.get(leader_college_code, leader_college_code)
                if leader_college_code
                else ""
            )

            data.append(
                {
                    "project_no": p.project_no,
                    "title": p.title,
                    "description": p.description,
                    "source_code": p.source.value if p.source else "",
                    "source_label": p.source.label if p.source else "",
                    "level_code": p.level.value if p.level else "",
                    "level_label": p.level.label if p.level else "",
                    "category_code": p.category.value if p.category else "",
                    "category_label": p.category.label if p.category else "",
                    "is_key_field": "是" if p.is_key_field else "否",
                    "key_domain_code": p.key_domain_code,
                    "self_funding": p.self_funding,
                    "category_description": p.category_description,
                    "start_date": p.start_date,
                    "end_date": p.end_date,
                    "budget": p.budget,
                    "approved_budget": p.approved_budget,
                    "research_content": p.research_content,
                    "research_plan": p.research_plan,
                    "expected_results": p.expected_results,
                    "innovation_points": p.innovation_points,
                    "status_code": p.status,
                    "status_display": p.get_status_display(),
                    "ranking": p.ranking,
                    "leader_name": leader.real_name if leader else "",
                    "leader_employee_id": leader.employee_id if leader else "",
                    "leader_phone": leader.phone if leader else "",
                    "leader_email": leader.email if leader else "",
                    "leader_college_code": leader.college if leader else "",
                    "leader_college": leader_college_label,
                    "leader_major": leader.major if leader else "",
                    "leader_grade": leader.grade if leader else "",
                    "leader_class_name": leader.class_name if leader else "",
                    "leader_department": leader.department if leader else "",
                    "advisors": "；".join(advisors_text),
                    "members": "；".join(members_text),
                    "achievements_count": len(list(p.achievements.all())),
                    "proposal_file_name": p.proposal_file.name if p.proposal_file else "",
                    "proposal_file_url": build_file_url(p.proposal_file),
                    "attachment_file_name": p.attachment_file.name if p.attachment_file else "",
                    "attachment_file_url": build_file_url(p.attachment_file),
                    "final_report_url": build_file_url(p.final_report),
                    "achievement_file_url": build_file_url(p.achievement_file),
                    "created_at": p.created_at,
                    "updated_at": p.updated_at,
                    "submitted_at": p.submitted_at,
                    "closure_applied_at": p.closure_applied_at,
                }
            )

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

            # 中期报告
            if p.mid_term_report:
                try:
                    files_to_zip.append((p.mid_term_report.path, f"{p.project_no}_{p.title}/中期报告.pdf"))
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

    @action(methods=["post"], detail=False, url_path="batch-status")
    def batch_update_status(self, request):
        """
        批量更新项目状态
        """
        user = request.user
        if not (user.is_level1_admin or user.is_level2_admin):
            return Response(
                {"code": 403, "message": "无权限操作"},
                status=status.HTTP_403_FORBIDDEN,
            )

        project_ids = request.data.get("project_ids", [])
        target_status = request.data.get("status")
        if not isinstance(project_ids, list) or not project_ids:
            return Response(
                {"code": 400, "message": "请提供项目ID列表"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not target_status:
            return Response(
                {"code": 400, "message": "请提供目标状态"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        allowed_statuses = {c[0] for c in Project.ProjectStatus.choices}
        if target_status not in allowed_statuses:
            return Response(
                {"code": 400, "message": "目标状态不合法"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = Project.objects.filter(id__in=project_ids)
        if user.is_level2_admin:
            queryset = queryset.filter(leader__college=user.college)

        updated = queryset.update(status=target_status)
        return Response(
            {"code": 200, "message": "更新成功", "data": {"updated": updated}}
        )

    def _render_project_doc(self, project, title):
        advisors = []
        for advisor in project.advisors.all():
            advisors.append(f"{advisor.user.real_name}({advisor.user.employee_id})")
        members = []
        for member in project.projectmember_set.all():
            role = "负责人" if member.role == "LEADER" else "成员"
            members.append(f"{role}: {member.user.real_name}({member.user.employee_id})")

        content = f"""
        <html>
        <head>
          <meta charset="utf-8" />
          <title>{title}</title>
        </head>
        <body>
          <h1 style="text-align:center;">{title}</h1>
          <h2>项目基本信息</h2>
          <p>项目编号：{project.project_no}</p>
          <p>项目名称：{project.title}</p>
          <p>项目级别：{project.level.label if project.level else ""}</p>
          <p>项目类别：{project.category.label if project.category else ""}</p>
          <p>项目来源：{project.source.label if project.source else ""}</p>
          <p>负责人：{project.leader.real_name}({project.leader.employee_id})</p>
          <p>负责人学院：{project.leader.college}</p>
          <p>指导教师：{"；".join(advisors)}</p>
          <p>项目成员：{"；".join(members)}</p>
          <h2>项目内容</h2>
          <p>项目简介：{project.description or ""}</p>
          <p>研究内容：{project.research_content or ""}</p>
          <p>研究方案：{project.research_plan or ""}</p>
          <p>预期成果：{project.expected_results or ""}</p>
          <p>创新点：{project.innovation_points or ""}</p>
        </body>
        </html>
        """
        return content

    def _render_establishment_notice(self, project):
        html = f"""
        <html>
        <head>
          <meta charset="utf-8" />
          <title>立项通知书</title>
        </head>
        <body>
          <h1 style="text-align:center;">立项通知书</h1>
          <p>项目编号：{project.project_no}</p>
          <p>项目名称：{project.title}</p>
          <p>负责人：{project.leader.real_name}({project.leader.employee_id})</p>
          <p>项目级别：{project.level.label if project.level else ""}</p>
          <p>项目类别：{project.category.label if project.category else ""}</p>
          <p>批准经费：{project.approved_budget or ""}</p>
          <p>请按要求组织实施项目。</p>
        </body>
        </html>
        """
        return html

    @action(methods=["get"], detail=True, url_path="export-doc")
    def export_doc(self, request, pk=None):
        """
        导出单个项目申报书（doc）
        """
        try:
            buffer, filename = DocumentService.generate_project_doc(pk)
            response = HttpResponse(
                buffer.read(),
                content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
            return response
        except Exception as e:
            return Response(
                {"code": 500, "message": f"生成失败: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(methods=["get"], detail=False, url_path="batch-export-doc")
    def batch_export_doc(self, request):
        """
        批量导出项目申报书（zip-doc）
        """
        ids = request.query_params.get("ids", "")
        if not ids:
            return Response(
                {"code": 400, "message": "请提供项目ID列表"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        id_list = [int(i) for i in ids.split(",") if i.isdigit()]
        if not id_list:
            return Response(
                {"code": 400, "message": "项目ID列表无效"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for pk in id_list:
                try:
                    doc_buffer, filename = DocumentService.generate_project_doc(pk)
                    zf.writestr(filename, doc_buffer.getvalue())
                except Exception as e:
                    pass # Ignore failed docs in batch
        
        buffer.seek(0)
        response = HttpResponse(buffer.read(), content_type="application/zip")
        response["Content-Disposition"] = 'attachment; filename="project_docs.zip"'
        return response

    @action(methods=["get"], detail=False, url_path="batch-establishment-notice")
    def batch_establishment_notice(self, request):
        """
        批量生成立项通知书（zip）
        """
        ids = request.query_params.get("ids", "")
        if not ids:
            return Response(
                {"code": 400, "message": "请提供项目ID列表"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        id_list = [int(i) for i in ids.split(",") if i.isdigit()]
        if not id_list:
            return Response(
                {"code": 400, "message": "项目ID列表无效"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = self.get_queryset().filter(id__in=id_list)
        from io import BytesIO
        import zipfile
        from django.http import HttpResponse

        buffer = BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for project in queryset:
                html = self._render_establishment_notice(project)
                filename = f"{project.project_no}_立项通知书.doc"
                zf.writestr(filename, html)
        buffer.seek(0)
        response = HttpResponse(buffer.read(), content_type="application/zip")
        response["Content-Disposition"] = 'attachment; filename="notices.zip"'
        return response

    def _render_certificate_html(self, project, setting):
        return render_certificate_html(project, setting)

    @action(methods=["get"], detail=True, url_path="certificate-preview")
    def certificate_preview(self, request, pk=None):
        """
        结题证书预览（HTML）
        """
        project = self.get_object()
        from apps.system_settings.models import CertificateSetting
        setting = CertificateSetting.objects.filter(is_active=True).order_by("-updated_at").first()
        html = self._render_certificate_html(project, setting)
        from django.http import HttpResponse

        return HttpResponse(html, content_type="text/html")

    @action(methods=["get"], detail=False, url_path="batch-certificates")
    def batch_certificates(self, request):
        """
        批量生成结题证书（zip）
        """
        ids = request.query_params.get("ids", "")
        if not ids:
            return Response(
                {"code": 400, "message": "请提供项目ID列表"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        id_list = [int(i) for i in ids.split(",") if i.isdigit()]
        if not id_list:
            return Response(
                {"code": 400, "message": "项目ID列表无效"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = self.get_queryset().filter(id__in=id_list, status=Project.ProjectStatus.CLOSED)
        from apps.system_settings.models import CertificateSetting
        setting = CertificateSetting.objects.filter(is_active=True).order_by("-updated_at").first()

        from io import BytesIO
        import zipfile
        from django.http import HttpResponse

        buffer = BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for project in queryset:
                html = self._render_certificate_html(project, setting)
                filename = f"{project.project_no}_结题证书.html"
                zf.writestr(filename, html)
        buffer.seek(0)
        response = HttpResponse(buffer.read(), content_type="application/zip")
        response["Content-Disposition"] = 'attachment; filename="certificates.zip"'
        return response

    @action(methods=["post"], detail=False, url_path="archive-closed")
    def archive_closed_projects(self, request):
        """
        归档已结题项目
        """
        closed_projects = self.get_queryset().filter(status=Project.ProjectStatus.CLOSED)
        created = 0
        for project in closed_projects:
            if hasattr(project, "archive"):
                continue
            snapshot = ProjectSerializer(project, context={"request": request}).data
            attachments = []
            for field in ["proposal_file", "attachment_file", "mid_term_report", "final_report", "achievement_file"]:
                f = getattr(project, field, None)
                if f:
                    attachments.append({"field": field, "name": f.name})
            ProjectArchive.objects.create(project=project, snapshot=snapshot, attachments=attachments)
            created += 1
        return Response(
            {"code": 200, "message": "归档完成", "data": {"created": created}}
        )

    @action(methods=["post"], detail=False, url_path="push-external")
    def push_external(self, request):
        """
        推送项目数据到外部平台（模拟）
        """
        ids = request.data.get("project_ids", [])
        target = request.data.get("target", "ANHUI_INNOVATION_PLATFORM")
        
        if not isinstance(ids, list) or not ids:
            return Response(
                {"code": 400, "message": "请提供项目ID列表"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        success_count = 0
        failed_count = 0
        
        for project_id in ids:
            success, msg = ExternalPushService.push_project_data(project_id, target)
            if success:
                success_count += 1
            else:
                failed_count += 1
                
        return Response(
            {
                "code": 200, 
                "message": f"推送完成：成功 {success_count}，失败 {failed_count}",
                "data": {"success": success_count, "failed": failed_count}
            }
        )


    @action(methods=["get"], detail=False, url_path="push-records")
    def push_records(self, request):
        queryset = ProjectPushRecord.objects.all().order_by("-created_at")
        serializer = ProjectPushRecordSerializer(queryset, many=True)
        return Response({"code": 200, "message": "获取成功", "data": serializer.data})

    @action(methods=["get"], detail=False, url_path="archives")
    def archives(self, request):
        queryset = ProjectArchive.objects.all().order_by("-archived_at")
        serializer = ProjectArchiveSerializer(queryset, many=True)
        return Response({"code": 200, "message": "获取成功", "data": serializer.data})

    @action(methods=["post"], detail=False, url_path="import-history")
    def import_history_projects(self, request):
        """
        批量导入历史项目
        """
        file = request.FILES.get("file")
        if not file:
            return Response(
                {"code": 400, "message": "请上传文件"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        import openpyxl
        from apps.users.models import User
        from apps.dictionaries.models import DictionaryItem
        from django.utils import timezone

        wb = openpyxl.load_workbook(file)
        sheet = wb.active
        created = 0
        errors = []

        header = [str(cell.value).strip() if cell.value is not None else "" for cell in sheet[1]]
        header_map = {name: idx for idx, name in enumerate(header)}

        def get_value(row, name, default=""):
            idx = header_map.get(name)
            if idx is None or idx >= len(row):
                return default
            value = row[idx]
            return value if value is not None else default

        for row_idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
            try:
                project_no = str(get_value(row, "项目编号", "")).strip()
                title = str(get_value(row, "项目名称", "")).strip()
                leader_id = str(get_value(row, "负责人学号/工号", "")).strip()
                leader_name = str(get_value(row, "负责人姓名", "")).strip()
                college_code = str(get_value(row, "学院", "")).strip()
                year_val = get_value(row, "项目年份", timezone.now().year)
                status_code = str(get_value(row, "项目状态(代码)", "CLOSED")).strip() or "CLOSED"
                level_code = str(get_value(row, "项目级别(代码)", "")).strip()
                category_code = str(get_value(row, "项目类别(代码)", "")).strip()
                source_code = str(get_value(row, "项目来源(代码)", "")).strip()

                if not title or not leader_id:
                    errors.append(f"第{row_idx}行缺少项目名称或负责人信息")
                    continue

                leader = User.objects.filter(employee_id=leader_id).first()
                if not leader:
                    leader = User.objects.create(
                        username=leader_id,
                        employee_id=leader_id,
                        real_name=leader_name or leader_id,
                        role=User.UserRole.STUDENT,
                        college=college_code or "",
                    )
                    leader.set_unusable_password()
                    leader.save()

                level_item = DictionaryItem.objects.filter(
                    dict_type__code="project_level", value=level_code
                ).first()
                category_item = DictionaryItem.objects.filter(
                    dict_type__code="project_type", value=category_code
                ).first()
                source_item = DictionaryItem.objects.filter(
                    dict_type__code="project_source", value=source_code
                ).first()

                if project_no and Project.objects.filter(project_no=project_no).exists():
                    errors.append(f"第{row_idx}行项目编号已存在")
                    continue

                if not project_no:
                    from .services import ProjectService

                    project_no = ProjectService.generate_project_no(
                        int(year_val) if str(year_val).isdigit() else timezone.now().year,
                        leader.college,
                    )

                project = Project.objects.create(
                    project_no=project_no,
                    title=title,
                    leader=leader,
                    year=int(year_val) if str(year_val).isdigit() else timezone.now().year,
                    status=status_code if status_code in dict(Project.ProjectStatus.choices) else Project.ProjectStatus.CLOSED,
                    level=level_item,
                    category=category_item,
                    source=source_item,
                )
                project.save()
                ProjectMember.objects.get_or_create(
                    project=project,
                    user=leader,
                    defaults={"role": ProjectMember.MemberRole.LEADER},
                )
                created += 1
            except Exception as exc:
                errors.append(f"第{row_idx}行导入失败: {exc}")

        return Response(
            {
                "code": 200,
                "message": "导入完成",
                "data": {"created": created, "errors": errors},
            }
        )

    @action(methods=["get"], detail=False, url_path="export-project-nos")
    def export_project_numbers(self, request):
        """
        导出项目编号清单
        """
        from apps.utils.export import generate_excel
        from django.http import HttpResponse
        from datetime import datetime

        queryset = self.get_queryset().select_related("leader")
        data = []
        for p in queryset:
            data.append(
                {
                    "project_no": p.project_no,
                    "title": p.title,
                    "year": p.year,
                    "college": p.leader.college if p.leader else "",
                    "status": p.status,
                }
            )
        headers = {
            "project_no": "项目编号",
            "title": "项目名称",
            "year": "年份",
            "college": "学院",
            "status": "状态",
        }
        excel_file = generate_excel(data, headers)
        filename = f"project_numbers_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
        response = HttpResponse(
            excel_file.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    @action(methods=["get"], detail=False, url_path="duplicate-project-nos")
    def duplicate_project_numbers(self, request):
        """
        查重项目编号
        """
        from django.db.models import Count

        duplicates = (
            Project.objects.values("project_no")
            .annotate(cnt=Count("id"))
            .filter(cnt__gt=1)
        )
        return Response(
            {"code": 200, "message": "获取成功", "data": list(duplicates)}
        )


class AchievementManagementViewSet(viewsets.ModelViewSet):
    """
    成果管理视图集（管理员）
    """
    queryset = ProjectAchievement.objects.all()
    serializer_class = ProjectAchievementSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = ProjectAchievement.objects.all().order_by("-created_at")
        
        # 权限控制：二级管理员只能看到本学院项目的成果
        user = self.request.user
        if user.is_level2_admin:
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

        projects_qs = Project.objects.filter(status__in=closure_statuses)

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
