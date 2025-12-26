"""
项目导出相关 mixin
"""

import io
import zipfile
from datetime import datetime

from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from ...certificates import render_certificate_html
from ...models import Project
from ...services import DocumentService


class ProjectExportMixin:
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

    def _render_certificate_html(self, project, setting):
        return render_certificate_html(project, setting)

    @action(methods=["get"], detail=False, url_path="export")
    def export_data(self, request):
        """
        批量导出数据
        """
        try:
            from apps.utils.export import generate_excel
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
                members_text.append(
                    f"{role_display}: {m.user.real_name}({m.user.employee_id})"
                )

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
                    ext = p.proposal_file.name.split(".")[-1]
                    files_to_zip.append(
                        (p.proposal_file.path, f"{p.project_no}_{p.title}/申请书.{ext}")
                    )
                except Exception:
                    pass

            # 中期报告
            if p.mid_term_report:
                try:
                    files_to_zip.append(
                        (p.mid_term_report.path, f"{p.project_no}_{p.title}/中期报告.pdf")
                    )
                except Exception:
                    pass

            # 结题报告
            if p.final_report:
                try:
                    files_to_zip.append(
                        (p.final_report.path, f"{p.project_no}_{p.title}/结题报告.pdf")
                    )
                except Exception:
                    pass

            # 成果附件 (zip/rar/pdf)
            if p.achievement_file:
                try:
                    ext = p.achievement_file.name.split(".")[-1]
                    files_to_zip.append(
                        (p.achievement_file.path, f"{p.project_no}_{p.title}/成果附件.{ext}")
                    )
                except Exception:
                    pass

            # 独立的成果附件 (ProjectAchievement)
            for ach in p.achievements.all():
                if ach.attachment:
                    try:
                        ext = ach.attachment.name.split(".")[-1]
                        files_to_zip.append(
                            (
                                ach.attachment.path,
                                f"{p.project_no}_{p.title}/成果/{ach.title}.{ext}",
                            )
                        )
                    except Exception:
                        pass

        if not files_to_zip:
            return Response(
                {"code": 400, "message": "当前筛选条件下没有可下载的附件"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        zip_file = generate_zip(files_to_zip)
        filename = f"attachments_{datetime.now().strftime('%Y%m%d%H%M%S')}.zip"

        response = HttpResponse(
            zip_file.read(),
            content_type="application/zip",
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    @action(methods=["get"], detail=True, url_path="export-doc")
    def export_doc(self, request, pk=None):
        """
        导出单个项目申报书（doc）
        """
        try:
            buffer, filename = DocumentService.generate_project_doc(pk)
            response = HttpResponse(
                buffer.read(),
                content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
            response["Content-Disposition"] = f'attachment; filename="{filename}"'
            return response
        except Exception as exc:
            return Response(
                {"code": 500, "message": f"生成失败: {str(exc)}"},
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
                except Exception:
                    pass

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

        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for project in queryset:
                html = self._render_establishment_notice(project)
                filename = f"{project.project_no}_立项通知书.doc"
                zf.writestr(filename, html)
        buffer.seek(0)
        response = HttpResponse(buffer.read(), content_type="application/zip")
        response["Content-Disposition"] = 'attachment; filename="notices.zip"'
        return response

    @action(methods=["get"], detail=True, url_path="certificate-preview")
    def certificate_preview(self, request, pk=None):
        """
        结题证书预览（HTML）
        """
        project = self.get_object()
        from apps.system_settings.models import CertificateSetting

        setting = (
            CertificateSetting.objects.filter(is_active=True)
            .order_by("-updated_at")
            .first()
        )
        html = self._render_certificate_html(project, setting)
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

        queryset = self.get_queryset().filter(
            id__in=id_list, status=Project.ProjectStatus.CLOSED
        )
        from apps.system_settings.models import CertificateSetting

        setting = (
            CertificateSetting.objects.filter(is_active=True)
            .order_by("-updated_at")
            .first()
        )

        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for project in queryset:
                html = self._render_certificate_html(project, setting)
                filename = f"{project.project_no}_结题证书.html"
                zf.writestr(filename, html)
        buffer.seek(0)
        response = HttpResponse(buffer.read(), content_type="application/zip")
        response["Content-Disposition"] = 'attachment; filename="certificates.zip"'
        return response

    @action(methods=["get"], detail=False, url_path="export-project-nos")
    def export_project_numbers(self, request):
        """
        导出项目编号清单
        """
        from apps.utils.export import generate_excel

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
