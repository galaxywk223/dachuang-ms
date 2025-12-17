"""
项目模型定义
"""

from django.db import models
from django.conf import settings
from apps.dictionaries.models import DictionaryItem


class Project(models.Model):
    """
    大创项目模型
    """

    class ProjectStatus(models.TextChoices):
        DRAFT = "DRAFT", "草稿"
        SUBMITTED = "SUBMITTED", "已提交"
        IN_PROGRESS = "IN_PROGRESS", "进行中"
        CLOSURE_DRAFT = "CLOSURE_DRAFT", "结题草稿"
        CLOSURE_SUBMITTED = "CLOSURE_SUBMITTED", "结题已提交"
        CLOSURE_LEVEL2_REVIEWING = "CLOSURE_LEVEL2_REVIEWING", "结题二级审核中"
        CLOSURE_LEVEL2_APPROVED = "CLOSURE_LEVEL2_APPROVED", "结题二级审核通过"
        CLOSURE_LEVEL2_REJECTED = "CLOSURE_LEVEL2_REJECTED", "结题二级审核不通过"
        CLOSURE_LEVEL1_REVIEWING = "CLOSURE_LEVEL1_REVIEWING", "结题一级审核中"
        CLOSURE_LEVEL1_APPROVED = "CLOSURE_LEVEL1_APPROVED", "结题一级审核通过"
        CLOSURE_LEVEL1_REJECTED = "CLOSURE_LEVEL1_REJECTED", "结题一级审核不通过"
        COMPLETED = "COMPLETED", "已完成"
        CLOSED = "CLOSED", "已结题"

    # Removed local TextChoices for Level and Category as they are now DictionaryItems

    # 基本信息
    project_no = models.CharField(
        max_length=50, unique=True, verbose_name="项目编号", blank=True
    )
    year = models.IntegerField(verbose_name="项目年份", default=2025)
    title = models.CharField(max_length=200, verbose_name="项目名称")
    description = models.TextField(verbose_name="项目简介", blank=True)
    level = models.ForeignKey(
        DictionaryItem,
        on_delete=models.PROTECT,
        related_name="projects_level",
        verbose_name="项目级别",
        null=True,
        blank=True,
    )
    category = models.ForeignKey(
        DictionaryItem,
        on_delete=models.PROTECT,
        related_name="projects_category",
        verbose_name="项目类别",
        null=True,
        blank=True,
    )
    source = models.ForeignKey(
        DictionaryItem,
        on_delete=models.PROTECT,
        related_name="projects_source",
        verbose_name="项目来源",
        null=True,
        blank=True,
    )

    # 项目负责人信息
    leader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="led_projects",
        verbose_name="项目负责人",
    )
    # 移除 redundant fields: leader_student_id, leader_contact, leader_email
    # 这些信息应直接从 leader (User) 对象获取

    # 项目成员
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="ProjectMember",
        related_name="joined_projects",
        verbose_name="项目成员",
    )

    # 项目详情
    is_key_field = models.BooleanField(default=False, verbose_name="重点领域项目")
    key_domain_code = models.CharField(max_length=50, blank=True, verbose_name="重点领域代码")
    # 移除 redundant fields: college, major_code
    # 这些信息应直接从 leader 或 members 获取
    self_funding = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="项目自筹（元）"
    )
    category_description = models.TextField(
        blank=True, default="", verbose_name="立项类别描述"
    )

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
        upload_to="proposals/", blank=True, null=True, verbose_name="申报书", max_length=255
    )
    attachment_file = models.FileField(
        upload_to="attachments/", blank=True, null=True, verbose_name="上传文件", max_length=255
    )

    # 结题材料
    final_report = models.FileField(
        upload_to="final_reports/", blank=True, null=True, verbose_name="结题报告", max_length=255
    )
    achievement_file = models.FileField(
        upload_to="achievements/", blank=True, null=True, verbose_name="成果材料", max_length=255
    )

    # 状态信息
    status = models.CharField(
        max_length=30,
        choices=ProjectStatus.choices,
        default=ProjectStatus.DRAFT,
        verbose_name="项目状态",
    )

    # 项目排名（二级管理员可修改）
    ranking = models.IntegerField(null=True, blank=True, verbose_name="项目排名")

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name="提交时间")
    closure_applied_at = models.DateTimeField(
        null=True, blank=True, verbose_name="结题申请时间"
    )

    class Meta:
        db_table = "projects"
        verbose_name = "项目"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["project_no"]),
            models.Index(fields=["status"]),

        ]

    def __str__(self):
        return f"{self.project_no} - {self.title}"


class ProjectAdvisor(models.Model):
    """
    项目指导教师模型
    """

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="advisors", verbose_name="项目"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="advised_projects",
        verbose_name="指导教师",
    )
    order = models.IntegerField(default=0, verbose_name="排序")

    class Meta:
        db_table = "project_advisors"
        verbose_name = "项目指导教师"
        verbose_name_plural = verbose_name
        ordering = ["order"]

    def __str__(self):
        return f"{self.project.title} - {self.user.real_name}"


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
    # 移除 redundant fields: student_id, department
    # student_id = models.CharField(max_length=20, verbose_name="学号", blank=True)
    # department = models.CharField(max_length=100, verbose_name="成员姓名", blank=True)
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
        upload_to="progress/", blank=True, null=True, verbose_name="附件", max_length=255
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


class ProjectAchievement(models.Model):
    """
    项目研究成果模型
    支持多种类型的成果：论文、专利、软著、竞赛奖项等
    """

    # Removed local TextChoices for AchievementType as it is now DictionaryItems

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="achievements",
        verbose_name="项目",
    )
    achievement_type = models.ForeignKey(
        DictionaryItem,
        on_delete=models.PROTECT,
        verbose_name="成果类型",
        related_name="project_achievements",
    )
    title = models.CharField(max_length=200, verbose_name="成果名称")
    description = models.TextField(verbose_name="成果描述")

    # 论文相关字段
    authors = models.CharField(max_length=200, blank=True, verbose_name="作者")
    journal = models.CharField(max_length=200, blank=True, verbose_name="期刊/会议名称")
    publication_date = models.DateField(null=True, blank=True, verbose_name="发表日期")
    doi = models.CharField(max_length=100, blank=True, verbose_name="DOI")

    # 专利相关字段
    patent_no = models.CharField(max_length=100, blank=True, verbose_name="专利号")
    patent_type = models.CharField(max_length=50, blank=True, verbose_name="专利类型")
    applicant = models.CharField(max_length=200, blank=True, verbose_name="申请人")

    # 软著相关字段
    copyright_no = models.CharField(max_length=100, blank=True, verbose_name="登记号")
    copyright_owner = models.CharField(
        max_length=200, blank=True, verbose_name="著作权人"
    )

    # 竞赛相关字段
    competition_name = models.CharField(
        max_length=200, blank=True, verbose_name="竞赛名称"
    )
    award_level = models.CharField(max_length=50, blank=True, verbose_name="获奖等级")
    award_date = models.DateField(null=True, blank=True, verbose_name="获奖日期")

    # 附件
    attachment = models.FileField(
        upload_to="achievements/", blank=True, null=True, verbose_name="成果附件", max_length=255
    )

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "project_achievements"
        verbose_name = "项目成果"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["project", "achievement_type"]),
        ]

    def __str__(self):
        return f"{self.project.project_no} - {self.title}"
