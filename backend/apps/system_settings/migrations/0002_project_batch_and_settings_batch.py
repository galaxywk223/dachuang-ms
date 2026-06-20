from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("system_settings", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProjectBatch",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, verbose_name="批次名称")),
                ("year", models.IntegerField(verbose_name="年度")),
                ("code", models.CharField(max_length=50, unique=True, verbose_name="批次编码")),
                ("is_current", models.BooleanField(default=False, verbose_name="是否当前批次")),
                ("is_active", models.BooleanField(default=True, verbose_name="是否启用")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="创建时间")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="更新时间")),
            ],
            options={
                "verbose_name": "项目批次",
                "verbose_name_plural": "项目批次",
                "db_table": "project_batches",
                "ordering": ["-year", "-created_at"],
            },
        ),
        migrations.AlterField(
            model_name="systemsetting",
            name="code",
            field=models.CharField(max_length=50, verbose_name="配置编码"),
        ),
        migrations.AddField(
            model_name="systemsetting",
            name="batch",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="settings",
                to="system_settings.projectbatch",
                verbose_name="所属批次",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="systemsetting",
            unique_together={("code", "batch")},
        ),
    ]
