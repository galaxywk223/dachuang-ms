from django.db import migrations


def seed_teacher_staff_title(apps, schema_editor):
    DictionaryType = apps.get_model("dictionaries", "DictionaryType")
    DictionaryItem = apps.get_model("dictionaries", "DictionaryItem")

    dict_type, _ = DictionaryType.objects.get_or_create(
        code="title",
        defaults={
            "name": "职称",
            "description": "Academic titles e.g. Professor, Lecturer",
            "is_system": True,
            "is_active": True,
        },
    )

    fields_to_update = []
    if dict_type.name != "职称":
        dict_type.name = "职称"
        fields_to_update.append("name")
    if not dict_type.is_system:
        dict_type.is_system = True
        fields_to_update.append("is_system")
    if not dict_type.is_active:
        dict_type.is_active = True
        fields_to_update.append("is_active")
    if fields_to_update:
        dict_type.save(update_fields=fields_to_update)

    item, created = DictionaryItem.objects.get_or_create(
        dict_type=dict_type,
        value="教工",
        defaults={
            "label": "教工",
            "sort_order": 1,
            "is_active": True,
        },
    )

    if not created:
        item_fields_to_update = []
        if item.label != "教工":
            item.label = "教工"
            item_fields_to_update.append("label")
        if item.sort_order != 1:
            item.sort_order = 1
            item_fields_to_update.append("sort_order")
        if not item.is_active:
            item.is_active = True
            item_fields_to_update.append("is_active")
        if item_fields_to_update:
            item.save(update_fields=item_fields_to_update)


def reverse_seed_teacher_staff_title(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("dictionaries", "0005_remove_school_project_level_alias"),
    ]

    operations = [
        migrations.RunPython(
            seed_teacher_staff_title,
            reverse_seed_teacher_staff_title,
        ),
    ]
