"""
审核管理视图
"""

from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.notifications.services import NotificationService
from apps.projects.models import Project
from apps.system_settings.services import SystemSettingService

from ..models import Review
from ..serializers import ReviewActionSerializer, ReviewSerializer
from ..services import ReviewService


class ReviewViewSet(viewsets.ModelViewSet):
    """
    审核管理视图集
    """

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = [
        "status",
        "review_type",
        "review_level",
        "project",
        "project__status",
    ]
    search_fields = ["project__project_no", "project__title"]
    ordering_fields = ["created_at", "reviewed_at"]

    def get_queryset(self):
        """
        根据用户角色过滤审核记录
        """
        user = self.request.user
        queryset = super().get_queryset()

        # 学生只能看到自己项目的审核记录
        if user.is_student:
            queryset = queryset.filter(project__leader=user)
        # 二级管理员只能看到本学院的审核记录
        elif user.is_level2_admin:
            queryset = queryset.filter(
                project__leader__college=user.college,
                review_level=Review.ReviewLevel.LEVEL2,
            )
        # 一级管理员可以看到所有一级审核记录
        elif user.is_level1_admin:
            queryset = queryset.filter(review_level=Review.ReviewLevel.LEVEL1)
        # 指导教师只能看到分配给自己的审核
        elif user.is_teacher:
            queryset = queryset.filter(
                project__advisors__user=user, review_level=Review.ReviewLevel.TEACHER
            ).distinct()
        elif user.is_expert:
            queryset = queryset.filter(reviewer=user)

        status_in = self.request.query_params.get(
            "status_in"
        ) or self.request.query_params.get("status__in")
        if status_in:
            status_list = [s.strip() for s in status_in.split(",") if s.strip()]
            if status_list:
                queryset = queryset.filter(status__in=status_list)

        reviewer_isnull = self.request.query_params.get("reviewer_isnull")
        if reviewer_isnull in ("true", "false"):
            queryset = queryset.filter(reviewer__isnull=(reviewer_isnull == "true"))

        # Explicitly handle status and review_level to ensure strict filtering
        status_param = self.request.query_params.get("status")
        if status_param:
            queryset = queryset.filter(status=status_param)

        review_level_param = self.request.query_params.get("review_level")
        if review_level_param:
            queryset = queryset.filter(review_level=review_level_param)

        return queryset

    @action(methods=["post"], detail=True)
    def review(self, request, pk=None):
        """
        执行审核操作
        """
        review = self.get_object()
        user = request.user

        if (
            review.reviewer_id is None
            and review.review_level
            in (Review.ReviewLevel.LEVEL2, Review.ReviewLevel.LEVEL1)
            and review.review_type
            in (
                Review.ReviewType.APPLICATION,
                Review.ReviewType.MID_TERM,
                Review.ReviewType.CLOSURE,
            )
            and (user.is_level2_admin or user.is_level1_admin)
        ):
            return Response(
                {"code": 400, "message": "该环节需先分配专家评审，管理员不能直接审核"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 检查审核权限
        if not self.check_review_permission(review, user):
            return Response(
                {"code": 403, "message": "无权限审核此项目"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # 检查审核状态
        if review.status != Review.ReviewStatus.PENDING:
            return Response(
                {"code": 400, "message": "该审核记录已处理"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 验证请求数据
        serializer = ReviewActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action_type = serializer.validated_data["action"]
        comments = serializer.validated_data.get("comments", "")
        score = serializer.validated_data.get("score")
        score_details = serializer.validated_data.get("score_details")
        closure_rating = serializer.validated_data.get("closure_rating")
        reject_to = serializer.validated_data.get("reject_to")
        target_node_id = serializer.validated_data.get(
            "target_node_id"
        )  # 新增：退回目标节点ID

        if user.is_expert:
            ok, msg = SystemSettingService.check_window(
                "EXPERT_REVIEW_WINDOW",
                timezone.now().date(),
                batch=review.project.batch,
            )
            if not ok:
                return Response(
                    {"code": 400, "message": msg},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        ok, msg = SystemSettingService.check_review_window(
            review.review_type,
            review.review_level,
            timezone.now().date(),
            batch=review.project.batch,
        )
        if not ok:
            return Response(
                {"code": 400, "message": msg},
                status=status.HTTP_400_BAD_REQUEST,
            )

        review_rules = SystemSettingService.get_setting(
            "REVIEW_RULES", batch=review.project.batch
        )
        min_len = int(review_rules.get("teacher_application_comment_min", 0) or 0)
        if (
            min_len
            and review.review_level == Review.ReviewLevel.TEACHER
            and review.review_type == Review.ReviewType.APPLICATION
            and len(comments or "") < min_len
        ):
            return Response(
                {"code": 400, "message": f"审核意见至少{min_len}字"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if review.review_level == Review.ReviewLevel.TEACHER:
            score = None

        # 执行审核
        try:
            if action_type == "approve":
                result = ReviewService.approve_review(
                    review, user, comments, score, closure_rating, score_details
                )
            else:
                result = ReviewService.reject_review(
                    review, user, comments, reject_to, target_node_id
                )
        except ValueError as exc:
            return Response(
                {"code": 400, "message": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if result:
            NotificationService.notify_review_result(
                review.project, action_type == "approve", comments
            )
            return Response(
                {
                    "code": 200,
                    "message": "审核成功",
                    "data": ReviewSerializer(review).data,
                }
            )
        else:
            return Response(
                {"code": 500, "message": "审核失败"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(methods=["get"], detail=True, url_path="reject-targets")
    def get_reject_targets(self, request, pk=None):
        """
        获取当前审核记录可退回的目标节点列表
        """
        from apps.system_settings.services.workflow_service import WorkflowService
        review = self.get_object()

        # 检查权限
        if not self.check_review_permission(review, request.user):
            return Response(
                {"code": 403, "message": "无权限查看此审核的退回选项"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # 获取 phase_instance 和 current_node_id
        phase_instance = review.phase_instance
        if not phase_instance or not phase_instance.current_node_id:
            return Response(
                {"code": 200, "message": "该审核记录未配置工作流节点", "data": []}
            )

        # 获取可退回的节点
        reject_targets = WorkflowService.get_reject_target_nodes(
            phase_instance.current_node_id
        )

        # 转换为可序列化的格式
        target_list = []
        for target in reject_targets:
            target_list.append(
                {
                    "id": target.id,
                    "code": target.code,
                    "name": target.name,
                    "node_type": target.node_type,
                    "role": target.role,
                }
            )

        return Response({"code": 200, "message": "获取成功", "data": target_list})

    @action(methods=["post"], detail=True, url_path="revise")
    def revise(self, request, pk=None):
        """
        在评审时间范围内修改已审核结果/意见
        """
        review = self.get_object()
        user = request.user

        if not self.check_review_permission(review, user):
            return Response(
                {"code": 403, "message": "无权限修改此审核"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if review.status == Review.ReviewStatus.PENDING:
            return Response(
                {"code": 400, "message": "该审核记录尚未处理"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.is_expert:
            ok, msg = SystemSettingService.check_window(
                "EXPERT_REVIEW_WINDOW",
                timezone.now().date(),
                batch=review.project.batch,
            )
            if not ok:
                return Response(
                    {"code": 400, "message": msg},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        ok, msg = SystemSettingService.check_review_window(
            review.review_type,
            review.review_level,
            timezone.now().date(),
            batch=review.project.batch,
        )
        if not ok:
            return Response(
                {"code": 400, "message": msg},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ReviewActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action_type = serializer.validated_data["action"]
        comments = serializer.validated_data.get("comments", "")
        score = serializer.validated_data.get("score")
        score_details = serializer.validated_data.get("score_details")
        closure_rating = serializer.validated_data.get("closure_rating")
        reject_to = serializer.validated_data.get("reject_to")

        review_rules = SystemSettingService.get_setting(
            "REVIEW_RULES", batch=review.project.batch
        )
        min_len = int(review_rules.get("teacher_application_comment_min", 0) or 0)
        if (
            min_len
            and review.review_level == Review.ReviewLevel.TEACHER
            and review.review_type == Review.ReviewType.APPLICATION
            and len(comments or "") < min_len
        ):
            return Response(
                {"code": 400, "message": f"审核意见至少{min_len}字"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        review.status = (
            Review.ReviewStatus.APPROVED
            if action_type == "approve"
            else Review.ReviewStatus.REJECTED
        )
        review.comments = comments
        if score_details is not None:
            try:
                total_score, normalized_details = (
                    ReviewService._normalize_score_details(review, score, score_details)
                )
            except ValueError as exc:
                return Response(
                    {"code": 400, "message": str(exc)},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            review.score = total_score
            review.score_details = normalized_details
        else:
            review.score = score
        review.reviewer = user
        review.reviewed_at = timezone.now()
        if review.review_type == Review.ReviewType.CLOSURE:
            review.closure_rating = closure_rating
        else:
            review.closure_rating = None
        review.save()

        if action_type == "reject":
            ReviewService.reject_review(review, user, comments, reject_to)

        NotificationService.notify_review_result(
            review.project, action_type == "approve", comments
        )

        return Response(
            {
                "code": 200,
                "message": "审核结果已更新",
                "data": ReviewSerializer(review).data,
            }
        )

    @action(methods=["get"], detail=False)
    def pending(self, request):
        """
        获取待审核列表
        """
        user = request.user

        if user.is_level2_admin:
            # 二级管理员获取本学院待审核的项目
            queryset = Review.objects.filter(
                project__leader__college=user.college,
                review_level=Review.ReviewLevel.LEVEL2,
                status=Review.ReviewStatus.PENDING,
                reviewer__isnull=True,
            )
        elif user.is_level1_admin:
            # 一级管理员获取待一级审核的项目
            queryset = Review.objects.filter(
                review_level=Review.ReviewLevel.LEVEL1,
                status=Review.ReviewStatus.PENDING,
                reviewer__isnull=True,
            )
        else:
            return Response(
                {"code": 403, "message": "无权限访问"}, status=status.HTTP_403_FORBIDDEN
            )

        # 应用过滤和排序
        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({"code": 200, "data": serializer.data})

    def check_review_permission(self, review, user):
        """
        检查用户是否有权限审核
        """
        if review.reviewer_id:
            return review.reviewer_id == user.id
        if review.review_level == Review.ReviewLevel.LEVEL2:
            # 二级审核：必须是二级管理员且是同一学院
            project_college = (
                review.project.leader.college
                if review.project and review.project.leader
                else None
            )
            return user.is_level2_admin and user.college == project_college
        elif review.review_level == Review.ReviewLevel.LEVEL1:
            # 一级审核：必须是一级管理员
            return user.is_level1_admin
        elif review.review_level == Review.ReviewLevel.TEACHER:
            # 导师审核：必须是该项目的导师
            # Check if user is in project advisors
            return (
                user.is_teacher and review.project.advisors.filter(user=user).exists()
            )
        return False

    @action(methods=["post"], detail=False, url_path="batch-review")
    def batch_review(self, request):
        """
        批量审核
        """
        review_ids = request.data.get("review_ids", [])
        action_type = request.data.get("action")
        comments = request.data.get("comments", "")
        score = request.data.get("score")
        score_details = request.data.get("score_details")
        closure_rating = request.data.get("closure_rating")
        reject_to = request.data.get("reject_to")

        if not isinstance(review_ids, list) or not review_ids:
            return Response(
                {"code": 400, "message": "请提供review_ids"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if action_type not in ["approve", "reject"]:
            return Response(
                {"code": 400, "message": "无效的审核动作"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        success = 0
        failed = []
        for review in Review.objects.filter(
            id__in=review_ids, status=Review.ReviewStatus.PENDING
        ):
            if (
                review.reviewer_id is None
                and review.review_level
                in (Review.ReviewLevel.LEVEL2, Review.ReviewLevel.LEVEL1)
                and review.review_type
                in (
                    Review.ReviewType.APPLICATION,
                    Review.ReviewType.MID_TERM,
                    Review.ReviewType.CLOSURE,
                )
                and (request.user.is_level2_admin or request.user.is_level1_admin)
            ):
                failed.append({"id": review.id, "reason": "需先分配专家评审"})
                continue
            if not self.check_review_permission(review, request.user):
                failed.append({"id": review.id, "reason": "无权限"})
                continue
            if request.user.is_expert:
                ok, msg = SystemSettingService.check_window(
                    "EXPERT_REVIEW_WINDOW",
                    timezone.now().date(),
                    batch=review.project.batch,
                )
                if not ok:
                    failed.append(
                        {"id": review.id, "reason": msg or "不在评审时间范围内"}
                    )
                    continue
            ok, msg = SystemSettingService.check_review_window(
                review.review_type,
                review.review_level,
                timezone.now().date(),
                batch=review.project.batch,
            )
            if not ok:
                failed.append({"id": review.id, "reason": msg or "不在审核时间范围内"})
                continue
            try:
                if action_type == "approve":
                    ReviewService.approve_review(
                        review,
                        request.user,
                        comments,
                        score,
                        closure_rating,
                        score_details,
                    )
                else:
                    ReviewService.reject_review(
                        review, request.user, comments, reject_to
                    )
            except ValueError as exc:
                failed.append({"id": review.id, "reason": str(exc)})
                continue
            NotificationService.notify_review_result(
                review.project, action_type == "approve", comments
            )
            success += 1

        return Response(
            {
                "code": 200,
                "message": "批量审核完成",
                "data": {"success": success, "failed": failed},
            }
        )

    @action(methods=["post"], detail=False, url_path="submit-to-level1")
    def submit_to_level1(self, request):
        """
        二级管理员提交项目到一级审核
        """
        user = request.user
        if not user.is_level2_admin:
            return Response(
                {"code": 403, "message": "只有二级管理员可以提交到一级审核"},
                status=status.HTTP_403_FORBIDDEN,
            )

        project_id = request.data.get("project_id")
        if not project_id:
            return Response(
                {"code": 400, "message": "请提供项目ID"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            project = Project.objects.get(id=project_id, leader__college=user.college)

            # 检查二级审核是否已通过
            from ..models import Review

            level2_passed = Review.objects.filter(
                project=project,
                review_type=Review.ReviewType.APPLICATION,
                review_level=Review.ReviewLevel.LEVEL2,
                status=Review.ReviewStatus.APPROVED,
            ).exists()
            if not level2_passed:
                return Response(
                    {"code": 400, "message": "项目必须先通过二级审核"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 创建一级审核记录
            review = ReviewService.create_level1_review(project)

            # 更新项目状态
            project.status = Project.ProjectStatus.LEVEL1_AUDITING
            project.save(update_fields=["status"])

            return Response(
                {
                    "code": 200,
                    "message": "已提交至一级管理员审核",
                    "data": ReviewSerializer(review).data,
                }
            )
        except Project.DoesNotExist:
            return Response(
                {"code": 404, "message": "项目不存在"}, status=status.HTTP_404_NOT_FOUND
            )
