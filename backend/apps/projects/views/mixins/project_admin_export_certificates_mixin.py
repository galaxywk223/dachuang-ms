"""
项目证书导出相关 mixin
"""

import io
import zipfile

from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.operations.models import AsyncTaskRecord
from apps.operations.services import DataCenterService
from apps.utils.export import safe_zip_path
from apps.utils.pagination import positive_int_csv

from ...certificates import render_certificate_html
from ...models import Project


class ProjectAdminExportCertificatesMixin:
    def _render_certificate_html(self, project, setting, request=None):
        return render_certificate_html(project, setting, request=request)

    @action(methods=["get"], detail=True, url_path="certificate-preview")
    def certificate_preview(self, request, pk=None):
        """
        结题证书预览（HTML）
        """
        project = self.get_object()
        # 自动匹配最佳证书配置
        html = self._render_certificate_html(project, setting=None, request=request)
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
        id_list = positive_int_csv(ids)
        if not id_list:
            return Response(
                {"code": 400, "message": "项目ID列表无效"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = self.get_queryset().filter(
            id__in=id_list, status=Project.ProjectStatus.CLOSED
        )

        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for project in queryset:
                # 假如不传递 setting，render_certificate_html 会内部自动匹配最佳模板
                html = self._render_certificate_html(
                    project, setting=None, request=request
                )
                filename = safe_zip_path(f"{project.project_no}_结题证书.html")
                zf.writestr(filename, html)
        buffer.seek(0)
        response = HttpResponse(buffer.read(), content_type="application/zip")
        response["Content-Disposition"] = 'attachment; filename="certificates.zip"'
        return response

    @action(methods=["post"], detail=False, url_path="batch-certificates-task")
    def batch_certificates_task(self, request):
        """
        批量生成结题证书后台任务。
        """
        ids = request.data.get("ids") or request.query_params.get("ids", "")
        id_list = positive_int_csv(ids)
        if not id_list:
            return Response(
                {"code": 400, "message": "请提供项目ID列表"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = self.get_queryset().filter(
            id__in=id_list, status=Project.ProjectStatus.CLOSED
        )
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for project in queryset:
                html = self._render_certificate_html(project, setting=None, request=request)
                zf.writestr(
                    safe_zip_path(f"{project.project_no}_结题证书.html"),
                    html,
                )
        task = DataCenterService.create_completed_file_task(
            request.user,
            "批量结题证书生成",
            AsyncTaskRecord.TaskType.EXPORT,
            "certificates.zip",
            buffer.getvalue(),
            result={"total": queryset.count()},
        )
        return Response(
            {"code": 200, "message": "证书生成任务已创建", "data": {"task_id": task.id}}
        )
