"""
项目批量操作相关 mixin
"""

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from ...models import Project, ProjectArchive, ProjectMember, ProjectPushRecord
from ...serializers import (
    ProjectArchiveSerializer,
    ProjectPushRecordSerializer,
)
from ...services import ExternalPushService, archive_projects


class ProjectBatchMixin:
    @action(methods=["post"], detail=False, url_path="batch-status")
    def batch_update_status(self, request):
        """
        批量更新项目状态
        """
        user = request.user
        if not (user.is_level1_admin or user.is_level2_admin):
            return Response(
                {"code": 403, "message": "无权限操作"},
                status=status.HTTP_403_FORBIDDEN,
            )

        project_ids = request.data.get("project_ids", [])
        target_status = request.data.get("status")
        if not isinstance(project_ids, list) or not project_ids:
            return Response(
                {"code": 400, "message": "请提供项目ID列表"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not target_status:
            return Response(
                {"code": 400, "message": "请提供目标状态"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        allowed_statuses = {c[0] for c in Project.ProjectStatus.choices}
        if target_status not in allowed_statuses:
            return Response(
                {"code": 400, "message": "目标状态不合法"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = Project.objects.filter(id__in=project_ids)
        if user.is_level2_admin:
            queryset = queryset.filter(leader__college=user.college)

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
        created = archive_projects(closed_projects, request=request)
        return Response(
            {"code": 200, "message": "归档完成", "data": {"created": len(created)}}
        )

    @action(methods=["post"], detail=False, url_path="push-external")
    def push_external(self, request):
        """
        推送项目数据到外部平台（模拟）
        """
        ids = request.data.get("project_ids", [])
        target = request.data.get("target", "ANHUI_INNOVATION_PLATFORM")

        if not isinstance(ids, list) or not ids:
            return Response(
                {"code": 400, "message": "请提供项目ID列表"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        success_count = 0
        failed_count = 0

        for project_id in ids:
            success, _msg = ExternalPushService.push_project_data(project_id, target)
            if success:
                success_count += 1
            else:
                failed_count += 1

        return Response(
            {
                "code": 200,
                "message": f"推送完成：成功 {success_count}，失败 {failed_count}",
                "data": {"success": success_count, "failed": failed_count},
            }
        )

    @action(methods=["get"], detail=False, url_path="push-records")
    def push_records(self, request):
        queryset = ProjectPushRecord.objects.all().order_by("-created_at")
        serializer = ProjectPushRecordSerializer(queryset, many=True)
        return Response({"code": 200, "message": "获取成功", "data": serializer.data})

    @action(methods=["get"], detail=False, url_path="archives")
    def archives(self, request):
        queryset = ProjectArchive.objects.all().order_by("-archived_at")
        serializer = ProjectArchiveSerializer(queryset, many=True)
        return Response({"code": 200, "message": "获取成功", "data": serializer.data})

    @action(methods=["post"], detail=False, url_path="import-history")
    def import_history_projects(self, request):
        """
        批量导入历史项目
        """
        from apps.system_settings.models import ProjectBatch
        from apps.system_settings.services import SystemSettingService

        file = request.FILES.get("file")
        if not file:
            return Response(
                {"code": 400, "message": "请上传文件"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        import openpyxl  # type: ignore[import-untyped]
        from apps.users.models import User, Role
        from apps.dictionaries.models import DictionaryItem
        from django.utils import timezone

        wb = openpyxl.load_workbook(file)
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

        batch_id = request.data.get("batch_id") or request.query_params.get("batch_id")

        for row_idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
            try:
                project_no = str(get_value(row, "项目编号", "")).strip()
                title = str(get_value(row, "项目名称", "")).strip()
                leader_id = str(get_value(row, "负责人学号/工号", "")).strip()
                leader_name = str(get_value(row, "负责人姓名", "")).strip()
                college_code = str(get_value(row, "学院", "")).strip()
                year_val = get_value(row, "项目年份", timezone.now().year)
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

                if project_no and Project.objects.filter(project_no=project_no).exists():
                    errors.append(f"第{row_idx}行项目编号已存在")
                    continue

                if not project_no:
                    from ...services import ProjectService

                    project_no = ProjectService.generate_project_no(
                        int(year_val) if str(year_val).isdigit() else timezone.now().year,
                        leader.college,
                    )

                batch = None
                if batch_id:
                    batch = ProjectBatch.objects.filter(id=batch_id).first()
                if not batch and str(year_val).isdigit():
                    batch = (
                        ProjectBatch.objects.filter(year=int(year_val), is_active=True)
                        .order_by("-is_current", "-id")
                        .first()
                    )
                if not batch:
                    batch = SystemSettingService.get_current_batch()

                project = Project.objects.create(
                    project_no=project_no,
                    title=title,
                    leader=leader,
                    batch=batch,
                    year=(
                        batch.year
                        if batch
                        else (
                            int(year_val)
                            if str(year_val).isdigit()
                            else timezone.now().year
                        )
                    ),
                    status=(
                        status_code
                        if status_code in dict(Project.ProjectStatus.choices)
                        else Project.ProjectStatus.CLOSED
                    ),
                    level=level_item,
                    category=category_item,
                    source=source_item,
                )
                project.save()
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
