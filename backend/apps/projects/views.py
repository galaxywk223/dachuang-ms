"""
项目视图
"""

from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone
from django.http import HttpResponse
import openpyxl
from io import BytesIO
import zipfile

from .models import Project, ProjectMember, ProjectProgress, ProjectAchievement, ProjectExpenditure
from .serializers import (
    ProjectSerializer,
    ProjectListSerializer,
    ProjectMemberSerializer,
    ProjectProgressSerializer,
    ProjectSubmitSerializer,
    ProjectAchievementSerializer,
    ProjectClosureSerializer,
    ProjectExpenditureSerializer,
)
from .serializers_midterm import ProjectMidTermSerializer
from .services import ProjectService
from .certificates import render_certificate_html
from apps.reviews.services import ReviewService
from apps.reviews.models import Review
from apps.system_settings.services import SystemSettingService



class ProjectViewSet(viewsets.ModelViewSet):
    """
    项目管理视图集
    """

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["status", "level", "leader__college", "leader", "batch", "year"]
    search_fields = ["project_no", "title", "advisors__user__real_name"]
    ordering_fields = ["created_at", "updated_at", "submitted_at"]

    @action(detail=True, methods=["get"], url_path="budget-stats")
    def budget_stats(self, request, pk=None):
        """
        获取项目经费统计
        """
        project = self.get_object()
        stats = ProjectService.get_budget_stats(project)
        return Response({"code": 200, "message": "获取成功", "data": stats})

    @action(detail=True, methods=["get"], url_path="certificate")
    def certificate(self, request, pk=None):
        """
        获取结题证书（HTML）
        """
        project = self.get_object()
        user = request.user

        if project.status != Project.ProjectStatus.CLOSED:
            return Response(
                {"code": 400, "message": "项目未结题，无法生成证书"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not (
            user.is_level1_admin
            or user.is_level2_admin
            or (user.is_student and project.leader_id == user.id)
        ):
            return Response(
                {"code": 403, "message": "无权限访问"},
                status=status.HTTP_403_FORBIDDEN,
            )

        html = render_certificate_html(project)
        return HttpResponse(html, content_type="text/html")

    def get_serializer_class(self):
        if self.action == "list":
            return ProjectListSerializer
        return ProjectSerializer

    def get_queryset(self):
        """
        根据用户角色过滤项目
        """
        from django.db.models import Q

        user = self.request.user
        queryset = super().get_queryset()

        # 学生只能看到自己参与的项目
        if user.is_student:
            queryset = queryset.filter(Q(leader=user) | Q(members=user)).distinct()
        # 二级管理员只能看到自己学院的项目
        elif user.is_level2_admin:
            queryset = queryset.filter(leader__college=user.college)
        # 一级管理员可以看到所有项目
        elif user.is_level1_admin:
            pass
        # 指导教师只能看到自己指导的项目
        elif user.role == "TEACHER":
            queryset = queryset.filter(advisors__user=user).distinct()

        status_in = self.request.query_params.get("status_in")
        if status_in:
            status_list = [s.strip() for s in status_in.split(",") if s.strip()]
            queryset = queryset.filter(status__in=status_list)

        exclude_review_type = self.request.query_params.get("exclude_assigned_review_type")
        exclude_review_level = self.request.query_params.get("exclude_assigned_review_level")
        if exclude_review_type:
            review_qs = Review.objects.filter(
                review_type=exclude_review_type, reviewer__isnull=False
            )
            if exclude_review_level:
                review_qs = review_qs.filter(review_level=exclude_review_level)
            assigned_project_ids = review_qs.values_list("project_id", flat=True)
            queryset = queryset.exclude(id__in=assigned_project_ids)

        return queryset

    def list(self, request, *args, **kwargs):
        """
        统一返回结构，方便前端处理
        """
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return Response(
                {
                    "code": 200,
                    "message": "获取成功",
                    "data": {
                        "results": serializer.data,
                        "count": self.paginator.page.paginator.count,
                    },
                }
            )

        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "code": 200,
                "message": "获取成功",
                "data": {"results": serializer.data, "count": len(serializer.data)},
            }
        )

    def retrieve(self, request, *args, **kwargs):
        """
        项目详情统一返回结构
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({"code": 200, "message": "获取成功", "data": serializer.data})

    def perform_create(self, serializer):
        """
        创建项目时设置负责人为当前用户
        """
        project = serializer.save(leader=self.request.user)
        # 自动将负责人添加为项目成员
        ProjectMember.objects.create(
            project=project,
            user=self.request.user,
            role=ProjectMember.MemberRole.LEADER,
        )

    @action(methods=["post"], detail=True)
    def submit(self, request, pk=None):
        """
        提交项目申报
        """
        project = self.get_object()

        # 检查权限
        if project.leader != request.user:
            return Response(
                {"code": 403, "message": "只有项目负责人可以提交项目"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # 检查项目状态
        if project.status != Project.ProjectStatus.DRAFT:
            return Response(
                {"code": 400, "message": "项目状态不允许提交"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 更新项目状态
        # 更新项目状态并创建导师审核
        from apps.reviews.services import ReviewService
        # This will set status to TEACHER_AUDITING
        ReviewService.create_teacher_review(project)
        
        project.submitted_at = timezone.now()
        project.save(update_fields=["submitted_at"])

        return Response({"code": 200, "message": "项目提交成功，等待导师审核"})

    @action(methods=["post"], detail=True)
    def add_member(self, request, pk=None):
        """
        添加项目成员
        """
        project = self.get_object()

        # 检查权限
        if project.leader != request.user:
            return Response(
                {"code": 403, "message": "只有项目负责人可以添加成员"},
                status=status.HTTP_403_FORBIDDEN,
            )

        user_id = request.data.get("user_id")
        if not user_id:
            return Response(
                {"code": 400, "message": "请提供用户ID"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            from apps.users.models import User

            user = User.objects.get(id=user_id)

            # 检查是否已是成员
            if ProjectMember.objects.filter(project=project, user=user).exists():
                return Response(
                    {"code": 400, "message": "该用户已是项目成员"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 添加成员
            member = ProjectMember.objects.create(
                project=project, user=user, role=ProjectMember.MemberRole.MEMBER
            )

            serializer = ProjectMemberSerializer(member)
            return Response(
                {"code": 200, "message": "成员添加成功", "data": serializer.data}
            )
        except User.DoesNotExist:
            return Response(
                {"code": 404, "message": "用户不存在"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(
        methods=["delete"], detail=True, url_path="remove-member/(?P<member_id>[^/.]+)"
    )
    def remove_member(self, request, pk=None, member_id=None):
        """
        移除项目成员
        """
        project = self.get_object()

        # 检查权限
        if project.leader != request.user:
            return Response(
                {"code": 403, "message": "只有项目负责人可以移除成员"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            member = ProjectMember.objects.get(project=project, id=member_id)

            # 不能移除负责人
            if member.role == ProjectMember.MemberRole.LEADER:
                return Response(
                    {"code": 400, "message": "不能移除项目负责人"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            member.delete()
            return Response({"code": 200, "message": "成员移除成功"})
        except ProjectMember.DoesNotExist:
            return Response(
                {"code": 404, "message": "成员不存在"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(methods=["get"], detail=True)
    def progress(self, request, pk=None):
        """
        获取项目进度列表
        """
        project = self.get_object()
        progress_list = project.progress_records.all()
        serializer = ProjectProgressSerializer(progress_list, many=True)
        return Response({"code": 200, "data": serializer.data})

    @action(methods=["post"], detail=True, url_path="add-progress")
    def add_progress(self, request, pk=None):
        """
        添加项目进度
        """
        project = self.get_object()

        # 检查是否是项目成员
        if not ProjectMember.objects.filter(
            project=project, user=request.user
        ).exists():
            return Response(
                {"code": 403, "message": "只有项目成员可以添加进度"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ProjectProgressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(project=project, created_by=request.user)

        return Response(
            {"code": 200, "message": "进度添加成功", "data": serializer.data}
        )

    @action(methods=["post"], detail=True, url_path="apply-mid-term")
    def apply_mid_term(self, request, pk=None):
        """
        申请中期检查
        """
        project = self.get_object()

        # 检查权限
        if project.leader != request.user:
            return Response(
                {"code": 403, "message": "只有项目负责人可以申请中期检查"},
                status=status.HTTP_403_FORBIDDEN,
            )

        data = request.data.copy()
        data["project_id"] = project.id
        serializer = ProjectMidTermSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        mid_term_report = serializer.validated_data.get("mid_term_report")
        is_draft = serializer.validated_data.get("is_draft", False)

        try:
            if not is_draft:
                ok, msg = SystemSettingService.check_window(
                    "MIDTERM_WINDOW", timezone.now().date(), batch=project.batch
                )
                if not ok:
                    return Response(
                        {"code": 400, "message": msg or "当前不在中期提交时间范围内"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            ProjectService.apply_mid_term(project, mid_term_report, is_draft)
            message = "中期检查已保存为草稿" if is_draft else "中期检查申请提交成功"
            
            # 如果是正式提交，创建导师审核任务
            if not is_draft:
                 ReviewService.create_mid_term_teacher_review(project)
                 
            return Response({"code": 200, "message": message})
        except ValueError as e:
            return Response(
                {"code": 400, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(methods=["post"], detail=True, url_path="submit-mid-term")
    def submit_mid_term(self, request, pk=None):
        """
        提交中期检查（从草稿状态）
        """
        project = self.get_object()

        # 检查权限
        if project.leader != request.user:
            return Response(
                {"code": 403, "message": "只有项目负责人可以提交中期检查"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            ok, msg = SystemSettingService.check_window(
                "MIDTERM_WINDOW", timezone.now().date(), batch=project.batch
            )
            if not ok:
                return Response(
                    {"code": 400, "message": msg or "当前不在中期提交时间范围内"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if ProjectService.submit_mid_term(project):
                # 创建导师审核任务
                ReviewService.create_mid_term_teacher_review(project)
                return Response({"code": 200, "message": "中期检查申请提交成功"})
            else:
                return Response(
                    {"code": 400, "message": "项目状态不允许提交"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except ValueError as e:
            return Response(
                {"code": 400, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(methods=["post"], detail=True, url_path="apply-closure")
    def apply_closure(self, request, pk=None):
        """
        申请项目结题
        """
        project = self.get_object()

        # 检查权限
        if project.leader != request.user:
            return Response(
                {"code": 403, "message": "只有项目负责人可以申请结题"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ProjectClosureSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        is_draft = serializer.validated_data.get("is_draft", False)
        final_report = serializer.validated_data.get("final_report")

        try:
            if not is_draft:
                ok, msg = SystemSettingService.check_window(
                    "CLOSURE_WINDOW", timezone.now().date(), batch=project.batch
                )
                if not ok:
                    return Response(
                        {"code": 400, "message": msg or "当前不在结题提交时间范围内"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            ProjectService.apply_closure(project, final_report, is_draft)
            if not is_draft:
                ReviewService.create_closure_teacher_review(project)
            message = "结题申请已保存为草稿" if is_draft else "结题申请提交成功"
            return Response({"code": 200, "message": message})
        except ValueError as e:
            return Response(
                {"code": 400, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(methods=["post"], detail=True, url_path="submit-closure")
    def submit_closure(self, request, pk=None):
        """
        提交结题申请（从草稿状态）
        """
        project = self.get_object()

        # 检查权限
        if project.leader != request.user:
            return Response(
                {"code": 403, "message": "只有项目负责人可以提交结题"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            ok, msg = SystemSettingService.check_window(
                "CLOSURE_WINDOW", timezone.now().date(), batch=project.batch
            )
            if not ok:
                return Response(
                    {"code": 400, "message": msg or "当前不在结题提交时间范围内"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if ProjectService.submit_closure(project):
                # 创建导师审核记录
                ReviewService.create_closure_teacher_review(project)
                return Response({"code": 200, "message": "结题申请提交成功"})
            else:
                return Response(
                    {"code": 400, "message": "项目状态不允许提交"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except ValueError as e:
            return Response(
                {"code": 400, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(methods=["post"], detail=True, url_path="revoke-closure")
    def revoke_closure(self, request, pk=None):
        """
        撤销结题申请
        """
        project = self.get_object()

        # 检查权限
        if project.leader != request.user:
            return Response(
                {"code": 403, "message": "只有项目负责人可以撤销申请"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if ProjectService.revoke_closure(project):
            return Response({"code": 200, "message": "结题申请已撤销"})
        else:
            return Response(
                {"code": 400, "message": "项目状态不允许撤销"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(methods=["get"], detail=True)
    def achievements(self, request, pk=None):
        """
        获取项目成果列表
        """
        project = self.get_object()
        achievements = project.achievements.all()
        serializer = ProjectAchievementSerializer(achievements, many=True)
        return Response({"code": 200, "data": serializer.data})

    @action(methods=["post"], detail=True, url_path="add-achievement")
    def add_achievement(self, request, pk=None):
        """
        添加项目成果
        """
        project = self.get_object()

        # 检查权限
        if project.leader != request.user:
            return Response(
                {"code": 403, "message": "只有项目负责人可以添加成果"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # 检查项目状态
        allowed_statuses = [
            Project.ProjectStatus.IN_PROGRESS,
            Project.ProjectStatus.CLOSURE_DRAFT,
            Project.ProjectStatus.CLOSURE_SUBMITTED,
        ]
        if project.status not in allowed_statuses:
            return Response(
                {"code": 400, "message": "当前项目状态不允许添加成果"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ProjectAchievementSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(project=project)

        return Response(
            {"code": 200, "message": "成果添加成功", "data": serializer.data}
        )

    @action(
        methods=["delete"],
        detail=True,
        url_path="remove-achievement/(?P<achievement_id>[^/.]+)",
    )
    def remove_achievement(self, request, pk=None, achievement_id=None):
        """
        删除项目成果
        """
        project = self.get_object()

        # 检查权限
        if project.leader != request.user:
            return Response(
                {"code": 403, "message": "只有项目负责人可以删除成果"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            achievement = ProjectAchievement.objects.get(
                project=project, id=achievement_id
            )
            achievement.delete()
            return Response({"code": 200, "message": "成果删除成功"})
        except ProjectAchievement.DoesNotExist:
            return Response(
                {"code": 404, "message": "成果不存在"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(methods=["post"], detail=True, url_path="update-ranking")
    def update_ranking(self, request, pk=None):
        """
        更新项目排名（仅二级管理员）
        """
        project = self.get_object()
        user = request.user

        # 检查权限
        if not user.is_level2_admin or project.leader.college != user.college:
            return Response(
                {"code": 403, "message": "无权限修改此项目排名"},
                status=status.HTTP_403_FORBIDDEN,
            )

        ranking = request.data.get("ranking")
        if ranking is None:
            return Response(
                {"code": 400, "message": "请提供排名"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        project.ranking = ranking
        project.save()

        return Response({"code": 200, "message": "排名更新成功"})

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

        # 获取本学院的项目
        projects = Project.objects.filter(leader__college=user.college)

        # 应用筛选条件
        status_filter = request.query_params.get("status")
        if status_filter:
            projects = projects.filter(status=status_filter)

        # 创建Excel工作簿
        import openpyxl
        from django.http import HttpResponse

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "项目列表"

        # 写入表头
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

        # 写入数据
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

        # 调整列宽
        for column in ws.columns:
            max_length = 0
            column = [cell for cell in column]
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2) * 1.2
            ws.column_dimensions[column[0].column_letter].width = adjusted_width

        # 返回Excel文件
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

        # 获取本学院的项目
        projects = Project.objects.filter(leader__college=user.college)

        # 应用筛选条件
        status_filter = request.query_params.get("status")
        if status_filter:
            projects = projects.filter(status=status_filter)

        # 创建ZIP文件
        from io import BytesIO
        import zipfile
        from django.http import HttpResponse

        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for project in projects:
                # 添加申报书
                if project.proposal_file:
                    try:
                        file_path = project.proposal_file.path
                        zip_file.write(
                            file_path,
                            f"{project.project_no}/申报书_{project.proposal_file.name.split('/')[-1]}",
                        )
                    except Exception as e:
                        pass

                # 添加中期报告
                if project.mid_term_report:
                    try:
                        file_path = project.mid_term_report.path
                        zip_file.write(
                            file_path,
                            f"{project.project_no}/中期报告_{project.mid_term_report.name.split('/')[-1]}",
                        )
                    except Exception:
                        pass

                # 添加结题报告
                if project.final_report:
                    try:
                        file_path = project.final_report.path
                        zip_file.write(
                            file_path,
                            f"{project.project_no}/结题报告_{project.final_report.name.split('/')[-1]}",
                        )
                    except Exception as e:
                        pass

                # 添加成果附件
                for achievement in project.achievements.all():
                    if achievement.attachment:
                        try:
                            file_path = achievement.attachment.path
                            zip_file.write(
                                file_path,
                                f"{project.project_no}/成果_{achievement.title}_{achievement.attachment.name.split('/')[-1]}",
                            )
                        except Exception as e:
                            pass

        # 返回ZIP文件
        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer.read(), content_type="application/zip")
        response["Content-Disposition"] = (
            f'attachment; filename="attachments_{user.college}.zip"'
        )
        return response


class ProjectProgressViewSet(viewsets.ReadOnlyModelViewSet):
    """
    项目进度视图集（只读）
    """

    queryset = ProjectProgress.objects.all()
    serializer_class = ProjectProgressSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["project"]
    ordering_fields = ["created_at"]


class ProjectAchievementViewSet(viewsets.ModelViewSet):
    """
    项目成果视图集
    """

    queryset = ProjectAchievement.objects.all()
    serializer_class = ProjectAchievementSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["project", "achievement_type"]
    ordering_fields = ["created_at"]

    def get_queryset(self):
        """
        根据用户角色过滤成果
        """
        from django.db.models import Q

        user = self.request.user
        queryset = super().get_queryset()

        # 学生只能看到自己参与项目的成果
        if user.is_student:
            queryset = queryset.filter(
                Q(project__leader=user) | Q(project__members=user)
            ).distinct()
        # 二级管理员只能看到本学院项目的成果
        elif user.is_level2_admin:
            queryset = queryset.filter(project__leader__college=user.college)

        return queryset


class ProjectExpenditureViewSet(viewsets.ModelViewSet):
    """
    项目经费视图集
    """
    queryset = ProjectExpenditure.objects.all()
    serializer_class = ProjectExpenditureSerializer
    permission_classes = [IsAuthenticated]

    filterset_fields = ["project"]

    def _can_manage_expenditure(self, user, project):
        if user.is_level1_admin or user.is_level2_admin:
            return True
        if user.is_student:
            return project.leader_id == user.id or project.members.filter(id=user.id).exists()
        if user.role == "TEACHER":
            return project.advisors.filter(user=user).exists()
        return False

    def _ensure_project_status(self, project):
        allowed_statuses = {
            Project.ProjectStatus.IN_PROGRESS,
            Project.ProjectStatus.MID_TERM_DRAFT,
            Project.ProjectStatus.MID_TERM_SUBMITTED,
            Project.ProjectStatus.MID_TERM_REVIEWING,
            Project.ProjectStatus.MID_TERM_APPROVED,
            Project.ProjectStatus.MID_TERM_REJECTED,
            Project.ProjectStatus.CLOSURE_DRAFT,
            Project.ProjectStatus.CLOSURE_SUBMITTED,
            Project.ProjectStatus.CLOSURE_LEVEL2_REVIEWING,
            Project.ProjectStatus.CLOSURE_LEVEL2_APPROVED,
            Project.ProjectStatus.CLOSURE_LEVEL2_REJECTED,
            Project.ProjectStatus.CLOSURE_LEVEL1_REVIEWING,
            Project.ProjectStatus.CLOSURE_LEVEL1_APPROVED,
            Project.ProjectStatus.CLOSURE_LEVEL1_REJECTED,
        }
        return project.status in allowed_statuses

    def perform_create(self, serializer):
        project = serializer.validated_data["project"]
        amount = serializer.validated_data["amount"]

        if not self._can_manage_expenditure(self.request.user, project):
            raise PermissionDenied("无权限录入该项目经费")

        if not self._ensure_project_status(project):
            raise serializers.ValidationError("当前项目状态不允许录入经费")
        
        # 验证余额
        stats = ProjectService.get_budget_stats(project)
        if amount > stats["remaining_amount"]:
            raise serializers.ValidationError(
                f"余额不足！当前剩余经费：{stats['remaining_amount']}元，本次申请：{amount}元"
            )
            
        serializer.save(created_by=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return Response(
                {
                    "code": 200,
                    "message": "获取成功",
                    "data": {
                        "results": serializer.data,
                        "count": self.paginator.page.paginator.count,
                    },
                }
            )

        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "code": 200,
                "message": "获取成功",
                "data": {"results": serializer.data, "count": len(serializer.data)},
            }
        )

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except serializers.ValidationError as e:
             raise e
        except ValueError as e:
            return Response(
                {"code": 400, "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, "is_student") and user.is_student:
            from django.db.models import Q

            return ProjectExpenditure.objects.filter(
                Q(project__leader=user) | Q(project__members=user)
            ).distinct()
        if user.role == "TEACHER":
            return ProjectExpenditure.objects.filter(
                project__advisors__user=user
            ).distinct()
        if user.is_level2_admin:
            return ProjectExpenditure.objects.filter(
                project__leader__college=user.college
            )
        return ProjectExpenditure.objects.all()

