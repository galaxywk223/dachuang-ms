from django.db import migrations

def create_project_source_dict(apps, schema_editor):
    DictionaryType = apps.get_model("dictionaries", "DictionaryType")
    DictionaryItem = apps.get_model("dictionaries", "DictionaryItem")

    # Create Dictionary Type
    dict_type, created = DictionaryType.objects.get_or_create(
        code="project_source",
        defaults={
            "name": "项目来源",
            "description": "项目来源类型",
            "is_system": True,
            "is_active": True,
        },
    )

    # Create Dictionary Items
    items = [
        {"value": "STUDENT_PROPOSED", "label": "学生自拟", "sort_order": 1},
        {"value": "TEACHER_PROPOSED", "label": "教师选题", "sort_order": 2},
        {"value": "COMPETITION", "label": "竞赛转化", "sort_order": 3},
        {"value": "ENTERPRISE", "label": "企业委托", "sort_order": 4},
    ]

    for item in items:
        DictionaryItem.objects.get_or_create(
            dict_type=dict_type,
            value=item["value"],
            defaults={
                "label": item["label"],
                "sort_order": item["sort_order"],
                "is_active": True,
            },
        )

def remove_project_source_dict(apps, schema_editor):
    DictionaryType = apps.get_model("dictionaries", "DictionaryType")
    try:
        dict_type = DictionaryType.objects.get(code="project_source")
        dict_type.delete()
    except DictionaryType.DoesNotExist:
        pass

class Migration(migrations.Migration):

    dependencies = [
        ("dictionaries", "0002_init_data"),
    ]

    operations = [
        migrations.RunPython(create_project_source_dict, remove_project_source_dict),
    ]
