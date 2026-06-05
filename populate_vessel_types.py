import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saker.settings')
django.setup()

from core.models import VesselType

vessel_types = [
    "Bulk Carrier",
    "Container Ship",
    "General Cargo Ship",
    "Oil Tanker",
    "Chemical Tanker",
    "LNG Carrier",
    "Cruise Ship",
    "Passenger Ship",
    "Ferry",
    "Ro-Ro Ship",
    "Ro-Ro Passenger (Ro-Pax)",
    "PSV (Platform Supply Vessel)",
    "AHTS (Anchor Handling Tug Supply Vessel)",
    "Drillship",
    "Barge",
    "Tugboat",
    "Dredger",
    "Fishing Vessel",
    "Survey Vessel",
    "Yacht",
    "Sailboat",
    "River Vessel"
]

def populate_vessel_types():
    added_count = 0
    for vtype in vessel_types:
        obj, created = VesselType.objects.get_or_create(name=vtype)
        if created:
            print(f"Added new vessel type: {vtype}")
            added_count += 1
        else:
            print(f"Vessel type already exists: {vtype}")
            
    print(f"\nSuccessfully added {added_count} new vessel types.")

if __name__ == "__main__":
    populate_vessel_types()
