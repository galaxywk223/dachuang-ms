from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0003_alter_user_role"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="expert_scope",
            field=models.CharField(
                blank=True,
                choices=[("SCHOOL", "校级专家"), ("COLLEGE", "院级专家")],
                default="COLLEGE",
                max_length=20,
                verbose_name="专家级别",
            ),
        ),
    ]
