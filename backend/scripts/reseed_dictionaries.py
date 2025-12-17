
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.dictionaries.models import DictionaryType, DictionaryItem

def seed_dictionaries():
    print("Seeding dictionaries...")
    
    # Project Level (project_level)
    level_type, _ = DictionaryType.objects.get_or_create(
        code="project_level", defaults={"name": "项目级别"}
    )
    print(f"Level Type ID: {level_type.id}")
    
    items_to_create = [
        ("SCHOOL", "校级", 1),
        ("PROVINCIAL", "省级", 2),
        ("NATIONAL", "国家级", 3)
    ]
    
    for value, label, sort_order in items_to_create:
        item, created = DictionaryItem.objects.get_or_create(
            dict_type=level_type, 
            value=value, 
            defaults={"label": label, "sort_order": sort_order}
        )
        print(f"Item {value}: Created={created}, ID={item.id}")

    # Project Category (project_type)
    category_type, _ = DictionaryType.objects.get_or_create(
        code="project_type", defaults={"name": "项目类别"}
    )
    
    cat_items = [
        ("INNOVATION_TRAINING", "创新训练项目", 1),
        ("ENTREPRENEURSHIP_TRAINING", "创业训练项目", 2),
        ("ENTREPRENEURSHIP_PRACTICE", "创业实践项目", 3)
    ]
    
    for value, label, sort_order in cat_items:
        item, created = DictionaryItem.objects.get_or_create(
            dict_type=category_type, 
            value=value, 
            defaults={"label": label, "sort_order": sort_order}
        )
        print(f"Item {value}: Created={created}, ID={item.id}")
    
    # Project Source (project_source)
    source_type, _ = DictionaryType.objects.get_or_create(
        code="project_source", defaults={"name": "项目来源"}
    )
    
    src_items = [
        ("SELF_SELECTED", "学生自选", 1),
        ("TEACHER_ASSIGNED", "教师指定", 2)
    ]
    
    for value, label, sort_order in src_items:
        item, created = DictionaryItem.objects.get_or_create(
            dict_type=source_type, 
            value=value, 
            defaults={"label": label, "sort_order": sort_order}
        )
        print(f"Item {value}: Created={created}, ID={item.id}")

    print("Dictionaries re-seeded successfully.")

if __name__ == "__main__":
    seed_dictionaries()
