import os
import django

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "saker.settings")
django.setup()

from api.models import Rank

# List of positions transcribed from your image
positions_data = [
    ("DO-1.000", "Master / Captain"),
    ("DO-2.000", "Staff Captain"),
    ("DO-3.000", "Chief Officer / Chief Mate"),
    ("DO-4.000", "Second Officer"),
    ("DO-5.000", "Third Officer"),
    ("DO-6.000", "Master / Captain"),
    ("DO-7.000", "Dynamic Positioning Operator (DPO)"),
    ("DO-8.000", "ROV Supervisor"),
    ("DO-9.000", "Offshore Installation Manager"),
    ("DO-10.000", "Deck Cadet"),
    ("DR-1.000", "Bosun"),
    ("DR-2.000", "ABLE SEAFARER DECK"),
    ("DR-3.000", "Able Seaman (AB)"),
    ("DR-4.000", "Ordinary Seaman (OS)"),
    ("DR-5.000", "Carpenter"),
    ("DR-6.000", "Pumpman"),
    ("DR-7.000", "Crane Operator"),
    ("DR-8.000", "Water and Pool"),
    ("DR-9.000", "Security Guard"),
    ("DR-10.000", "Life Guard"),
    ("DR-11.000", "Upholsterer"),
    ("DR-12.000", "Doctor"),
    ("DR-13.000", "Hotel Director"),
    ("DR-14.000", "Assistant Hotel Director"),
    ("DR-15.000", "Purser"),
    ("DR-16.000", "Assistant Purser"),
    ("DR-17.000", "Food & Beverage Manager"),
    ("DR-18.000", "Executive Chef"),
    ("DR-19.000", "Chief Housekeeper"),
    ("DR-20.000", "Guest Services Manager"),
    ("DR-21.000", "Restaurant Manager"),
    ("DR-22.000", "Head Waiter"),
    ("DR-23.000", "Waiter"),
    ("DR-24.000", "F&B attendant"),
    ("DR-25.000", "Bartender"),
    ("DR-26.000", "Cabin Steward"),
    ("DR-27.000", "Laundryman"),
    ("DR-28.000", "Cook"),
    ("DR-29.000", "2nd Cook"),
    ("DR-30.000", "3rd Cook"),
    ("DR-31.000", "Assistant Cook"),
    ("DR-32.000", "Baker"),
    ("DR-33.000", "Assistant Baker"),
    ("DR-34.000", "Pastry"),
    ("DR-35.000", "Assistant pastry"),
    ("DR-36.000", "Butcher"),
    ("DR-37.000", "Steward"),
    ("DR-38.000", "Utility Galley"),
    ("DR-39.000", "Tour Expert"),
    ("DR-40.000", "Photographer"),
    ("EO-1.000", "Chief Engineer"),
    ("EO-2.000", "Second Engineer"),
    ("EO-3.000", "Third Engineer"),
    ("EO-4.000", "Fourth Engineer"),
    ("EO-5.000", "ETO"),
    ("EO-6.000", "2ND ETO"),
    ("EO-7.000", "3RD ETO"),
    ("EO-8.000", "ELECTRICAL ENGINEER"),
    ("EO-9.000", "Refrigeration Engineer"),
    ("EO-10.000", "HVAC Engineer"),
    ("EO-11.000", "Engine Cadet"),
    ("EO-12.000", "Gas Engineer"),
    ("EO-13.000", "Cargo Engineer"),
    ("EO-14.000", "Reliquefaction Engineer"),
    ("ER-1.000", "Motorman"),
    ("ER-2.000", "Mechanic"),
    ("ER-3.000", "Assistant Mechanic"),
    ("ER-4.000", "Oiler"),
    ("ER-5.000", "Wiper"),
    ("ER-6.000", "Fitter"),
    ("ER-7.000", "Welder"),
    ("ER-8.000", "Plumber"),
    ("ER-9.000", "Assistant Plumber"),
    ("ER-10.000", "Water and Pool"),
    ("ER-11.000", "Electrician"),
    ("ER-12.000", "2nd Electrician"),
    ("ER-13.000", "3rd Electrician"),
    ("ER-14.000", "Assistant Electrician"),
    ("ER-15.000", "Trainee Electrician"),
    ("ER-16.000", "AC Technician"),
    ("ER-17.000", "Senior Accommodation Repairman"),
    ("ER-18.000", "Junior Accommodation Repairman"),
]

added = 0
for code, name in positions_data:
    obj, created = Rank.objects.get_or_create(code=code, defaults={"name": name})
    if created:
        added += 1

print(f"Successfully added {added} new positions to the database!")
