
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.dictionaries.models import DictionaryType, DictionaryItem

def seed_dictionaries():
    # Project Level
    level_type, _ = DictionaryType.objects.get_or_create(
        code="PROJECT_LEVEL", defaults={"name": "项目级别"}
    )
    DictionaryItem.objects.get_or_create(
        dict_type=level_type, value="SCHOOL", defaults={"label": "校级", "sort_order": 1}
    )
    DictionaryItem.objects.get_or_create(
        dict_type=level_type, value="PROVINCIAL", defaults={"label": "省级", "sort_order": 2}
    )
    DictionaryItem.objects.get_or_create(
        dict_type=level_type, value="NATIONAL", defaults={"label": "国家级", "sort_order": 3}
    )

    # Project Category
    category_type, _ = DictionaryType.objects.get_or_create(
        code="PROJECT_CATEGORY", defaults={"name": "项目类别"}
    )
    DictionaryItem.objects.get_or_create(
        dict_type=category_type, value="INNOVATION_TRAINING", defaults={"label": "创新训练项目", "sort_order": 1}
    )
    DictionaryItem.objects.get_or_create(
        dict_type=category_type, value="ENTREPRENEURSHIP_TRAINING", defaults={"label": "创业训练项目", "sort_order": 2}
    )
    DictionaryItem.objects.get_or_create(
        dict_type=category_type, value="ENTREPRENEURSHIP_PRACTICE", defaults={"label": "创业实践项目", "sort_order": 3}
    )
    
    # Project Source
    source_type, _ = DictionaryType.objects.get_or_create(
        code="PROJECT_SOURCE", defaults={"name": "项目来源"}
    )
    DictionaryItem.objects.get_or_create(
        dict_type=source_type, value="SELF_SELECTED", defaults={"label": "学生自选", "sort_order": 1}
    )
    DictionaryItem.objects.get_or_create(
        dict_type=source_type, value="TEACHER_ASSIGNED", defaults={"label": "教师指定", "sort_order": 2}
    )

    print("Dictionaries seeded successfully.")

if __name__ == "__main__":
    seed_dictionaries()
