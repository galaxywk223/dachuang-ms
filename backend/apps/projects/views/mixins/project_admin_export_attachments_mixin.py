"""
项目附件导出相关 mixin
"""

from datetime import datetime
import logging

from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.utils.downloads import attachment_content_disposition
from apps.utils.export import safe_zip_path
from apps.utils.pagination import positive_int_csv


class ProjectAdminExportAttachmentsMixin:
    logger = logging.getLogger(__name__)
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
            id_list = positive_int_csv(ids)
            if id_list is None:
                return Response(
                    {"code": 400, "message": "项目ID列表无效"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if id_list:
                queryset = queryset.filter(id__in=id_list)

        files_to_zip = []
        for p in queryset:
            # 申请书
            if p.proposal_file:
                try:
                    ext = p.proposal_file.name.split(".")[-1]
                    files_to_zip.append(
                        (
                            p.proposal_file,
                            safe_zip_path(
                                f"{p.project_no}_{p.title}", f"申请书.{ext}"
                            ),
                        )
                    )
                except Exception as exc:
                    self.logger.warning("Skip proposal file for project %s: %s", p.id, exc)

            # 中期报告
            if p.mid_term_report:
                try:
                    name = p.mid_term_report.name
                    ext = name.rsplit(".", 1)[-1] if "." in name else "file"
                    files_to_zip.append(
                        (
                            p.mid_term_report,
                            safe_zip_path(
                                f"{p.project_no}_{p.title}", f"中期报告.{ext}"
                            ),
                        )
                    )
                except Exception as exc:
                    self.logger.warning("Skip mid-term report for project %s: %s", p.id, exc)

            # 结题报告
            if p.final_report:
                try:
                    name = p.final_report.name
                    ext = name.rsplit(".", 1)[-1] if "." in name else "file"
                    files_to_zip.append(
                        (
                            p.final_report,
                            safe_zip_path(
                                f"{p.project_no}_{p.title}", f"结题报告.{ext}"
                            ),
                        )
                    )
                except Exception as exc:
                    self.logger.warning("Skip final report for project %s: %s", p.id, exc)

            # 成果附件 (zip/rar/pdf/doc/docx)
            if p.achievement_file:
                try:
                    ext = p.achievement_file.name.split(".")[-1]
                    files_to_zip.append(
                        (
                            p.achievement_file,
                            safe_zip_path(
                                f"{p.project_no}_{p.title}", f"成果附件.{ext}"
                            ),
                        )
                    )
                except Exception as exc:
                    self.logger.warning("Skip achievement file for project %s: %s", p.id, exc)

            # 独立的成果附件 (ProjectAchievement)
            for ach in p.achievements.all():
                if ach.attachment:
                    try:
                        ext = ach.attachment.name.split(".")[-1]
                        files_to_zip.append(
                            (
                                ach.attachment,
                                safe_zip_path(
                                    f"{p.project_no}_{p.title}",
                                    "成果",
                                    f"{ach.title}.{ext}",
                                ),
                            )
                        )
                    except Exception as exc:
                        self.logger.warning("Skip achievement attachment for project %s: %s", p.id, exc)

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
        response["Content-Disposition"] = attachment_content_disposition(filename)
        return response
