"""
项目模型定义
"""

from django.db import models
from django.conf import settings


class Project(models.Model):
    """
    大创项目模型
    """

    class ProjectStatus(models.TextChoices):
        DRAFT = "DRAFT", "草稿"
        SUBMITTED = "SUBMITTED", "已提交"
        LEVEL2_REVIEWING = "LEVEL2_REVIEWING", "二级审核中"
        LEVEL2_APPROVED = "LEVEL2_APPROVED", "二级审核通过"
        LEVEL2_REJECTED = "LEVEL2_REJECTED", "二级审核不通过"
        LEVEL1_REVIEWING = "LEVEL1_REVIEWING", "一级审核中"
        LEVEL1_APPROVED = "LEVEL1_APPROVED", "一级审核通过"
        LEVEL1_REJECTED = "LEVEL1_REJECTED", "一级审核不通过"
        IN_PROGRESS = "IN_PROGRESS", "进行中"
        COMPLETED = "COMPLETED", "已完成"
        CLOSED = "CLOSED", "已结题"

    class ProjectLevel(models.TextChoices):
        NATIONAL = "NATIONAL", "国家级"
        PROVINCIAL = "PROVINCIAL", "省级"
        SCHOOL = "SCHOOL", "校级"

    # 基本信息
    project_no = models.CharField(max_length=50, unique=True, verbose_name="项目编号")
    title = models.CharField(max_length=200, verbose_name="项目名称")
    description = models.TextField(verbose_name="项目简介")
    level = models.CharField(
        max_length=20,
        choices=ProjectLevel.choices,
        default=ProjectLevel.SCHOOL,
        verbose_name="项目级别",
    )

    # 项目负责人
    leader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="led_projects",
        verbose_name="项目负责人",
    )

    # 项目成员
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="ProjectMember",
        related_name="joined_projects",
        verbose_name="项目成员",
    )

    # 指导老师
    advisor = models.CharField(max_length=50, verbose_name="指导教师")
    advisor_title = models.CharField(
        max_length=50, blank=True, verbose_name="指导教师职称"
    )

    # 项目详情
    category = models.CharField(max_length=100, verbose_name="项目类别")
    research_field = models.CharField(max_length=100, verbose_name="研究领域")
    keywords = models.CharField(max_length=200, blank=True, verbose_name="关键词")

    # 时间和经费
    start_date = models.DateField(null=True, blank=True, verbose_name="开始日期")
    end_date = models.DateField(null=True, blank=True, verbose_name="结束日期")
    budget = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="项目经费"
    )

    # 项目内容
    research_content = models.TextField(blank=True, verbose_name="研究内容")
    research_plan = models.TextField(blank=True, verbose_name="研究方案")
    expected_results = models.TextField(blank=True, verbose_name="预期成果")
    innovation_points = models.TextField(blank=True, verbose_name="创新点")

    # 申报材料
    proposal_file = models.FileField(
        upload_to="proposals/", blank=True, null=True, verbose_name="申报书"
    )

    # 结题材料
    final_report = models.FileField(
        upload_to="final_reports/", blank=True, null=True, verbose_name="结题报告"
    )
    achievement_file = models.FileField(
        upload_to="achievements/", blank=True, null=True, verbose_name="成果材料"
    )

    # 状态信息
    status = models.CharField(
        max_length=20,
        choices=ProjectStatus.choices,
        default=ProjectStatus.DRAFT,
        verbose_name="项目状态",
    )

    # 学院信息（用于二级管理员筛选）
    college = models.CharField(max_length=100, verbose_name="所属学院")

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name="提交时间")

    class Meta:
        db_table = "projects"
        verbose_name = "项目"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["project_no"]),
            models.Index(fields=["status"]),
            models.Index(fields=["college"]),
        ]

    def __str__(self):
        return f"{self.project_no} - {self.title}"


class ProjectMember(models.Model):
    """
    项目成员关联模型
    """

    class MemberRole(models.TextChoices):
        LEADER = "LEADER", "负责人"
        MEMBER = "MEMBER", "成员"

    project = models.ForeignKey(Project, on_delete=models.CASCADE, verbose_name="项目")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="成员"
    )
    role = models.CharField(
        max_length=20,
        choices=MemberRole.choices,
        default=MemberRole.MEMBER,
        verbose_name="角色",
    )
    join_date = models.DateField(auto_now_add=True, verbose_name="加入日期")
    contribution = models.TextField(blank=True, verbose_name="贡献说明")

    class Meta:
        db_table = "project_members"
        verbose_name = "项目成员"
        verbose_name_plural = verbose_name
        unique_together = ["project", "user"]

    def __str__(self):
        return f"{self.project.title} - {self.user.real_name}"


class ProjectProgress(models.Model):
    """
    项目进度记录
    """

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="progress_records",
        verbose_name="项目",
    )
    title = models.CharField(max_length=200, verbose_name="进度标题")
    content = models.TextField(verbose_name="进度内容")
    attachment = models.FileField(
        upload_to="progress/", blank=True, null=True, verbose_name="附件"
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name="创建人"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = "project_progress"
        verbose_name = "项目进度"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.project.title} - {self.title}"
