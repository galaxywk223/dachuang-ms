
import os
import sys
import django

def setup_django():
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()

def fix_dictionary_codes():
    setup_django()
    from apps.dictionaries.models import DictionaryType

    # Map old uppercase codes to new lowercase codes (matching frontend)
    mapping = {
        "PROJECT_LEVEL": "project_level",
        "PROJECT_CATEGORY": "project_type", # Frontend uses project_type for category
        "PROJECT_SOURCE": "project_source"
    }

    for old_code, new_code in mapping.items():
        try:
            old_dt = DictionaryType.objects.get(code=old_code)
            
            # Check if new_code already exists
            if DictionaryType.objects.filter(code=new_code).exists():
                print(f"Target code {new_code} already exists. Merging items...")
                new_dt = DictionaryType.objects.get(code=new_code)
                
                # Move items from old_dt to new_dt
                items = old_dt.items.all()
                for item in items:
                    # Check if item value already exists in new_dt
                    if not new_dt.items.filter(value=item.value).exists():
                        item.dict_type = new_dt
                        item.save()
                        print(f"Moved item {item.value} to {new_code}")
                    else:
                        print(f"Item {item.value} already exists in {new_code}, skipping.")
                
                # Delete old DictionaryType
                old_dt.delete()
                print(f"Deleted old DictionaryType: {old_code}")
            else:
                # Rename if target doesn't exist
                old_dt.code = new_code
                old_dt.save()
                print(f"Renamed code: {old_code} -> {new_code}")
                
        except DictionaryType.DoesNotExist:
            print(f"DictionaryType not found: {old_code}")

if __name__ == "__main__":
    fix_dictionary_codes()
