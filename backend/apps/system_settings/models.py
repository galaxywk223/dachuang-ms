# mypy: disable-error-code=var-annotated
"""
系统设置模型
"""

from django.db import models
from django.conf import settings

from apps.dictionaries.models import DictionaryItem


class ProjectBatch(models.Model):
    """
    项目批次（多批次/多年度）
    """

    STATUS_DRAFT = "draft"
    STATUS_ACTIVE = "active"
    STATUS_FINISHED = "finished"
    STATUS_ARCHIVED = "archived"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "草稿"),
        (STATUS_ACTIVE, "进行中"),
        (STATUS_FINISHED, "已结束"),
        (STATUS_ARCHIVED, "已归档"),
    ]

    name = models.CharField(max_length=100, verbose_name="批次名称")
    year = models.IntegerField(verbose_name="年度")
    code = models.CharField(max_length=50, unique=True, verbose_name="批次编码")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
        verbose_name="批次状态",
    )
    is_current = models.BooleanField(default=False, verbose_name="是否当前批次")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    is_deleted = models.BooleanField(default=False, verbose_name="是否删除")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "project_batches"
        verbose_name = "项目批次"
        verbose_name_plural = verbose_name
        ordering = ["-year", "-created_at"]

    def __str__(self):
        return f"{self.name}({self.year})"


class SystemSetting(models.Model):
    """
    系统配置（JSON）
    """

    code = models.CharField(max_length=50, verbose_name="配置编码")
    name = models.CharField(max_length=100, verbose_name="配置名称")
    data = models.JSONField(default=dict, verbose_name="配置数据")
    batch = models.ForeignKey(
        ProjectBatch,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="settings",
        verbose_name="所属批次",
    )
    is_locked = models.BooleanField(default=False, verbose_name="是否锁定")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_settings",
        verbose_name="更新人",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "system_settings"
        verbose_name = "系统配置"
        verbose_name_plural = verbose_name
        ordering = ["code"]
        unique_together = ("code", "batch")

    def __str__(self):
        return f"{self.name}({self.code})"


class CertificateSetting(models.Model):
    """
    结题证书配置
    """

    name = models.CharField(max_length=100, verbose_name="模板名称")
    school_name = models.CharField(max_length=100, verbose_name="学校名称")
    issuer_name = models.CharField(max_length=100, verbose_name="证书发放单位")
    template_code = models.CharField(max_length=50, default="DEFAULT", verbose_name="模板编码")
    background_image = models.ImageField(
        upload_to="certificates/backgrounds/",
        null=True,
        blank=True,
        verbose_name="证书底图",
    )
    seal_image = models.ImageField(
        upload_to="certificates/seals/",
        null=True,
        blank=True,
        verbose_name="电子印章",
    )
    style_config = models.JSONField(default=dict, verbose_name="样式配置")
    project_level = models.ForeignKey(
        DictionaryItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="certificate_level_settings",
        verbose_name="适用项目级别",
    )
    project_category = models.ForeignKey(
        DictionaryItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="certificate_category_settings",
        verbose_name="适用项目类别",
    )
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_certificates",
        verbose_name="更新人",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "certificate_settings"
        verbose_name = "结题证书配置"
        verbose_name_plural = verbose_name
        ordering = ["-updated_at"]

    def __str__(self):
        return self.name


class WorkflowConfig(models.Model):
    """
    流程配置（按批次/阶段）
    """

    class Phase(models.TextChoices):
        APPLICATION = "APPLICATION", "立项"
        MID_TERM = "MID_TERM", "中期"
        CLOSURE = "CLOSURE", "结题"

    name = models.CharField(max_length=100, verbose_name="流程名称")
    phase = models.CharField(
        max_length=20, choices=Phase.choices, verbose_name="流程阶段"
    )
    batch = models.ForeignKey(
        ProjectBatch,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="workflow_configs",
        verbose_name="所属批次",
    )
    version = models.IntegerField(default=1, verbose_name="版本号")
    description = models.TextField(blank=True, default="", verbose_name="说明")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    is_locked = models.BooleanField(default=False, verbose_name="是否锁定")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_workflows",
        verbose_name="创建人",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_workflows",
        verbose_name="更新人",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "workflow_configs"
        verbose_name = "流程配置"
        verbose_name_plural = verbose_name
        ordering = ["-updated_at"]
        unique_together = ("phase", "batch", "version")

    def __str__(self):
        return f"{self.name}({self.phase})"


class ReviewTemplate(models.Model):
    """
    评审模板（评分项与权重）
    """

    class Scope(models.TextChoices):
        COLLEGE = "COLLEGE", "院级"
        SCHOOL = "SCHOOL", "校级"

    name = models.CharField(max_length=100, verbose_name="模板名称")
    review_type = models.CharField(max_length=20, verbose_name="评审类型")
    review_level = models.CharField(max_length=20, verbose_name="评审级别")
    scope = models.CharField(
        max_length=20, choices=Scope.choices, default=Scope.COLLEGE, verbose_name="范围"
    )
    batch = models.ForeignKey(
        ProjectBatch,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="review_templates",
        verbose_name="所属批次",
    )
    description = models.TextField(blank=True, default="", verbose_name="模板说明")
    notice = models.TextField(blank=True, default="", verbose_name="评审注意事项")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    is_locked = models.BooleanField(default=False, verbose_name="是否锁定")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_review_templates",
        verbose_name="创建人",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_review_templates",
        verbose_name="更新人",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "review_templates"
        verbose_name = "评审模板"
        verbose_name_plural = verbose_name
        ordering = ["-updated_at"]

    def __str__(self):
        return self.name


class ReviewTemplateItem(models.Model):
    """
    评审模板评分项
    """

    template = models.ForeignKey(
        ReviewTemplate,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="评审模板",
    )
    title = models.CharField(max_length=200, verbose_name="评分项")
    description = models.TextField(blank=True, default="", verbose_name="说明")
    weight = models.DecimalField(
        max_digits=5, decimal_places=2, default=0, verbose_name="权重"
    )
    max_score = models.IntegerField(default=100, verbose_name="最高分")
    is_required = models.BooleanField(default=False, verbose_name="是否必填")
    sort_order = models.IntegerField(default=0, verbose_name="排序")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "review_template_items"
        verbose_name = "评审模板评分项"
        verbose_name_plural = verbose_name
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.template.name} - {self.title}"


class WorkflowNode(models.Model):
    """
    流程节点（支持拖拽排序）
    """

    class NodeType(models.TextChoices):
        REVIEW = "REVIEW", "审核"
        EXPERT_REVIEW = "EXPERT_REVIEW", "专家评审"
        APPROVAL = "APPROVAL", "管理员确认"

    class Role(models.TextChoices):
        TEACHER = "TEACHER", "导师"
        LEVEL2_ADMIN = "LEVEL2_ADMIN", "二级管理员"
        LEVEL1_ADMIN = "LEVEL1_ADMIN", "一级管理员"
        EXPERT = "EXPERT", "专家"

    class ReturnPolicy(models.TextChoices):
        NONE = "NONE", "不允许退回"
        STUDENT = "STUDENT", "退回学生"
        TEACHER = "TEACHER", "退回导师"
        PREVIOUS = "PREVIOUS", "退回上一级"

    workflow = models.ForeignKey(
        WorkflowConfig,
        on_delete=models.CASCADE,
        related_name="nodes",
        verbose_name="流程配置",
    )
    code = models.CharField(max_length=50, verbose_name="节点编码")
    name = models.CharField(max_length=100, verbose_name="节点名称")
    node_type = models.CharField(
        max_length=20, choices=NodeType.choices, verbose_name="节点类型"
    )
    role = models.CharField(max_length=20, choices=Role.choices, verbose_name="角色")
    review_level = models.CharField(
        max_length=20, blank=True, default="", verbose_name="审核级别"
    )
    scope = models.CharField(
        max_length=20, blank=True, default="", verbose_name="专家范围"
    )
    return_policy = models.CharField(
        max_length=20,
        choices=ReturnPolicy.choices,
        default=ReturnPolicy.NONE,
        verbose_name="退回规则",
    )
    review_template = models.ForeignKey(
        ReviewTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="workflow_nodes",
        verbose_name="关联评审模板",
    )
    notice = models.TextField(blank=True, default="", verbose_name="评审注意事项")
    sort_order = models.IntegerField(default=0, verbose_name="排序")
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        db_table = "workflow_nodes"
        verbose_name = "流程节点"
        verbose_name_plural = verbose_name
        ordering = ["sort_order", "id"]
        unique_together = ("workflow", "code")

    def __str__(self):
        return f"{self.workflow.name} - {self.name}"
