"""
用户管理相关视图（管理员）
"""

import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.contrib.auth.hashers import make_password
from django.conf import settings

from ...models import User
from ...password_validation import get_password_validation_errors
from ...permissions import IsAdmin
from ...serializers import UserSerializer, UserCreateSerializer
from ...services import UserService
from apps.utils.pagination import positive_int_query

logger = logging.getLogger(__name__)


def has_school_admin_scope(user):
    return user.is_school_admin or user.is_level1_admin


def admin_role_filter():
    return Q(role_fk__scope_dimension__isnull=False) | Q(
        role_fk__code__in=[
            User.UserRole.LEVEL1_ADMIN,
            User.UserRole.LEVEL2_ADMIN,
        ]
    )


class AdminUserViewSet(viewsets.ModelViewSet):
    """
    用户管理视图集（管理员）
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_service = UserService()

    def _resp(self, request, payload, status_code=status.HTTP_200_OK):
        return Response(payload, status=status_code)

    def _user_snapshot(self, user: User):
        return {
            "id": user.id,
            "employee_id": user.employee_id,
            "real_name": user.real_name,
            "is_active": user.is_active,
            "is_expert": user.is_expert,
            "role": user.role_fk.code if user.role_fk else None,
            "college": user.college,
        }

    def _password_error_response(self, request, password, user=None):
        errors = get_password_validation_errors(password, user=user)
        if not errors:
            return None
        return self._resp(
            request,
            {
                "code": 400,
                "message": "密码不符合强度要求",
                "errors": {"password": errors},
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

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
        is_admin = self.request.query_params.get("is_admin", "")

        if is_admin and is_admin.lower() == "true":
            queryset = queryset.filter(admin_role_filter())
        elif role:
            if role == User.UserRole.EXPERT:
                queryset = queryset.filter(
                    Q(role_fk__code=User.UserRole.TEACHER)
                    | Q(role_fk__scope_dimension__isnull=False),
                    is_expert=True,
                )
            elif role == User.UserRole.TEACHER:
                queryset = queryset.filter(
                    Q(role_fk__code=User.UserRole.TEACHER)
                    | Q(role_fk__scope_dimension__isnull=False)
                )
            else:
                queryset = queryset.filter(role_fk__code=role)

        expert_scope = self.request.query_params.get("expert_scope", "")
        if expert_scope:
            queryset = queryset.filter(expert_scope=expert_scope)

        is_expert = self.request.query_params.get("is_expert")
        if is_expert in ("true", "false"):
            queryset = queryset.filter(is_expert=is_expert == "true")

        if current_user.is_admin and not has_school_admin_scope(current_user):
            queryset = queryset.filter(
                Q(role_fk__code=User.UserRole.TEACHER)
                | Q(role_fk__scope_dimension__isnull=False)
            )
            if current_user.college:
                queryset = queryset.filter(college=current_user.college).filter(
                    Q(is_expert=False) | Q(expert_assigned_by=current_user)
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
        page = positive_int_query(request.query_params, "page", 1)
        page_size = positive_int_query(request.query_params, "page_size", 10, 100)

        total = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size
        users = queryset[start:end]

        serializer = self.get_serializer(users, many=True)

        return self._resp(
            request,
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
            },
        )

    def retrieve(self, request, *args, **kwargs):
        """
        获取用户详情
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return self._resp(
            request, {"code": 200, "message": "获取成功", "data": serializer.data}
        )

    def create(self, request, *args, **kwargs):
        """
        创建用户
        """
        if not (request.user.is_superuser or request.user.is_admin):
            return self._resp(
                request,
                {"code": 403, "message": "无权限创建用户"},
                status_code=status.HTTP_403_FORBIDDEN,
            )

        data = request.data.copy()
        data.setdefault("role", User.UserRole.STUDENT)

        if data.get("role_fk"):
            from ...models import Role

            role_obj = Role.objects.filter(pk=data.get("role_fk")).first()
            if role_obj and role_obj.code == User.UserRole.EXPERT:
                return self._resp(
                    request,
                    {
                        "code": 400,
                        "message": "不支持直接创建专家，请从教师中勾选",
                        "errors": {"role": "不支持直接创建专家，请从教师中勾选"},
                    },
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

        if request.user.is_admin and not has_school_admin_scope(request.user):
            return self._resp(
                request,
                {"code": 403, "message": "非校级管理员无权创建用户"},
                status_code=status.HTTP_403_FORBIDDEN,
            )

        if data.get("role") == User.UserRole.EXPERT:
            return self._resp(
                request,
                {"code": 400, "message": "不支持直接创建专家，请从教师中勾选"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # 设置默认密码
        if "password" not in data or not data["password"]:
            if not settings.DEFAULT_USER_PASSWORD:
                return self._resp(
                    request,
                    {
                        "code": 400,
                        "message": "请提供密码或配置 DEFAULT_USER_PASSWORD",
                    },
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            data["password"] = settings.DEFAULT_USER_PASSWORD

        serializer = self.get_serializer(data=data)
        if not serializer.is_valid():
            logger.warning("User creation validation errors: %s", serializer.errors)
            return self._resp(
                request,
                {"code": 400, "message": "参数校验失败", "errors": serializer.errors},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        self.perform_create(serializer)

        # 返回完整用户信息
        output_data = UserSerializer(serializer.instance).data

        return self._resp(
            request,
            {"code": 200, "message": "创建成功", "data": output_data},
            status_code=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        """
        更新用户信息
        """
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        before = self._user_snapshot(instance)
        if request.user.is_admin and not has_school_admin_scope(request.user):
            return self._resp(
                request,
                {"code": 403, "message": "非校级管理员无权修改用户信息"},
                status_code=status.HTTP_403_FORBIDDEN,
            )

        data = request.data.copy()
        password = data.pop("password", None)
        if data.get("role") == User.UserRole.EXPERT:
            return self._resp(
                request,
                {"code": 400, "message": "不支持直接设置专家角色，请从教师中勾选"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        if password:
            blocked = self._password_error_response(request, password, user=instance)
            if blocked is not None:
                return blocked
        self.perform_update(serializer)

        if password:
            instance.set_password(password)
            instance.save(update_fields=["password"])

        return self._resp(
            request, {"code": 200, "message": "更新成功", "data": serializer.data}
        )

    def destroy(self, request, *args, **kwargs):
        """
        删除用户
        """
        instance = self.get_object()
        before = self._user_snapshot(instance)
        if request.user.is_admin and not has_school_admin_scope(request.user):
            return self._resp(
                request,
                {"code": 403, "message": "非校级管理员无权删除用户"},
                status_code=status.HTTP_403_FORBIDDEN,
            )

        # 不允许删除自己
        if instance.id == request.user.id:
            return self._resp(
                request,
                {"code": 400, "message": "不能删除自己的账号"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        self.perform_destroy(instance)
        return self._resp(request, {"code": 200, "message": "删除成功"})

    @action(methods=["post"], detail=True, url_path="toggle-status")
    def toggle_status(self, request, pk=None):
        """
        启用/禁用用户
        """
        user = self.get_object()
        before = self._user_snapshot(user)
        if request.user.is_admin and not has_school_admin_scope(request.user):
            return self._resp(
                request,
                {"code": 403, "message": "非校级管理员无权修改用户状态"},
                status_code=status.HTTP_403_FORBIDDEN,
            )

        # 不允许禁用自己
        if user.id == request.user.id:
            return self._resp(
                request,
                {"code": 400, "message": "不能禁用自己的账号"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        user.is_active = not user.is_active
        user.save()

        return self._resp(
            request,
            {"code": 200, "message": f"用户已{'启用' if user.is_active else '禁用'}"}
        )

    @action(methods=["post"], detail=True, url_path="toggle-expert")
    def toggle_expert(self, request, pk=None):
        """
        勾选/取消专家资格
        """
        user = self.get_object()
        operator = request.user
        before = self._user_snapshot(user)

        if not operator.is_admin:
            return self._resp(
                request,
                {"code": 403, "message": "无权限设置专家资格"},
                status_code=status.HTTP_403_FORBIDDEN,
            )

        if not user.is_teacher:
            return self._resp(
                request,
                {"code": 400, "message": "仅教师可设置为专家"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if operator.is_admin and not has_school_admin_scope(operator):
            if not operator.college:
                return self._resp(
                    request,
                    {"code": 400, "message": "当前账号未设置学院信息"},
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            if user.college != operator.college:
                return self._resp(
                    request,
                    {"code": 403, "message": "无权限设置其他学院教师为专家"},
                    status_code=status.HTTP_403_FORBIDDEN,
                )
            if user.expert_assigned_by_id and user.expert_assigned_by_id != operator.id:
                return self._resp(
                    request,
                    {"code": 403, "message": "无权限修改其他管理员的专家"},
                    status_code=status.HTTP_403_FORBIDDEN,
                )

        desired = request.data.get("is_expert")
        if desired is None:
            desired_value = not user.is_expert
        else:
            desired_value = str(desired).lower() in ("true", "1", "yes")

        if desired_value:
            user.is_expert = True
            user.expert_assigned_by = operator
        else:
            if user.expert_assigned_by_id and not (
                has_school_admin_scope(operator)
                or user.expert_assigned_by_id == operator.id
            ):
                return self._resp(
                    request,
                    {"code": 403, "message": "无权限取消其他管理员的专家"},
                    status_code=status.HTTP_403_FORBIDDEN,
                )
            user.is_expert = False
            user.expert_assigned_by = None

        user.save(update_fields=["is_expert", "expert_assigned_by"])
        return self._resp(
            request,
            {
                "code": 200,
                "message": "专家资格已更新",
                "data": {"is_expert": user.is_expert},
            }
        )

    @action(methods=["post"], detail=True, url_path="reset-password")
    def reset_password(self, request, pk=None):
        """
        重置用户密码
        """
        user = self.get_object()
        if request.user.is_admin and not has_school_admin_scope(request.user):
            return self._resp(
                request,
                {"code": 403, "message": "非校级管理员无权重置密码"},
                status_code=status.HTTP_403_FORBIDDEN,
            )

        new_password = request.data.get("password") or settings.DEFAULT_RESET_PASSWORD
        if not new_password:
            return self._resp(
                request,
                {"code": 400, "message": "请提供密码或配置 DEFAULT_RESET_PASSWORD"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        blocked = self._password_error_response(request, new_password, user=user)
        if blocked is not None:
            return blocked

        user.password = make_password(new_password)
        user.save()

        return self._resp(
            request,
            {
                "code": 200,
                "message": "密码已重置",
                "data": {"temporary_password_set": True},
            },
        )

    @action(methods=["get"], detail=False, url_path="statistics")
    def get_statistics(self, request):
        """
        获取用户统计数据
        """
        total_users = User.objects.count()
        student_count = User.objects.filter(role_fk__code="STUDENT").count()
        admin_count = User.objects.filter(admin_role_filter()).count()

        return self._resp(
            request,
            {
                "code": 200,
                "message": "获取成功",
                "data": {
                    "total_users": total_users,
                    "student_count": student_count,
                    "admin_count": admin_count,
                },
            },
        )

    @action(methods=["post"], detail=False, url_path="import_data")
    def import_data(self, request):
        """
        批量导入用户数据
        """
        file = request.FILES.get("file")
        role = request.data.get("role", "STUDENT")
        expert_scope = request.data.get("expert_scope")

        if not file:
            return self._resp(
                request,
                {"code": 400, "message": "未上传文件"},
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            current_user = request.user
            default_college = None

            # 非校级管理员权限检查
            if current_user.is_admin and not has_school_admin_scope(current_user):
                return self._resp(
                    request,
                    {"code": 403, "message": "非校级管理员无权导入用户"},
                    status_code=status.HTTP_403_FORBIDDEN,
                )

            if role == User.UserRole.EXPERT:
                return self._resp(
                    request,
                    {"code": 400, "message": "不支持直接导入专家，请先导入教师"},
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            result = self.user_service.import_users(
                file,
                role,
                expert_scope=expert_scope,
                default_college=default_college,
            )

            return self._resp(
                request,
                {
                    "code": 200,
                    "message": f"成功导入 {result['created']} 个用户",
                    "data": result,
                },
            )
        except ValueError as e:
            return self._resp(
                request,
                {"code": 400, "message": str(e)},
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            logger.exception("Error importing users")
            return self._resp(
                request,
                {"code": 500, "message": "导入失败，请稍后重试"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
