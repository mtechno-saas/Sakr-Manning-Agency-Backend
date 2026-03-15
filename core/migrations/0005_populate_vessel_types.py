from django.db import migrations


def populate_vessel_types(apps, schema_editor):
    VesselType = apps.get_model('core', 'VesselType')
    vessel_types = [
        'Container Ships',
        'Bulk Carriers',
        'Tankers',
        'Ro-Ro Ships',
        'Passenger Ships',
        'Fishing Vessels',
        'Recreational',
        'Offshore Support Vessels',
        'Icebreakers',
        'Tugboats',
    ]
    for vt_name in vessel_types:
        VesselType.objects.get_or_create(name=vt_name)


def reverse_vessel_types(apps, schema_editor):
    VesselType = apps.get_model('core', 'VesselType')
    VesselType.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_populate_flags'),
    ]

    operations = [
        migrations.RunPython(populate_vessel_types, reverse_vessel_types),
    ]
