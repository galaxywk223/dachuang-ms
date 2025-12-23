"""
用户管理控制器
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ..serializers import UserSerializer, UserCreateSerializer
from ..business.user_business import UserBusiness
from ..repositories.login_log_repository import LoginLogRepository


class UserManagementController(viewsets.ModelViewSet):
    """
    用户管理控制器
    """

    permission_classes = [IsAuthenticated]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_business = UserBusiness()
        self.login_log_repository = LoginLogRepository()

    def get_serializer_class(self):
        """根据操作类型返回相应的序列化器"""
        if self.action == "create":
            return UserCreateSerializer
        return UserSerializer

    def get_queryset(self):
        """获取查询集"""
        filters = {}

        # 根据角色过滤
        role = self.request.query_params.get("role")
        if role:
            filters["role"] = role

        # 根据激活状态过滤
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            filters["is_active"] = is_active.lower() == "true"

        # 搜索
        search = self.request.query_params.get("search")
        if search:
            filters["search"] = search

        return self.user_business.get_user_list(filters)

    @action(methods=["post"], detail=True)
    def reset_password(self, request, pk=None):
        """
        重置用户密码
        """
        user = self.get_object()
        success = self.user_business.reset_password(user)

        if success:
            return Response({"message": "密码重置成功"}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "密码重置失败"}, status=status.HTTP_400_BAD_REQUEST
            )

    @action(methods=["post"], detail=True)
    def toggle_active(self, request, pk=None):
        """
        切换用户激活状态
        """
        user = self.get_object()
        new_status = self.user_business.toggle_user_active(user)

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
        
        if not file:
             return Response({"code": 400, "message": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            result = self.user_business.import_users(file, role)
            return Response({
                "code": 200, 
                "message": f"Imported {result['created']} users.",
                "data": result
            })
        except Exception as e:
            return Response({"code": 500, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
