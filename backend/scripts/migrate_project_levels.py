
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.projects.models import Project
from apps.dictionaries.models import DictionaryItem

def migrate_project_levels():
    # Map Chinese values to English codes
    mapping = {
        "校级": "SCHOOL",
        "校级一般": "SCHOOL",
        "校级重点": "SCHOOL",
        "省级": "PROVINCIAL",
        "国家级": "NATIONAL"
    }

    for chinese_val, english_code in mapping.items():
        try:
            # Find the new item
            new_item = DictionaryItem.objects.get(dict_type__code='project_level', value=english_code)
            
            # Find old items with Chinese value
            old_items = DictionaryItem.objects.filter(dict_type__code='project_level', value=chinese_val)
            
            for old_item in old_items:
                # Find projects using this old item
                projects = Project.objects.filter(level=old_item)
                count = projects.count()
                if count > 0:
                    print(f"Migrating {count} projects from {chinese_val} to {english_code}...")
                    projects.update(level=new_item)
        except DictionaryItem.DoesNotExist:
            print(f"New item {english_code} not found! Skipping {chinese_val}.")

    print("Project level migration completed.")

if __name__ == "__main__":
    migrate_project_levels()
