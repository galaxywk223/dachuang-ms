from django.db import migrations


def seed_project_levels(apps, schema_editor):
    """
    Ensure project_level dictionary and items exist with the required options.
    """
    DictionaryType = apps.get_model("dictionaries", "DictionaryType")
    DictionaryItem = apps.get_model("dictionaries", "DictionaryItem")

    # Create or fetch the canonical project_level type
    level_type, _ = DictionaryType.objects.get_or_create(
        code="project_level",
        defaults={
            "name": "项目级别",
            "description": "项目级别（校级/省级/国家级等）",
            "is_system": True,
            "is_active": True,
        },
    )

    # Migrate legacy uppercase code if it exists
    try:
        legacy_type = DictionaryType.objects.get(code="PROJECT_LEVEL")
        if legacy_type.id != level_type.id:
            for item in legacy_type.items.all():
                if not DictionaryItem.objects.filter(
                    dict_type=level_type, value=item.value
                ).exists():
                    item.dict_type = level_type
                    item.save(update_fields=["dict_type"])
            legacy_type.delete()
    except DictionaryType.DoesNotExist:
        pass

    items = [
        ("SCHOOL_GENERAL", "校级一般", 1),
        ("SCHOOL_KEY", "校级重点", 2),
        ("PROVINCIAL", "省级", 3),
        ("NATIONAL", "国家级", 4),
    ]

    for value, label, sort_order in items:
        obj, created = DictionaryItem.objects.get_or_create(
            dict_type=level_type,
            value=value,
            defaults={
                "label": label,
                "sort_order": sort_order,
                "is_active": True,
                "extra_data": {},
            },
        )
        if not created:
            updated = False
            if obj.label != label:
                obj.label = label
                updated = True
            if obj.sort_order != sort_order:
                obj.sort_order = sort_order
                updated = True
            if not obj.is_active:
                obj.is_active = True
                updated = True
            if updated:
                obj.save()

    # Compatibility alias for existing data that still uses SCHOOL
    DictionaryItem.objects.get_or_create(
        dict_type=level_type,
        value="SCHOOL",
        defaults={
            "label": "校级（兼容）",
            "sort_order": 0,
            "is_active": False,
            "extra_data": {},
        },
    )


def noop_reverse(apps, schema_editor):
    # Do not delete data on reverse to avoid accidental loss
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("dictionaries", "0003_dictionaryitem_template_file"),
    ]

    operations = [
        migrations.RunPython(seed_project_levels, noop_reverse),
    ]
