"""
用户视图
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ...serializers import UserSerializer, UserCreateSerializer
from ...models import User
from ...services.user_service import UserService
from ...repositories.login_log_repository import LoginLogRepository


class UserViewSet(viewsets.ModelViewSet):
    """
    用户视图集
    """

    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_service = UserService()
        self.login_log_repository = LoginLogRepository()

    def get_serializer_class(self):
        """根据操作类型返回相应的序列化器"""
        if self.action == "create":
            return UserCreateSerializer
        return UserSerializer

    def get_queryset(self):
        """获取查询集"""
        filters = {}
        current_user = self.request.user

        # 根据角色过滤
        role = self.request.query_params.get("role")
        if role:
            filters["role"] = role

        expert_scope = self.request.query_params.get("expert_scope")
        if expert_scope:
            filters["expert_scope"] = expert_scope

        # 根据激活状态过滤
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            filters["is_active"] = is_active.lower() == "true"

        # 搜索
        search = self.request.query_params.get("search")
        if search:
            filters["search"] = search

        if current_user.is_level2_admin:
            filters["role"] = User.UserRole.EXPERT
            if current_user.college:
                filters["college"] = current_user.college
                filters["expert_scope"] = User.ExpertScope.COLLEGE
            else:
                return User.objects.none()

        return self.user_service.get_user_list(filters)

    @action(methods=["post"], detail=True)
    def reset_password(self, request, pk=None):
        """
        重置用户密码
        """
        user = self.get_object()
        try:
            new_password = request.data.get("password")
            self.user_service.reset_password(user, new_password=new_password)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "密码重置成功"}, status=status.HTTP_200_OK)

    @action(methods=["post"], detail=True)
    def toggle_active(self, request, pk=None):
        """
        切换用户激活状态
        """
        user = self.get_object()
        new_status = self.user_service.toggle_user_active(user)

        return Response(
            {
                "message": f"用户已{'激活' if new_status else '禁用'}",
                "is_active": new_status,
            },
            status=status.HTTP_200_OK,
        )

    @action(methods=["get"], detail=True)
    def login_logs(self, request, pk=None):
        """
        获取用户登录日志
        """
        user = self.get_object()
        logs = self.login_log_repository.get_user_login_logs(user, limit=20)

        log_data = []
        for log in logs:
            log_data.append(
                {
                    "id": log.id,
                    "ip_address": log.ip_address,
                    "user_agent": log.user_agent,
                    "login_time": log.login_time,
                    "login_status": log.login_status,
                }
            )

        return Response(log_data, status=status.HTTP_200_OK)

    @action(methods=["post"], detail=False)
    def import_data(self, request):
        """
        批量导入用户数据
        """
        file = request.FILES.get("file")
        role = request.data.get("role", "STUDENT")
        expert_scope = request.data.get("expert_scope")
        
        if not file:
             return Response({"code": 400, "message": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            current_user = request.user
            default_college = None
            if current_user.is_level2_admin:
                if role != User.UserRole.EXPERT:
                    return Response(
                        {"code": 403, "message": "二级管理员仅可导入院级专家"},
                        status=status.HTTP_403_FORBIDDEN,
                    )
                if not current_user.college:
                    return Response(
                        {"code": 400, "message": "当前账号未设置学院信息"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                expert_scope = User.ExpertScope.COLLEGE
                default_college = current_user.college
            elif role == User.UserRole.EXPERT:
                expert_scope = expert_scope or User.ExpertScope.COLLEGE
                if expert_scope == User.ExpertScope.SCHOOL:
                    default_college = ""
            result = self.user_service.import_users(
                file,
                role,
                expert_scope=expert_scope,
                default_college=default_college,
            )
            return Response({
                "code": 200, 
                "message": f"Imported {result['created']} users.",
                "data": result
            })
        except Exception as e:
            return Response({"code": 500, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
