from django.core.management.base import BaseCommand
from api.models import Rank

RANKS = [
    ("DO-1.000", "Master"),
    ("DO-2.000", "1st. Officer – Chief Off."),
    ("DO-3.000", "2nd. Officer"),
    ("DO-4.000", "3rd. Officer"),
    ("DO-5.000", "Tug Master"),
    ("DR-1.000", "Boson"),
    ("DR-2.000", "A.B – O.S"),
    ("DR-3.000", "Steward / Galley Boy"),
    ("DR-4.000", "Cook / 2nd. Cook / Ass. Cook/ Baker/pastry"),
    ("DR-5.000", "Carpenter"),
    ("DR-6.000", "Waiter"),
    ("DR-7.000", "Purser /"),
    ("DR-8.000", "Doctor"),
    ("EO-1.000", "1st. Engineer"),
    ("EO-2.000", "2nd. Engineer"),
    ("EO-3.000", "3rd. Engineer"),
    ("EO-4.000", "Electrical Engineer – E/E - ETO"),
    ("EO-5.000", "Assistant Electration"),
    ("EO-6.000", "4TH. Engineer"),
    ("ER-1.000", "Electrician"),
    ("ER-2.000", "Motor Man / MECHANIC"),
    ("ER-3.000", "Oiler"),
    ("ER-4.000", "Fitter - Welder"),
    ("ER-5.000", "Wiper"),
]

class Command(BaseCommand):
    help = "Load predefined ranks into the Rank model"

    def handle(self, *args, **kwargs):
        for code, name in RANKS:
            rank, created = Rank.objects.get_or_create(code=code, defaults={"name": name})
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created rank: {code} - {name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Rank already exists: {code}"))
