"""
项目导出数据相关 mixin
"""

from datetime import datetime

from django.http import HttpResponse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response


class ProjectAdminExportDataMixin:
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
            .prefetch_related(
                "advisors__user", "projectmember_set__user", "achievements"
            )
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
            "start_date": "开始日期",
            "end_date": "结束日期",
            "budget": "项目经费(元)",
            "approved_budget": "批准经费(元)",
            "expected_results": "预期成果",
            "status_code": "状态(代码)",
            "status_display": "状态",
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
                    "start_date": p.start_date,
                    "end_date": p.end_date,
                    "budget": p.budget,
                    "approved_budget": p.approved_budget,
                    "expected_results": p.expected_results,
                    "status_code": p.status,
                    "status_display": p.get_status_display(),
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
                    "proposal_file_name": p.proposal_file.name
                    if p.proposal_file
                    else "",
                    "proposal_file_url": build_file_url(p.proposal_file),
                    "attachment_file_name": p.attachment_file.name
                    if p.attachment_file
                    else "",
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
            content_type=(
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ),
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
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
