from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("dictionaries", "0004_seed_project_level_items"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="SystemSetting",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=50, unique=True, verbose_name="配置编码")),
                ("name", models.CharField(max_length=100, verbose_name="配置名称")),
                ("data", models.JSONField(default=dict, verbose_name="配置数据")),
                ("is_locked", models.BooleanField(default=False, verbose_name="是否锁定")),
                ("is_active", models.BooleanField(default=True, verbose_name="是否启用")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="创建时间")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="更新时间")),
                ("updated_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="updated_settings", to=settings.AUTH_USER_MODEL, verbose_name="更新人")),
            ],
            options={
                "verbose_name": "系统配置",
                "verbose_name_plural": "系统配置",
                "db_table": "system_settings",
                "ordering": ["code"],
            },
        ),
        migrations.CreateModel(
            name="CertificateSetting",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, verbose_name="模板名称")),
                ("school_name", models.CharField(max_length=100, verbose_name="学校名称")),
                ("issuer_name", models.CharField(max_length=100, verbose_name="证书发放单位")),
                ("template_code", models.CharField(default="DEFAULT", max_length=50, verbose_name="模板编码")),
                ("background_image", models.ImageField(blank=True, null=True, upload_to="certificates/backgrounds/", verbose_name="证书底图")),
                ("seal_image", models.ImageField(blank=True, null=True, upload_to="certificates/seals/", verbose_name="电子印章")),
                ("style_config", models.JSONField(default=dict, verbose_name="样式配置")),
                ("is_active", models.BooleanField(default=True, verbose_name="是否启用")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="创建时间")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="更新时间")),
                ("project_category", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="certificate_category_settings", to="dictionaries.dictionaryitem", verbose_name="适用项目类别")),
                ("project_level", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="certificate_level_settings", to="dictionaries.dictionaryitem", verbose_name="适用项目级别")),
                ("updated_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="updated_certificates", to=settings.AUTH_USER_MODEL, verbose_name="更新人")),
            ],
            options={
                "verbose_name": "结题证书配置",
                "verbose_name_plural": "结题证书配置",
                "db_table": "certificate_settings",
                "ordering": ["-updated_at"],
            },
        ),
    ]
