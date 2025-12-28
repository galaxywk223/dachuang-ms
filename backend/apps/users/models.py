# mypy: disable-error-code=var-annotated
"""
用户模型定义
支持三种角色：学生、二级管理员（学院级）、一级管理员（校级）
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class User(AbstractUser):
    """
    扩展的用户模型
    """

    class UserRole(models.TextChoices):
        STUDENT = "STUDENT", "学生"
        LEVEL2_ADMIN = "LEVEL2_ADMIN", "二级管理员"
        LEVEL1_ADMIN = "LEVEL1_ADMIN", "一级管理员"
        TEACHER = "TEACHER", "指导教师"
        EXPERT = "EXPERT", "评审专家"

    class ExpertScope(models.TextChoices):
        SCHOOL = "SCHOOL", "校级专家"
        COLLEGE = "COLLEGE", "院级专家"

    # 基本信息
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.STUDENT,
        verbose_name="角色",
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

    @property
    def is_student(self):
        return self.role == self.UserRole.STUDENT

    @property
    def is_level2_admin(self):
        return self.role == self.UserRole.LEVEL2_ADMIN

    @property
    def is_level1_admin(self):
        return self.role == self.UserRole.LEVEL1_ADMIN


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
