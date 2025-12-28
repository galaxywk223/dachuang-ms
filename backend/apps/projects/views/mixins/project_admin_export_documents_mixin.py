"""
项目文档导出相关 mixin
"""

import io
import zipfile
import logging

from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from ...services import DocumentService


class ProjectAdminExportDocumentsMixin:
    logger = logging.getLogger(__name__)
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
                content_type=(
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                ),
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
                except Exception as exc:
                    self.logger.warning("Failed to export doc for project %s: %s", pk, exc)

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
