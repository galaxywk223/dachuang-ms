"""
项目经费视图
"""

from rest_framework import viewsets, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from ..models import Project, ProjectExpenditure
from ..serializers import ProjectExpenditureSerializer
from ..services import ProjectService

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
            Project.ProjectStatus.READY_FOR_CLOSURE,
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

