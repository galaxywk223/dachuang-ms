from django.db import migrations, models


def remove_report_tasks(apps, schema_editor):
    AsyncTaskRecord = apps.get_model("operations", "AsyncTaskRecord")
    OperationLog = apps.get_model("operations", "OperationLog")

    report_tasks = list(
        AsyncTaskRecord.objects.filter(task_type="REPORT").only("id", "result_file")
    )
    report_task_ids = [str(task.id) for task in report_tasks]

    for task in report_tasks:
        result_file = getattr(task, "result_file", None)
        if not result_file:
            continue
        try:
            result_file.delete(save=False)
        except Exception:
            pass

    if report_task_ids:
        OperationLog.objects.filter(
            target_type="AsyncTaskRecord",
            target_id__in=report_task_ids,
        ).delete()
    OperationLog.objects.filter(detail__task_type="REPORT").delete()
    OperationLog.objects.filter(action="生成报表快照").delete()
    AsyncTaskRecord.objects.filter(task_type="REPORT").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("operations", "0002_operationlog"),
    ]

    operations = [
        migrations.RunPython(remove_report_tasks, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="asynctaskrecord",
            name="task_type",
            field=models.CharField(
                choices=[
                    ("IMPORT", "数据导入"),
                    ("EXPORT", "数据导出"),
                ],
                default="IMPORT",
                max_length=20,
                verbose_name="任务类型",
            ),
        ),
    ]
