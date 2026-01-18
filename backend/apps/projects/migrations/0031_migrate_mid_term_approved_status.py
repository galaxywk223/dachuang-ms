from django.db import migrations


def migrate_mid_term_approved(apps, schema_editor):
    Project = apps.get_model("projects", "Project")
    Project.objects.filter(status="MID_TERM_APPROVED").update(
        status="READY_FOR_CLOSURE"
    )


class Migration(migrations.Migration):
    dependencies = [
        ("projects", "0030_alter_project_status_and_more"),
    ]

    operations = [
        migrations.RunPython(migrate_mid_term_approved, migrations.RunPython.noop),
    ]
