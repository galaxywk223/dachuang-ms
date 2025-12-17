
import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.dictionaries.models import DictionaryType, DictionaryItem

def diagnose():
    print("--- Dictionary Types ---")
    for dt in DictionaryType.objects.all():
        print(f"Code: {dt.code}, Name: {dt.name}, ID: {dt.id}")

    print("\n--- Dictionary Items (SCHOOL) ---")
    items = DictionaryItem.objects.filter(value='SCHOOL')
    if not items.exists():
        print("No items with value 'SCHOOL' found.")
    else:
        for item in items:
            print(f"Item: {item.value}, Label: {item.label}, Type: {item.dict_type.code}")

    print("\n--- Dictionary Items (project_level) ---")
    try:
        dt = DictionaryType.objects.get(code='project_level')
        for item in dt.items.all():
             print(f"Item: {item.value}, Label: {item.label}")
    except DictionaryType.DoesNotExist:
        print("DictionaryType 'project_level' does not exist.")

if __name__ == "__main__":
    diagnose()
