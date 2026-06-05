import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saker.settings')
django.setup()

from core.models import VesselType

valid_vessel_types = [
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

def cleanup_and_populate():
    # 1. Count current records
    initial_count = VesselType.objects.count()
    print(f"Found {initial_count} existing vessel types in the database.")
    
    # 2. Delete all existing vessel types
    print("Deleting all existing vessel types to clean up garbage data...")
    VesselType.objects.all().delete()
    
    # 3. Add only the valid ones
    added_count = 0
    for vtype in valid_vessel_types:
        obj, created = VesselType.objects.get_or_create(name=vtype)
        if created:
            added_count += 1
            
    print(f"Successfully added {added_count} correct vessel types.")
    print(f"Database now has exactly {VesselType.objects.count()} clean vessel types.")

if __name__ == "__main__":
    cleanup_and_populate()
