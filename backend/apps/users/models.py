# mypy: disable-error-code=var-annotated
"""
用户模型定义
角色通过 Role 表自定义配置
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class Permission(models.Model):
    """
    权限定义表
    定义系统中所有可用的权限点
    """

    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="权限代码",
        help_text="如：manage_users, review_projects",
    )
    name = models.CharField(max_length=100, verbose_name="权限名称")
    description = models.TextField(blank=True, verbose_name="权限描述")
    category = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="权限分类",
        help_text="如：用户管理、项目管理、审核管理",
    )
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "permissions"
        verbose_name = "权限"
        verbose_name_plural = verbose_name
        ordering = ["category", "code"]

    def __str__(self):
        return f"{self.name}({self.code})"


class Role(models.Model):
    """
    角色定义表
    校级管理员可以自定义角色及其权限
    """

    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="角色代码",
        help_text="如：STUDENT, TEACHER, LEVEL1_ADMIN",
    )
    name = models.CharField(max_length=100, verbose_name="角色名称")
    permissions = models.ManyToManyField(
        Permission, blank=True, related_name="roles", verbose_name="权限列表"
    )
    scope_dimension = models.CharField(
        max_length=50,
        choices=[
            ("COLLEGE", "学院"),
            ("PROJECT_CATEGORY", "项目类别"),
            ("PROJECT_LEVEL", "项目级别"),
            ("PROJECT_SOURCE", "项目来源"),
            ("KEY_FIELD", "重点领域代码"),
        ],
        null=True,
        blank=True,
        verbose_name="数据范围维度",
        help_text="管理员角色的数据范围维度。非管理员角色留空。",
    )
    is_system = models.BooleanField(
        default=False, verbose_name="是否系统内置", help_text="系统内置角色不可删除"
    )
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    default_route = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="默认路由",
        help_text="登录后默认跳转的路由",
    )
    sort_order = models.IntegerField(default=0, verbose_name="排序")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "roles"
        verbose_name = "角色"
        verbose_name_plural = verbose_name
        ordering = ["sort_order", "code"]

    def __str__(self):
        return f"{self.name}({self.code})"

    def get_permissions(self):
        """获取角色的所有权限代码列表"""
        return list(
            self.permissions.filter(is_active=True).values_list("code", flat=True)
        )


class User(AbstractUser):
    """
    扩展的用户模型
    """

    class UserRole(models.TextChoices):
        """系统内置角色代码"""

        STUDENT = "STUDENT", "学生"
        TEACHER = "TEACHER", "指导教师"
        EXPERT = "EXPERT", "评审专家"
        LEVEL2_ADMIN = "LEVEL2_ADMIN", "院级管理员"
        LEVEL1_ADMIN = "LEVEL1_ADMIN", "校级管理员"

    class ExpertScope(models.TextChoices):
        SCHOOL = "SCHOOL", "校级专家"
        COLLEGE = "COLLEGE", "院级专家"

    # 基本信息 - 角色改为外键关联
    role_fk = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name="users",
        verbose_name="角色",
        null=True,  # 用于迁移过程
        blank=True,
    )

    # 学生使用学号，管理员使用工号
    employee_id = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="学号/工号",
        validators=[
            RegexValidator(regex="^[0-9a-zA-Z]+$", message="只能包含数字和字母")
        ],
    )

    real_name = models.CharField(max_length=50, verbose_name="真实姓名")
    phone = models.CharField(max_length=11, blank=True, verbose_name="手机号")
    email = models.EmailField(blank=True, verbose_name="邮箱")

    # 学生专属字段
    major = models.CharField(max_length=100, blank=True, verbose_name="专业")
    grade = models.CharField(max_length=10, blank=True, verbose_name="年级")
    class_name = models.CharField(max_length=50, blank=True, verbose_name="班级")
    gender = models.CharField(
        max_length=10,
        blank=True,
        choices=[("男", "男"), ("女", "女")],
        verbose_name="性别",
    )

    # 管理员专属字段
    college = models.CharField(max_length=100, blank=True, verbose_name="所属学院")
    department = models.CharField(max_length=100, blank=True, verbose_name="所属部门")
    title = models.CharField(max_length=50, blank=True, verbose_name="职称")

    expert_scope = models.CharField(
        max_length=20,
        choices=ExpertScope.choices,
        blank=True,
        default=ExpertScope.COLLEGE,
        verbose_name="专家级别",
    )
    is_expert = models.BooleanField(default=False, verbose_name="是否专家")
    expert_assigned_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_experts",
        verbose_name="专家设置人",
    )
    managed_scope_value = models.ForeignKey(
        "dictionaries.DictionaryItem",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_by_users",
        verbose_name="管理范围值",
        help_text="管理员用户负责的维度值（如学院、项目类别等）。对应角色的 scope_dimension。",
    )

    # 扩展字段
    avatar = models.ImageField(
        upload_to="avatars/", blank=True, null=True, verbose_name="头像"
    )
    is_active = models.BooleanField(default=True, verbose_name="是否激活")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "users"
        verbose_name = "用户"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.real_name}({self.employee_id})"

    def get_role_code(self):
        """获取角色代码，用于向后兼容"""
        return self.role_fk.code if self.role_fk else None

    def get_permissions(self):
        """获取用户的所有权限代码列表"""
        return self.role_fk.get_permissions() if self.role_fk else []

    def has_permission(self, permission_code):
        """检查用户是否拥有某个权限"""
        return permission_code in self.get_permissions()

    @property
    def is_student(self):
        """向后兼容的角色判断"""
        return self.role_fk is not None and self.role_fk.code == self.UserRole.STUDENT

    @property
    def is_level2_admin(self):
        """向后兼容的角色判断"""
        return (
            self.role_fk is not None and self.role_fk.code == self.UserRole.LEVEL2_ADMIN
        )

    @property
    def is_level1_admin(self):
        """向后兼容的角色判断"""
        return (
            self.role_fk is not None and self.role_fk.code == self.UserRole.LEVEL1_ADMIN
        )

    @property
    def is_admin(self):
        """通用管理员判断（支持多级管理员）"""
        role_code = self.get_role_code()
        return bool(role_code and role_code.endswith("_ADMIN"))

    @property
    def is_teacher(self):
        """向后兼容的角色判断"""
        role_code = self.get_role_code()
        return bool(
            role_code
            and (role_code == self.UserRole.TEACHER or role_code.endswith("_ADMIN"))
        )

    @property
    def is_expert_role(self):
        """向后兼容：基于角色的专家判断"""
        return self.role_fk is not None and self.role_fk.code == self.UserRole.EXPERT


class LoginLog(models.Model):
    """
    登录日志
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    login_time = models.DateTimeField(auto_now_add=True, verbose_name="登录时间")
    ip_address = models.GenericIPAddressField(verbose_name="IP地址")
    user_agent = models.CharField(max_length=200, blank=True, verbose_name="用户代理")
    login_status = models.BooleanField(default=True, verbose_name="登录状态")

    class Meta:
        db_table = "login_logs"
        verbose_name = "登录日志"
        verbose_name_plural = verbose_name
        ordering = ["-login_time"]

    def __str__(self):
        return f"{self.user.real_name} - {self.login_time}"
