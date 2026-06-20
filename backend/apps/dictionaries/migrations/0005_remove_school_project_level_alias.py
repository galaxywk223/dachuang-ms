from django.db import migrations


def remove_school_project_level_alias(apps, schema_editor):
    DictionaryItem = apps.get_model("dictionaries", "DictionaryItem")
    DictionaryItem.objects.filter(
        dict_type__code="project_level",
        value="SCHOOL",
    ).delete()


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("dictionaries", "0004_seed_project_level_items"),
    ]

    operations = [
        migrations.RunPython(remove_school_project_level_alias, noop_reverse),
    ]
