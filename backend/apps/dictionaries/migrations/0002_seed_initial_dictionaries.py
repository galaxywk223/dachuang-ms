from django.db import migrations

def seed_dictionaries(apps, schema_editor):
    DictionaryType = apps.get_model('dictionaries', 'DictionaryType')
    DictionaryItem = apps.get_model('dictionaries', 'DictionaryItem')
    
    # Define initial dictionary types
    types_data = [
        # (code, name, description)
        ('project_level', '项目级别', 'Projects levels e.g. National, Provincial'),
        ('project_category', '项目类别', 'Categories for projects'),
        ('key_field_code', '所属重点领域代码', 'Key field codes'),
        ('project_type', '项目类型', 'Types of projects'),
        ('college', '学院', 'University colleges/schools'),
        ('title', '职称', 'Academic titles e.g. Professor, Lecturer'),
        ('project_major_code', '项目所属专业类代码', '4-digit major codes'),
        ('project_source', '项目来源', 'Source of the project'),
    ]
    
    for code, name, desc in types_data:
        dict_type, created = DictionaryType.objects.get_or_create(
            code=code,
            defaults={
                'name': name,
                'description': desc,
                'is_system': True,  # Mark as system so they aren't easily deleted
                'is_active': True
            }
        )
        
        # Seed items for Project Source specifically
        if code == 'project_source':
            source_items = [
                ('teacher_research', '教师科研类'),
                ('discipline_competition', '学科竞赛类'),
                ('student_autonomous', '学生自主类'),
            ]
            for i, (val, label) in enumerate(source_items):
                DictionaryItem.objects.get_or_create(
                    dict_type=dict_type,
                    value=val,
                    defaults={
                        'label': label,
                        'sort_order': i + 1,
                        'is_active': True
                    }
                )

def reverse_seed(apps, schema_editor):
    # We generally don't delete data in reverse migrations for dictionaries to be safe,
    # but strictly speaking we could.
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('dictionaries', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_dictionaries, reverse_seed),
    ]
