"""
项目文档导出相关 mixin
"""

import io
import zipfile
import logging
from html import escape

from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.operations.models import AsyncTaskRecord
from apps.operations.services import DataCenterService
from apps.utils.downloads import attachment_content_disposition
from apps.utils.export import safe_zip_arcname, safe_zip_path
from apps.utils.pagination import positive_int_csv

from ...services import DocumentService


class ProjectAdminExportDocumentsMixin:
    logger = logging.getLogger(__name__)

    @staticmethod
    def _html_text(value):
        return escape(str(value or ""), quote=True)

    def _render_project_doc(self, project, title):
        text = self._html_text
        advisors = []
        for advisor in project.advisors.all():
            advisors.append(
                f"{text(advisor.user.real_name)}({text(advisor.user.employee_id)})"
            )
        members = []
        for member in project.projectmember_set.all():
            role = "负责人" if member.role == "LEADER" else "成员"
            members.append(
                f"{text(role)}: {text(member.user.real_name)}({text(member.user.employee_id)})"
            )

        content = f"""
        <html>
        <head>
          <meta charset="utf-8" />
          <title>{text(title)}</title>
        </head>
        <body>
          <h1 style="text-align:center;">{text(title)}</h1>
          <h2>项目基本信息</h2>
          <p>项目编号：{text(project.project_no)}</p>
          <p>项目名称：{text(project.title)}</p>
          <p>项目级别：{text(project.level.label if project.level else "")}</p>
          <p>项目类别：{text(project.category.label if project.category else "")}</p>
          <p>项目来源：{text(project.source.label if project.source else "")}</p>
          <p>负责人：{text(project.leader.real_name)}({text(project.leader.employee_id)})</p>
          <p>负责人学院：{text(project.leader.college)}</p>
          <p>指导教师：{"；".join(advisors)}</p>
          <p>项目成员：{"；".join(members)}</p>
          <h2>项目内容</h2>
          <p>项目简介：{text(project.description)}</p>
          <p>预期成果：{text(project.expected_results)}</p>
        </body>
        </html>
        """
        return content

    def _render_establishment_notice(self, project):
        text = self._html_text
        html = f"""
        <html>
        <head>
          <meta charset="utf-8" />
          <title>立项通知书</title>
        </head>
        <body>
          <h1 style="text-align:center;">立项通知书</h1>
          <p>项目编号：{text(project.project_no)}</p>
          <p>项目名称：{text(project.title)}</p>
          <p>负责人：{text(project.leader.real_name)}({text(project.leader.employee_id)})</p>
          <p>项目级别：{text(project.level.label if project.level else "")}</p>
          <p>项目类别：{text(project.category.label if project.category else "")}</p>
          <p>批准经费：{text(project.approved_budget)}</p>
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
        project = self.get_object()
        try:
            buffer, filename = DocumentService.generate_project_doc(project.id)
            response = HttpResponse(
                buffer.read(),
                content_type=(
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                ),
            )
            response["Content-Disposition"] = attachment_content_disposition(filename)
            return response
        except Exception:
            self.logger.exception("Failed to export doc for project %s", project.id)
            return Response(
                {"code": 500, "message": "生成失败，请稍后重试"},
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
        id_list = positive_int_csv(ids)
        if not id_list:
            return Response(
                {"code": 400, "message": "项目ID列表无效"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        allowed_ids = set(
            self.get_queryset().filter(id__in=id_list).values_list("id", flat=True)
        )
        export_ids = [project_id for project_id in id_list if project_id in allowed_ids]

        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for pk in export_ids:
                try:
                    doc_buffer, filename = DocumentService.generate_project_doc(pk)
                    zf.writestr(safe_zip_arcname(filename), doc_buffer.getvalue())
                except Exception as exc:
                    self.logger.warning("Failed to export doc for project %s: %s", pk, exc)

        buffer.seek(0)
        response = HttpResponse(buffer.read(), content_type="application/zip")
        response["Content-Disposition"] = 'attachment; filename="project_docs.zip"'
        return response

    @action(methods=["post"], detail=False, url_path="batch-export-doc-task")
    def batch_export_doc_task(self, request):
        """
        批量导出项目申报书后台任务。
        """
        ids = request.data.get("ids") or request.query_params.get("ids", "")
        id_list = positive_int_csv(ids)
        if not id_list:
            return Response(
                {"code": 400, "message": "请提供项目ID列表"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        allowed_ids = set(
            self.get_queryset().filter(id__in=id_list).values_list("id", flat=True)
        )
        export_ids = [project_id for project_id in id_list if project_id in allowed_ids]

        buffer = io.BytesIO()
        exported = 0
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for pk in export_ids:
                try:
                    doc_buffer, filename = DocumentService.generate_project_doc(pk)
                    zf.writestr(safe_zip_arcname(filename), doc_buffer.getvalue())
                    exported += 1
                except Exception as exc:
                    self.logger.warning("Failed to export doc for project %s: %s", pk, exc)
        task = DataCenterService.create_completed_file_task(
            request.user,
            "批量申报书导出",
            AsyncTaskRecord.TaskType.EXPORT,
            "project_docs.zip",
            buffer.getvalue(),
            result={"total": exported},
        )
        return Response(
            {"code": 200, "message": "申报书导出任务已创建", "data": {"task_id": task.id}}
        )

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
        id_list = positive_int_csv(ids)
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
                filename = safe_zip_path(f"{project.project_no}_立项通知书.doc")
                zf.writestr(filename, html)
        buffer.seek(0)
        response = HttpResponse(buffer.read(), content_type="application/zip")
        response["Content-Disposition"] = 'attachment; filename="notices.zip"'
        return response

    @action(methods=["post"], detail=False, url_path="batch-establishment-notice-task")
    def batch_establishment_notice_task(self, request):
        """
        批量生成立项通知书后台任务。
        """
        ids = request.data.get("ids") or request.query_params.get("ids", "")
        id_list = positive_int_csv(ids)
        if not id_list:
            return Response(
                {"code": 400, "message": "请提供项目ID列表"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        queryset = self.get_queryset().filter(id__in=id_list)
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for project in queryset:
                html = self._render_establishment_notice(project)
                zf.writestr(
                    safe_zip_path(f"{project.project_no}_立项通知书.doc"),
                    html,
                )
        task = DataCenterService.create_completed_file_task(
            request.user,
            "批量立项通知书生成",
            AsyncTaskRecord.TaskType.EXPORT,
            "establishment_notices.zip",
            buffer.getvalue(),
            result={"total": queryset.count()},
        )
        return Response(
            {"code": 200, "message": "通知书生成任务已创建", "data": {"task_id": task.id}}
        )
