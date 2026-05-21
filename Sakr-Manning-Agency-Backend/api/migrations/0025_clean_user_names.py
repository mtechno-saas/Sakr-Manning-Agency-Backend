from django.db import migrations

def clean_names(apps, schema_editor):
    Users = apps.get_model('api', 'Users')
    for user in Users.objects.all():
        first = (user.first_name or "").strip()
        middle = (user.middle_name or "").strip()
        last = (user.last_name or "").strip()
        
        # 1. If last name is empty but middle name is present, use middle name
        if not last and middle:
            last = middle
            
        first_parts = first.split()
        if len(first_parts) > 1:
            new_first = first_parts[0]
            rest_of_first = " ".join(first_parts[1:])
            
            if not last:
                last = rest_of_first
                first = new_first
            elif first.endswith(last):
                first = first[:-len(last)].strip()
                if not first:
                    first = new_first
            else:
                first = new_first
        
        if last and first.endswith(last):
            first = first[:-len(last)].strip()
            if not first:
                first = first_parts[0] if first_parts else "Unknown"
                
        user.first_name = first
        user.middle_name = ""
        user.last_name = last
        user.save()

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0024_declaration'),
    ]

    operations = [
        migrations.RunPython(clean_names, migrations.RunPython.noop),
    ]
