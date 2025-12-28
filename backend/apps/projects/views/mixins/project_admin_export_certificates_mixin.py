"""
项目证书导出相关 mixin
"""

import io
import zipfile

from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

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
        from apps.system_settings.models import CertificateSetting

        setting = (
            CertificateSetting.objects.filter(is_active=True)
            .order_by("-updated_at")
            .first()
        )
        html = self._render_certificate_html(project, setting, request=request)
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
                html = self._render_certificate_html(project, setting, request=request)
                filename = f"{project.project_no}_结题证书.html"
                zf.writestr(filename, html)
        buffer.seek(0)
        response = HttpResponse(buffer.read(), content_type="application/zip")
        response["Content-Disposition"] = 'attachment; filename="certificates.zip"'
        return response
