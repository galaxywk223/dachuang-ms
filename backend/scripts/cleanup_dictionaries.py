
import os
import sys
import django

def setup_django():
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()

def cleanup_dictionaries():
    setup_django()
    from apps.dictionaries.models import DictionaryItem

    # Cleanup Project Level
    # Remove items where value is Chinese (e.g., '校级重点', '省级', '国家级')
    invalid_values = ['校级重点', '校级一般', '省级', '国家级']
    deleted_count, _ = DictionaryItem.objects.filter(
        dict_type__code='project_level', 
        value__in=invalid_values
    ).delete()
    print(f"Deleted {deleted_count} invalid project_level items.")

    # Verify what's left
    items = DictionaryItem.objects.filter(dict_type__code='project_level').values('id', 'value', 'label')
    print("Remaining project_level items:", list(items))

if __name__ == "__main__":
    cleanup_dictionaries()
