# mypy: disable-error-code=var-annotated
"""
项目模型定义
"""

from django.db import models
from django.conf import settings
from apps.dictionaries.models import DictionaryItem
from apps.system_settings.models import ProjectBatch


class Project(models.Model):
    """
    大创项目模型
    """

    class ProjectStatus(models.TextChoices):
        DRAFT = "DRAFT", "草稿"
        SUBMITTED = "SUBMITTED", "已提交"  # 提交给老师
        TEACHER_AUDITING = "TEACHER_AUDITING", "导师审核中"
        TEACHER_APPROVED = "TEACHER_APPROVED", "导师审核通过"
        TEACHER_REJECTED = "TEACHER_REJECTED", "导师审核不通过"
        COLLEGE_AUDITING = "COLLEGE_AUDITING", "学院审核中"  # Level 2
        LEVEL1_AUDITING = "LEVEL1_AUDITING", "校级审核中"
        APPLICATION_RETURNED = "APPLICATION_RETURNED", "立项退回修改"
        # Original IN_PROGRESS was likely used for "Approved and running".
        # Let's keep IN_PROGRESS for "Established".

        IN_PROGRESS = "IN_PROGRESS", "进行中"  # 立项成功
        MID_TERM_DRAFT = "MID_TERM_DRAFT", "中期草稿"
        MID_TERM_SUBMITTED = "MID_TERM_SUBMITTED", "中期已提交"
        MID_TERM_REVIEWING = "MID_TERM_REVIEWING", "中期审核中"
        READY_FOR_CLOSURE = "READY_FOR_CLOSURE", "待结题"
        MID_TERM_REJECTED = "MID_TERM_REJECTED", "中期审核不通过"
        MID_TERM_RETURNED = "MID_TERM_RETURNED", "中期退回修改"
        CLOSURE_DRAFT = "CLOSURE_DRAFT", "结题草稿"
        CLOSURE_SUBMITTED = "CLOSURE_SUBMITTED", "结题已提交"
        CLOSURE_LEVEL2_REVIEWING = "CLOSURE_LEVEL2_REVIEWING", "结题二级审核中"
        CLOSURE_LEVEL2_APPROVED = "CLOSURE_LEVEL2_APPROVED", "结题二级审核通过"
        CLOSURE_LEVEL2_REJECTED = "CLOSURE_LEVEL2_REJECTED", "结题二级审核不通过"
        CLOSURE_LEVEL1_REVIEWING = "CLOSURE_LEVEL1_REVIEWING", "结题一级审核中"
        CLOSURE_LEVEL1_APPROVED = "CLOSURE_LEVEL1_APPROVED", "结题一级审核通过"
        CLOSURE_LEVEL1_REJECTED = "CLOSURE_LEVEL1_REJECTED", "结题一级审核不通过"
        CLOSURE_RETURNED = "CLOSURE_RETURNED", "结题退回修改"
        COMPLETED = "COMPLETED", "已完成"
        CLOSED = "CLOSED", "已结题"
        TERMINATED = "TERMINATED", "已终止"

    # Removed local TextChoices for Level and Category as they are now DictionaryItems

    # 基本信息
    project_no = models.CharField(
        max_length=50, unique=True, verbose_name="项目编号", blank=True
    )
    batch = models.ForeignKey(
        ProjectBatch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="projects",
        verbose_name="项目批次",
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
    key_domain_code = models.CharField(
        max_length=50, blank=True, verbose_name="重点领域代码"
    )
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
    approved_budget = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="批准经费",
    )

    # 项目内容
    research_content = models.TextField(blank=True, verbose_name="研究内容")
    research_plan = models.TextField(blank=True, verbose_name="研究方案")
    expected_results = models.TextField(blank=True, verbose_name="预期成果")
    expected_results_data = models.JSONField(
        default=list, blank=True, verbose_name="预期成果清单"
    )
    innovation_points = models.TextField(blank=True, verbose_name="创新点")

    # 申报材料
    proposal_file = models.FileField(
        upload_to="proposals/",
        blank=True,
        null=True,
        verbose_name="申报书",
        max_length=255,
    )
    attachment_file = models.FileField(
        upload_to="attachments/",
        blank=True,
        null=True,
        verbose_name="上传文件",
        max_length=255,
    )
    # 中期检查材料
    mid_term_report = models.FileField(
        upload_to="mid_term_reports/",
        blank=True,
        null=True,
        verbose_name="中期检查报告",
        max_length=255,
    )

    # 结题材料
    final_report = models.FileField(
        upload_to="final_reports/",
        blank=True,
        null=True,
        verbose_name="结题报告",
        max_length=255,
    )
    achievement_file = models.FileField(
        upload_to="achievements/",
        blank=True,
        null=True,
        verbose_name="成果材料",
        max_length=255,
    )

    achievement_summary = models.TextField(
        blank=True, default="", verbose_name="结题成果简介"
    )

    # 状态信息
    status = models.CharField(
        max_length=30,
        choices=ProjectStatus.choices,
        default=ProjectStatus.DRAFT,
        verbose_name="项目状态",
    )

    # 项目排名（管理员可修改）
    ranking = models.IntegerField(null=True, blank=True, verbose_name="项目排名")

    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name="提交时间")
    mid_term_submitted_at = models.DateTimeField(
        null=True, blank=True, verbose_name="中期提交时间"
    )
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


class ProjectPhaseInstance(models.Model):
    """
    项目阶段实例（支持同一阶段多轮 attempt）
    """

    class Phase(models.TextChoices):
        APPLICATION = "APPLICATION", "立项"
        MID_TERM = "MID_TERM", "中期"
        CLOSURE = "CLOSURE", "结题"

    class State(models.TextChoices):
        IN_PROGRESS = "IN_PROGRESS", "进行中"
        RETURNED = "RETURNED", "已退回"
        COMPLETED = "COMPLETED", "已完成"

    class ReturnTo(models.TextChoices):
        STUDENT = "STUDENT", "退回学生"
        TEACHER = "TEACHER", "退回导师"

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="phase_instances",
        verbose_name="项目",
    )
    phase = models.CharField(max_length=20, choices=Phase.choices, verbose_name="阶段")
    attempt_no = models.PositiveIntegerField(default=1, verbose_name="轮次")
    step = models.CharField(max_length=50, default="", verbose_name="当前环节")
    # 当前流程节点ID，用于跟踪动态工作流位置
    current_node_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="当前流程节点ID",
        help_text="关联到 WorkflowNode.id，用于动态工作流引擎",
    )
    state = models.CharField(
        max_length=20,
        choices=State.choices,
        default=State.IN_PROGRESS,
        verbose_name="状态",
    )
    return_to = models.CharField(
        max_length=20,
        choices=ReturnTo.choices,
        blank=True,
        default="",
        verbose_name="退回对象",
    )
    returned_reason = models.TextField(blank=True, default="", verbose_name="退回原因")
    returned_at = models.DateTimeField(null=True, blank=True, verbose_name="退回时间")

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_phase_instances",
        verbose_name="创建人",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "project_phase_instances"
        verbose_name = "项目阶段实例"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "phase", "attempt_no"],
                name="uniq_project_phase_attempt",
            )
        ]

    def __str__(self):
        return f"{self.project.project_no} {self.phase}#{self.attempt_no} {self.step}({self.state})"


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
        upload_to="achievements/",
        blank=True,
        null=True,
        verbose_name="成果附件",
        max_length=255,
    )
    extra_data = models.JSONField(default=dict, blank=True, verbose_name="扩展信息")

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


class ProjectExpenditure(models.Model):
    """
    项目经费支出记录
    """

    class ExpenditureStatus(models.TextChoices):
        RECORDED = "RECORDED", "已录入"
        PENDING = "PENDING", "待审核"
        APPROVED = "APPROVED", "审核通过"
        REJECTED = "REJECTED", "审核不通过"

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="expenditures",
        verbose_name="项目",
    )
    title = models.CharField(max_length=200, verbose_name="支出事项")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="金额")
    expenditure_date = models.DateField(verbose_name="支出日期")

    proof_file = models.FileField(
        upload_to="expenditures/",
        blank=True,
        null=True,
        verbose_name="凭证文件",
        max_length=255,
    )

    status = models.CharField(
        max_length=20,
        choices=ExpenditureStatus.choices,
        default=ExpenditureStatus.RECORDED,
        verbose_name="状态",
    )

    # 审核相关字段
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_expenditures",
        verbose_name="审核人",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name="审核时间")
    review_comment = models.TextField(blank=True, verbose_name="审核意见")

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        verbose_name="创建人",
    )

    is_deleted = models.BooleanField(default=False, verbose_name="是否删除")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "project_expenditures"
        verbose_name = "经费支出"
        verbose_name_plural = verbose_name
        ordering = ["-expenditure_date", "-created_at"]
        indexes = [
            models.Index(fields=["project", "expenditure_date"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.project.project_no} - {self.title} - {self.amount}"


class ProjectChangeRequest(models.Model):
    """
    项目变更/延期/终止申请
    """

    class ChangeType(models.TextChoices):
        CHANGE = "CHANGE", "项目变更"
        TERMINATION = "TERMINATION", "项目终止"
        EXTENSION = "EXTENSION", "项目延期"

    class ChangeStatus(models.TextChoices):
        DRAFT = "DRAFT", "草稿"
        SUBMITTED = "SUBMITTED", "已提交"
        TEACHER_REVIEWING = "TEACHER_REVIEWING", "导师审核中"
        LEVEL2_REVIEWING = "LEVEL2_REVIEWING", "二级审核中"
        LEVEL1_REVIEWING = "LEVEL1_REVIEWING", "一级审核中"
        APPROVED = "APPROVED", "审核通过"
        REJECTED = "REJECTED", "审核不通过"

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="change_requests",
        verbose_name="项目",
    )
    request_type = models.CharField(
        max_length=20, choices=ChangeType.choices, verbose_name="申请类型"
    )
    reason = models.TextField(blank=True, verbose_name="申请原因")
    change_data = models.JSONField(null=True, blank=True, verbose_name="变更内容")
    requested_end_date = models.DateField(null=True, blank=True, verbose_name="延期至")
    attachment = models.FileField(
        upload_to="change_requests/",
        null=True,
        blank=True,
        verbose_name="附件",
        max_length=255,
    )
    status = models.CharField(
        max_length=30,
        choices=ChangeStatus.choices,
        default=ChangeStatus.DRAFT,
        verbose_name="状态",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_change_requests",
        verbose_name="申请人",
    )
    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name="提交时间")
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name="审核时间")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "project_change_requests"
        verbose_name = "项目变更申请"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.project.project_no} - {self.get_request_type_display()}"


class ProjectChangeReview(models.Model):
    """
    项目变更审核记录
    """

    class ReviewStatus(models.TextChoices):
        PENDING = "PENDING", "待审核"
        APPROVED = "APPROVED", "审核通过"
        REJECTED = "REJECTED", "审核不通过"

    change_request = models.ForeignKey(
        ProjectChangeRequest,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="变更申请",
    )
    workflow_node = models.ForeignKey(
        "system_settings.WorkflowNode",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="change_reviews",
        verbose_name="关联工作流节点",
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="审核人",
    )
    status = models.CharField(
        max_length=20,
        choices=ReviewStatus.choices,
        default=ReviewStatus.PENDING,
        verbose_name="审核状态",
    )
    comments = models.TextField(blank=True, verbose_name="审核意见")
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name="审核时间")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = "project_change_reviews"
        verbose_name = "项目变更审核"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]

    def __str__(self):
        role_code = (
            self.workflow_node.get_role_code() if self.workflow_node else "UNKNOWN"
        )
        return f"{self.change_request.project.project_no} - {role_code}"


class ProjectArchive(models.Model):
    """
    项目归档记录
    """

    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name="archive",
        verbose_name="项目",
    )
    snapshot = models.JSONField(default=dict, verbose_name="项目快照")
    attachments = models.JSONField(default=list, verbose_name="附件清单")
    metadata = models.JSONField(default=dict, blank=True, verbose_name="归档元数据")
    archived_at = models.DateTimeField(auto_now_add=True, verbose_name="归档时间")

    class Meta:
        db_table = "project_archives"
        verbose_name = "项目归档"
        verbose_name_plural = verbose_name
        ordering = ["-archived_at"]
        indexes = [
            models.Index(fields=["-archived_at"]),
        ]

    def __str__(self):
        return f"{self.project.project_no} - 归档"
