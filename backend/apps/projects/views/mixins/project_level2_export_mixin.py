"""
Project export actions.
"""

from io import BytesIO
import zipfile
import logging

import openpyxl  # type: ignore[import-untyped]
from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from ...models import Project


class ProjectLevel2ExportMixin:
    logger = logging.getLogger(__name__)
    @action(methods=["get"], detail=False, url_path="export-excel")
    def export_excel(self, request):
        """
        批量导出项目数据为Excel（仅非校级管理员）
        """
        user = request.user
        if not user.is_admin or user.is_level1_admin:
            return Response(
                {"code": 403, "message": "无权限导出数据"},
                status=status.HTTP_403_FORBIDDEN,
            )

        projects = Project.objects.filter(leader__college=user.college)

        status_filter = request.query_params.get("status")
        if status_filter:
            projects = projects.filter(status=status_filter)

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "项目列表"

        headers = [
            "项目编号",
            "项目名称",
            "项目级别",
            "负责人",
            "指导教师",
            "项目类别",
            "研究领域",
            "项目状态",
            "排名",
            "创建时间",
            "提交时间",
        ]
        ws.append(headers)

        for project in projects:
            level_label = project.level.label if project.level else ""
            category_label = project.category.label if project.category else ""
            advisor_names = ", ".join(
                [advisor.user.real_name for advisor in project.advisors.all()]
            )
            research_field = project.key_domain_code if project.is_key_field else ""
            ws.append(
                [
                    project.project_no,
                    project.title,
                    level_label,
                    project.leader.real_name,
                    advisor_names,
                    category_label,
                    research_field,
                    project.get_status_display(),
                    project.ranking or "",
                    project.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    (
                        project.submitted_at.strftime("%Y-%m-%d %H:%M:%S")
                        if project.submitted_at
                        else ""
                    ),
                ]
            )

        for column in ws.columns:
            max_length = 0
            column_cells = [cell for cell in column]
            for cell in column_cells:
                try:
                    max_length = max(max_length, len(str(cell.value)))
                except Exception as exc:
                    self.logger.debug("Failed to size column: %s", exc)
            adjusted_width = (max_length + 2) * 1.2
            ws.column_dimensions[column_cells[0].column_letter].width = adjusted_width

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = (
            f'attachment; filename="projects_{user.college}.xlsx"'
        )
        wb.save(response)
        return response

    @action(methods=["get"], detail=False, url_path="export-attachments")
    def export_attachments(self, request):
        """
        批量下载项目附件为ZIP（仅非校级管理员）
        """
        user = request.user
        if not user.is_admin or user.is_level1_admin:
            return Response(
                {"code": 403, "message": "无权限下载附件"},
                status=status.HTTP_403_FORBIDDEN,
            )

        projects = Project.objects.filter(leader__college=user.college)

        status_filter = request.query_params.get("status")
        if status_filter:
            projects = projects.filter(status=status_filter)

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for project in projects:
                if project.proposal_file:
                    try:
                        zip_file.write(
                            project.proposal_file.path,
                            f"{project.project_no}/申报书_{project.proposal_file.name.split('/')[-1]}",
                        )
                    except Exception as exc:
                        self.logger.warning("Skip proposal file for project %s: %s", project.id, exc)

                if project.mid_term_report:
                    try:
                        zip_file.write(
                            project.mid_term_report.path,
                            f"{project.project_no}/中期报告_{project.mid_term_report.name.split('/')[-1]}",
                        )
                    except Exception as exc:
                        self.logger.warning("Skip mid-term report for project %s: %s", project.id, exc)

                if project.final_report:
                    try:
                        zip_file.write(
                            project.final_report.path,
                            f"{project.project_no}/结题报告_{project.final_report.name.split('/')[-1]}",
                        )
                    except Exception as exc:
                        self.logger.warning("Skip final report for project %s: %s", project.id, exc)

                for achievement in project.achievements.all():
                    if achievement.attachment:
                        try:
                            zip_file.write(
                                achievement.attachment.path,
                                f"{project.project_no}/成果_{achievement.title}_{achievement.attachment.name.split('/')[-1]}",
                            )
                        except Exception as exc:
                            self.logger.warning("Skip achievement attachment for project %s: %s", project.id, exc)

        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer.read(), content_type="application/zip")
        response["Content-Disposition"] = (
            f'attachment; filename="attachments_{user.college}.zip"'
        )
        return response
