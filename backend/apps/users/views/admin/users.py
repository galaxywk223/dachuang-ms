"""
用户管理相关视图（管理员）
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.contrib.auth.hashers import make_password

from ...models import User
from ...serializers import UserSerializer, UserCreateSerializer


class AdminUserViewSet(viewsets.ModelViewSet):
    """
    用户管理视图集（管理员）
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """Use the create serializer when creating users so we can set passwords and defaults."""
        if self.action == "create":
            return UserCreateSerializer
        return self.serializer_class

    def get_queryset(self):
        """
        获取用户列表，支持筛选
        """
        queryset = User.objects.all().order_by("-created_at")
        current_user = self.request.user

        # 搜索
        search = self.request.query_params.get("search", "")
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search)
                | Q(employee_id__icontains=search)
                | Q(real_name__icontains=search)
            )

        college = self.request.query_params.get("college", "")
        if college:
            queryset = queryset.filter(college=college)

        # 按角色筛选
        role = self.request.query_params.get("role", "")
        if role:
            queryset = queryset.filter(role=role)

        expert_scope = self.request.query_params.get("expert_scope", "")
        if expert_scope:
            queryset = queryset.filter(expert_scope=expert_scope)

        if current_user.is_level2_admin:
            queryset = queryset.filter(role=User.UserRole.EXPERT)
            if current_user.college:
                queryset = queryset.filter(
                    college=current_user.college,
                    expert_scope=User.ExpertScope.COLLEGE,
                )
            else:
                queryset = queryset.none()

        # 按工号/学号精确筛选
        employee_id = self.request.query_params.get("employee_id", "")
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)

        return queryset

    def list(self, request, *args, **kwargs):
        """
        获取用户列表（分页）
        """
        queryset = self.get_queryset()

        # 分页
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))

        total = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size
        users = queryset[start:end]

        serializer = self.get_serializer(users, many=True)

        return Response(
            {
                "code": 200,
                "message": "获取成功",
                "data": {
                    "results": serializer.data,
                    "count": total,
                    "total": total,  # 向后兼容
                    "page": page,
                    "page_size": page_size,
                },
            }
        )

    def create(self, request, *args, **kwargs):
        """
        创建用户
        """
        if not (
            request.user.is_superuser
            or request.user.role == User.UserRole.LEVEL1_ADMIN
            or request.user.role == User.UserRole.LEVEL2_ADMIN
        ):
            return Response(
                {"code": 403, "message": "无权限创建用户"},
                status=status.HTTP_403_FORBIDDEN,
            )

        data = request.data.copy()
        data.setdefault("role", User.UserRole.STUDENT)

        if request.user.role == User.UserRole.LEVEL2_ADMIN:
            if data.get("role") != User.UserRole.EXPERT:
                return Response(
                    {"code": 403, "message": "二级管理员仅可创建院级专家"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            if not request.user.college:
                return Response(
                    {"code": 400, "message": "当前账号未设置学院信息"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            data["college"] = request.user.college
            data["expert_scope"] = User.ExpertScope.COLLEGE
        elif data.get("role") == User.UserRole.EXPERT:
            data.setdefault("expert_scope", User.ExpertScope.COLLEGE)
            if data.get("expert_scope") == User.ExpertScope.SCHOOL:
                data["college"] = ""
            elif not data.get("college"):
                return Response(
                    {"code": 400, "message": "院级专家需选择学院"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # 设置默认密码
        if "password" not in data or not data["password"]:
            data["password"] = "123456"

        serializer = self.get_serializer(data=data)
        if not serializer.is_valid():
            print(f"User Creation Validation Errors: {serializer.errors}")
            return Response(
                {"code": 400, "message": "参数校验失败", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        self.perform_create(serializer)

        # 返回完整用户信息
        output_data = UserSerializer(serializer.instance).data

        return Response(
            {"code": 200, "message": "创建成功", "data": output_data},
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        """
        更新用户信息
        """
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        if request.user.is_level2_admin:
            if instance.role != User.UserRole.EXPERT:
                return Response(
                    {"code": 403, "message": "二级管理员仅可管理院级专家"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            if request.user.college and instance.college != request.user.college:
                return Response(
                    {"code": 403, "message": "无权限管理其他学院专家"},
                    status=status.HTTP_403_FORBIDDEN,
                )

        data = request.data.copy()
        password = data.pop("password", None)
        if request.user.is_level2_admin:
            data["role"] = User.UserRole.EXPERT
            data["college"] = request.user.college
            data["expert_scope"] = User.ExpertScope.COLLEGE
        elif instance.role == User.UserRole.EXPERT:
            data.setdefault("expert_scope", instance.expert_scope)
            if data.get("expert_scope") == User.ExpertScope.SCHOOL:
                data["college"] = ""
            elif not data.get("college"):
                return Response(
                    {"code": 400, "message": "院级专家需选择学院"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if password:
            instance.set_password(password)
            instance.save(update_fields=["password"])

        return Response({"code": 200, "message": "更新成功", "data": serializer.data})

    def destroy(self, request, *args, **kwargs):
        """
        删除用户
        """
        instance = self.get_object()
        if request.user.is_level2_admin:
            if instance.role != User.UserRole.EXPERT:
                return Response(
                    {"code": 403, "message": "二级管理员仅可管理院级专家"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            if request.user.college and instance.college != request.user.college:
                return Response(
                    {"code": 403, "message": "无权限管理其他学院专家"},
                    status=status.HTTP_403_FORBIDDEN,
                )

        # 不允许删除自己
        if instance.id == request.user.id:
            return Response(
                {"code": 400, "message": "不能删除自己的账号"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.perform_destroy(instance)
        return Response({"code": 200, "message": "删除成功"})

    @action(methods=["post"], detail=True, url_path="toggle-status")
    def toggle_status(self, request, pk=None):
        """
        启用/禁用用户
        """
        user = self.get_object()
        if request.user.is_level2_admin:
            if user.role != User.UserRole.EXPERT:
                return Response(
                    {"code": 403, "message": "二级管理员仅可管理院级专家"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            if request.user.college and user.college != request.user.college:
                return Response(
                    {"code": 403, "message": "无权限管理其他学院专家"},
                    status=status.HTTP_403_FORBIDDEN,
                )

        # 不允许禁用自己
        if user.id == request.user.id:
            return Response(
                {"code": 400, "message": "不能禁用自己的账号"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.is_active = not user.is_active
        user.save()

        return Response(
            {"code": 200, "message": f"用户已{'启用' if user.is_active else '禁用'}"}
        )

    @action(methods=["post"], detail=True, url_path="reset-password")
    def reset_password(self, request, pk=None):
        """
        重置用户密码
        """
        user = self.get_object()
        if request.user.is_level2_admin:
            if user.role != User.UserRole.EXPERT:
                return Response(
                    {"code": 403, "message": "二级管理员仅可管理院级专家"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            if request.user.college and user.college != request.user.college:
                return Response(
                    {"code": 403, "message": "无权限管理其他学院专家"},
                    status=status.HTTP_403_FORBIDDEN,
                )

        # 重置为默认密码
        user.password = make_password("123456")
        user.save()

        return Response({"code": 200, "message": "密码已重置为: 123456"})

    @action(methods=["get"], detail=False, url_path="statistics")
    def get_statistics(self, request):
        """
        获取用户统计数据
        """
        total_users = User.objects.count()
        student_count = User.objects.filter(role="STUDENT").count()
        admin_count = User.objects.filter(
            role__in=["LEVEL1_ADMIN", "LEVEL2_ADMIN"]
        ).count()

        return Response(
            {
                "code": 200,
                "message": "获取成功",
                "data": {
                    "total_users": total_users,
                    "student_count": student_count,
                    "admin_count": admin_count,
                },
            }
        )
