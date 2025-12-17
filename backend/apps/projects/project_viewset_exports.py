"""
Project export action mixins (keep views.py small).
"""

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import HttpResponse

from .models import Project


class ProjectExportActionsMixin:
    permission_classes = [IsAuthenticated]

    @action(methods=["get"], detail=False, url_path="export-excel")
    def export_excel(self, request):
        """
        批量导出项目数据为Excel（仅二级管理员）
        """
        user = request.user
        if not user.is_level2_admin:
            return Response(
                {"code": 403, "message": "无权限导出数据"},
                status=status.HTTP_403_FORBIDDEN,
            )

        projects = Project.objects.filter(leader__college=user.college)

        status_filter = request.query_params.get("status")
        if status_filter:
            projects = projects.filter(status=status_filter)

        import openpyxl

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
            ws.append(
                [
                    project.project_no,
                    project.title,
                    project.get_level_display(),
                    project.leader.real_name,
                    project.advisor,
                    project.category,
                    project.research_field,
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
            column = [cell for cell in column]
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except Exception:
                    pass
            adjusted_width = (max_length + 2) * 1.2
            ws.column_dimensions[column[0].column_letter].width = adjusted_width

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
        批量下载项目附件为ZIP（仅二级管理员）
        """
        user = request.user
        if not user.is_level2_admin:
            return Response(
                {"code": 403, "message": "无权限下载附件"},
                status=status.HTTP_403_FORBIDDEN,
            )

        projects = Project.objects.filter(leader__college=user.college)

        status_filter = request.query_params.get("status")
        if status_filter:
            projects = projects.filter(status=status_filter)

        from io import BytesIO
        import zipfile

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for project in projects:
                if project.proposal_file:
                    try:
                        file_path = project.proposal_file.path
                        zip_file.write(
                            file_path,
                            f"{project.project_no}/申报书_{project.proposal_file.name.split('/')[-1]}",
                        )
                    except Exception:
                        pass

                if project.final_report:
                    try:
                        file_path = project.final_report.path
                        zip_file.write(
                            file_path,
                            f"{project.project_no}/结题报告_{project.final_report.name.split('/')[-1]}",
                        )
                    except Exception:
                        pass

                for achievement in project.achievements.all():
                    if achievement.attachment:
                        try:
                            file_path = achievement.attachment.path
                            zip_file.write(
                                file_path,
                                f"{project.project_no}/成果_{achievement.title}_{achievement.attachment.name.split('/')[-1]}",
                            )
                        except Exception:
                            pass

        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer.read(), content_type="application/zip")
        response["Content-Disposition"] = (
            f'attachment; filename="attachments_{user.college}.zip"'
        )
        return response

