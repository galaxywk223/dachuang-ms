"""
项目批量操作相关 mixin
"""

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from ...models import Project, ProjectArchive, ProjectMember
from apps.operations.services import DataCenterService
from apps.system_settings.services import SystemSettingService
from apps.utils.pagination import optional_positive_int, positive_int_list
from ...serializers import ProjectArchiveSerializer
from ...services.archive_service import ArchiveService


ADMIN_BATCH_STATUS_TARGETS = {
    Project.ProjectStatus.CLOSED,
    Project.ProjectStatus.TERMINATED,
}


def has_school_admin_scope(user):
    return user.is_school_admin or user.is_level1_admin


class ProjectBatchMixin:
    @action(methods=["post"], detail=False, url_path="batch-status")
    def batch_update_status(self, request):
        """
        批量更新项目状态
        """
        user = request.user
        if not has_school_admin_scope(user):
            return Response(
                {"code": 403, "message": "只有校级管理员可以批量变更项目状态"},
                status=status.HTTP_403_FORBIDDEN,
            )

        project_ids = request.data.get("project_ids", [])
        target_status = request.data.get("status")
        if not isinstance(project_ids, list) or not project_ids:
            return Response(
                {"code": 400, "message": "请提供项目ID列表"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        project_ids = positive_int_list(project_ids)
        if not project_ids:
            return Response(
                {"code": 400, "message": "项目ID列表不合法"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not target_status:
            return Response(
                {"code": 400, "message": "请提供目标状态"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if target_status not in ADMIN_BATCH_STATUS_TARGETS:
            return Response(
                {"code": 400, "message": "目标状态不合法"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        current_batch = SystemSettingService.get_current_batch()
        if not current_batch:
            return Response(
                {"code": 200, "message": "当前无可用批次", "data": {"updated": 0}}
            )

        queryset = Project.objects.filter(id__in=project_ids, batch=current_batch)
        updated = queryset.update(status=target_status)
        return Response(
            {"code": 200, "message": "更新成功", "data": {"updated": updated}}
        )

    @action(methods=["post"], detail=False, url_path="archive-closed")
    def archive_closed_projects(self, request):
        """
        归档已结题项目
        """
        closed_projects = self.get_queryset().filter(status=Project.ProjectStatus.CLOSED)
        total = closed_projects.count()
        result = ArchiveService.archive_projects(closed_projects, request=request)
        created_count = result["success_count"]
        failed_count = result["failed_count"]
        skipped_count = total - created_count - failed_count
        message = "归档完成" if failed_count == 0 else "归档部分完成"
        return Response(
            {
                "code": 200,
                "message": message,
                "data": {
                    "created": created_count,
                    "skipped": skipped_count,
                    "failed_count": failed_count,
                    "failures": result["failed"],
                },
            }
        )

    @action(methods=["get"], detail=False, url_path="archives")
    def archives(self, request):
        queryset = ProjectArchive.objects.all().order_by("-archived_at")
        if request.user.is_admin and not has_school_admin_scope(request.user):
            queryset = queryset.filter(project__leader__college=request.user.college)
        serializer = ProjectArchiveSerializer(queryset, many=True)
        return Response({"code": 200, "message": "获取成功", "data": serializer.data})

    @action(methods=["post"], detail=False, url_path="import-history")
    def import_history_projects(self, request):
        """
        批量导入历史项目
        """
        if not has_school_admin_scope(request.user):
            return Response(
                {"code": 403, "message": "无权限导入历史项目"},
                status=status.HTTP_403_FORBIDDEN,
            )

        from apps.system_settings.models import ProjectBatch

        file = request.FILES.get("file")
        if not file:
            return Response(
                {"code": 400, "message": "请上传文件"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        batch_id = request.data.get("batch_id") or request.query_params.get("batch_id")
        target_batch = None
        if batch_id:
            parsed_batch_id = optional_positive_int(batch_id)
            if parsed_batch_id is None:
                return Response(
                    {"code": 400, "message": "批次参数不合法"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            target_batch = ProjectBatch.objects.filter(id=parsed_batch_id).first()
            if not target_batch:
                return Response(
                    {"code": 404, "message": "批次不存在"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if target_batch.status != ProjectBatch.STATUS_ARCHIVED:
                return Response(
                    {"code": 400, "message": "历史项目只能导入归档批次"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        import openpyxl  # type: ignore[import-untyped]
        from openpyxl.utils.exceptions import InvalidFileException  # type: ignore[import-untyped]
        from apps.users.models import User, Role
        from apps.dictionaries.models import DictionaryItem

        try:
            wb = openpyxl.load_workbook(file)
        except (InvalidFileException, OSError, KeyError, ValueError):
            return Response(
                {"code": 400, "message": "导入文件格式错误，请上传有效的 Excel 文件"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        sheet = wb.active
        created = 0
        errors = []
        student_role = Role.objects.filter(code=User.UserRole.STUDENT).first()
        if not student_role:
            return Response(
                {"code": 400, "message": "默认学生角色不存在"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        header = [
            str(cell.value).strip() if cell.value is not None else ""
            for cell in sheet[1]
        ]
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
                year_val = get_value(row, "项目年份", "")
                status_code = (
                    str(get_value(row, "项目状态(代码)", "CLOSED")).strip()
                    or "CLOSED"
                )
                level_code = str(get_value(row, "项目级别(代码)", "")).strip()
                category_code = str(get_value(row, "项目类别(代码)", "")).strip()
                source_code = str(get_value(row, "项目来源(代码)", "")).strip()

                if not title or not leader_id:
                    errors.append(f"第{row_idx}行缺少项目名称或负责人信息")
                    continue
                try:
                    year = DataCenterService._history_year(year_val, project_no)
                except ValueError as exc:
                    errors.append(f"第{row_idx}行项目年份{exc}")
                    continue

                leader = User.objects.filter(employee_id=leader_id).first()
                if not leader:
                    leader = User.objects.create(
                        username=leader_id,
                        employee_id=leader_id,
                        real_name=leader_name or leader_id,
                        role_fk=student_role,
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

                if not project_no:
                    from ...services import ProjectService

                    project_no = ProjectService.generate_project_no(
                        year,
                        leader.college,
                    )

                batch = target_batch
                if not batch:
                    batch, _ = ProjectBatch.objects.get_or_create(
                        code=f"HIST{year}",
                        defaults={
                            "name": f"{year} 年历史项目",
                            "year": year,
                            "status": ProjectBatch.STATUS_ARCHIVED,
                            "is_current": False,
                            "is_active": True,
                        },
                    )
                    if batch.status != ProjectBatch.STATUS_ARCHIVED:
                        batch.status = ProjectBatch.STATUS_ARCHIVED
                        batch.is_current = False
                        batch.is_active = True
                        batch.save(update_fields=["status", "is_current", "is_active"])

                existing_project = Project.objects.filter(project_no=project_no).first()
                if existing_project and existing_project.batch_id != batch.id:
                    errors.append(f"第{row_idx}行项目编号已存在于非历史批次，不能覆盖")
                    continue

                project, _ = Project.objects.update_or_create(
                    project_no=project_no,
                    defaults={
                        "title": title,
                        "leader": leader,
                        "batch": batch,
                        "year": batch.year,
                        "status": (
                            status_code
                            if status_code in dict(Project.ProjectStatus.choices)
                            else Project.ProjectStatus.CLOSED
                        ),
                        "level": level_item,
                        "category": category_item,
                        "source": source_item,
                    },
                )
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
        return Response({"code": 200, "message": "获取成功", "data": list(duplicates)})
