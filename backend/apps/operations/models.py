from django.conf import settings
from django.db import models


class AsyncTaskRecord(models.Model):
    class TaskType(models.TextChoices):
        IMPORT = "IMPORT", "数据导入"
        EXPORT = "EXPORT", "数据导出"

    class TaskStatus(models.TextChoices):
        PENDING = "PENDING", "待执行"
        RUNNING = "RUNNING", "执行中"
        SUCCESS = "SUCCESS", "成功"
        FAILED = "FAILED", "失败"

    task_type = models.CharField(
        max_length=20,
        choices=TaskType.choices,
        default=TaskType.IMPORT,
        verbose_name="任务类型",
    )
    title = models.CharField(max_length=200, verbose_name="任务标题")
    status = models.CharField(
        max_length=20,
        choices=TaskStatus.choices,
        default=TaskStatus.PENDING,
        verbose_name="任务状态",
    )
    progress = models.PositiveSmallIntegerField(default=0, verbose_name="进度")
    message = models.CharField(max_length=255, blank=True, verbose_name="任务消息")
    payload = models.JSONField(default=dict, blank=True, verbose_name="任务参数")
    result = models.JSONField(default=dict, blank=True, verbose_name="任务结果")
    result_file = models.FileField(
        upload_to="task_results/",
        null=True,
        blank=True,
        max_length=255,
        verbose_name="结果文件",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_async_tasks",
        verbose_name="创建人",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    started_at = models.DateTimeField(null=True, blank=True, verbose_name="开始时间")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="完成时间")

    class Meta:
        db_table = "async_task_records"
        verbose_name = "异步任务"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["task_type", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.title}({self.status})"


class OperationLog(models.Model):
    class LogStatus(models.TextChoices):
        SUCCESS = "SUCCESS", "成功"
        FAILED = "FAILED", "失败"

    module = models.CharField(max_length=50, verbose_name="业务模块")
    action = models.CharField(max_length=100, verbose_name="操作动作")
    target_type = models.CharField(max_length=50, blank=True, verbose_name="对象类型")
    target_id = models.CharField(max_length=64, blank=True, verbose_name="对象ID")
    target_name = models.CharField(max_length=200, blank=True, verbose_name="对象名称")
    status = models.CharField(
        max_length=20,
        choices=LogStatus.choices,
        default=LogStatus.SUCCESS,
        verbose_name="操作状态",
    )
    detail = models.JSONField(default=dict, blank=True, verbose_name="操作详情")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP地址")
    operator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="operation_logs",
        verbose_name="操作人",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="操作时间")

    class Meta:
        db_table = "operation_logs"
        verbose_name = "操作日志"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["module", "-created_at"]),
            models.Index(fields=["operator", "-created_at"]),
            models.Index(fields=["status", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.module}:{self.action}({self.status})"
