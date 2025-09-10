from django.db import models
from django import forms
from django.core.management.base import BaseCommand
from multiselectfield import MultiSelectField
from django.utils.text import slugify
from django.db.models import Max
from django.contrib.auth.models import AbstractUser

class Marital_Status(models.TextChoices):
    SINGLE = 'SINGLE'
    MARRIED = 'MARRIED'


class User_Status(models.TextChoices):
    IN_VECATION = 'VECATION'
    ON_SITE = 'ON_SITE'
    MEDICAL = 'MEDICAL VECATION'





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
("ER-5.000", "Wiper")
]




CERTIFICATES = [
    ("PERSONAL_SURVIVAL_TECHNIQUES", "Personal Survival Techniques"),
    ("PROFICIENCY_IN_PERSONAL_SURVIVAL_TECHNIQUES", "Proficiency In Personal Survival Techniques"),
    ("FIRE_PREVENTION_AND_FIRE_FIGHTING", "Fire Prevention and Fire Fighting"),
    ("ADVANCED_FIRE_PREVENTION_AND_FIRE_FIGHTING", "Advanced Fire Prevention and Fire Fighting"),
    ("ELEMENTARY_FIRST_AID", "Elementary First Aid"),
    ("MEDICAL_CARE_STUDIES", "Medical Care Studies"),
    ("PERSONAL_SAFETY_AND_SOCIAL_RESPONSIBILITIES", "Personal Safety and Social Responsibilities"),
    ("PROFICIENCY_OF_SECURITY_AWARENESS_TRAINING_SEAFARERS", "Proficiency Of Security Awareness Training Seafarers"),
    ("PROFICIENCY_AS_SHIP_SECURITY_OFFICER_PSSO", "Proficiency as a Ship Security Officer (PSSO)"),
    ("PROFICIENCY_IN_SURVIVAL_CRAFT_AND_RESCUE_BOATS", "Proficiency In Survival Craft & Rescue Boats"),
    ("GMDSS", "G.M.D.S.S"),
    ("COMMUNICATIONS", "Communications"),
    ("ADVANCED_COMMUNICATIONS", "Advanced Communications"),
    ("ECDIS_ADVANCED_SIMULATOR_MANAGEMENT_LEVEL", "ECDIS Advanced Simulator (Management Level)"),
    ("ECDIS_SIMULATOR_OPERATION_LEVEL", "ECDIS Simulator (Operation Level)"),
    ("PREVENTION_AND_COMBATING_OF_MARINE_POLLUTION", "Prevention and Combating of Marine Pollution"),
    ("RADAR_AND_ARPA_SIMULATOR_AND_SEARCH_AND_RESCUE", "Radar & ARPA Simulator and Search & Rescue"),
    ("ARPA_SIMULATOR_AND_SEARCH", "ARPA Simulator and Search"),
    ("MARINE_RADAR_AND_AUTOMATIC_RADAR_PLOTTING", "Marine Radar and Automatic Radar Plotting"),
    ("BRIDGE_RESOURCE_MANAGEMENT_BRM", "Bridge Resource Management (B.R.M)"),
    ("ENGINE_RESOURCE_MANAGEMENT_ERM", "Engine Resource Management (E.R.M)"),
    ("NAVIGATIONAL_WATCH_KEEPING", "Navigational Watch Keeping"),
    ("PROFICIENCY_FOR_RATING_FORMING_PART_OF_NAVIGATIONAL_WATCH_II_4", "Proficiency for Rating forming part of Navigational watch (II/4)"),
    ("HIGH_VOLTAGE_TRAINING_OPERATION_OF_SHIP_1000V_AND_MORE", "High Voltage Training – Operation of Ship (1000 Volt and More)"),
    ("PASSENGER_SAFETY_CARGO_SAFETY_AND_HULL_INTEGRITY", "Passenger Safety Cargo Safety and Hull Integrity"),
    ("CROWD_MANAGEMENT_TRAINING", "Crowd Management Training"),
    ("CRISIS_MANAGEMENT_AND_HUMAN_BEHAVIOR_TRAINING", "Crisis Management and Human Behavior Training"),
    ("SAFETY_TRAINING_FOR_PERSONAL_PROVIDING_DIRECT_PASSENGER_SERVICES", "Safety training for Personal Prov. Direct Passengers"),
    ("PRACTICAL_ABILITY_TO_PREPARE_MEALS_MLC_2006", "Practical Ability to Prepare Meals (MLC 2006)"),
    ("PERSONAL_HYGIENE_AND_ENVIRONMENTAL_PROTECTION_MLC_2006", "Personal Hygiene and Envir. Protection (MLC 2006)"),
    ("SAFETY_AND_HEALTH_IN_PROVISION_OF_MEALS_MLC_2006", "Safety and Health in the Provision Meals (MLC 2006)"),
    ("FOOD_STORAGE_AND_INVENTORY_CONTROL_MLC_2006", "Food Storage and Inventory Control (MLC 2006)"),
    ("SHIPS_COOK_CERTIFICATE_MLC_2006", "Ships Cook Certificate (MLC 2006)"),
    ("ABLE_SEAFARER_DECK", "Able Seafarer Deck"),
    ("PROFICIENCY_FOR_ABLE_SEAFARER_DECK_II_5", "Proficiency for Able Seafarer Deck (II/5)"),
    ("ENGINEERING_WATCH_KEEPING", "Engineering Watch Keeping"),
    ("PROFICIENCY_FOR_RATING_FORMING_PART_OF_WATCH_IN_ENGINE_ROOM", "Proficiency for Rating forming part of a watch in engine room"),
    ("ABLE_SEAFARER_ENGINE", "Able Seafarer Engine"),
    ("PROFICIENCY_FOR_ABLE_SEAFARER_ENGINE_III_5", "Proficiency for Able Seafarer Engine (III/5)"),
    ("ELECTRO_TECHNICAL_RATING", "Electro Technical Rating"),
    ("PROFICIENCY_FOR_ELECTRO_TECHNICAL_RATING_III_7", "Proficiency for Electro Technical Rating (III/7)"),
    ("DP_INDUCTION_DP_ADVANCED", "D.p. induction/ d.p. advanced"),
    ("DP_OPERATOR_UNLIMITED", "D.p. operator (unlimited)"),
    ("OTHERS_CERTIFICATES", "Others"),
]



# class Rank(models.Model):
#     code = models.CharField(max_length=780, unique=True)
#     name = models.CharField(max_length=780)

#     def __str__(self):
#         return f"{self.code} - {self.name}"

class Rank(models.Model):
    code = models.CharField(max_length=780, unique=True)  # e.g. DO-1.000
    name = models.CharField(max_length=780)

    def __str__(self):
        return f"{self.code} - {self.name}"
    

class UserRank(models.Model):
    user = models.ForeignKey("Users", on_delete=models.CASCADE, related_name="user_ranks")
    rank = models.ForeignKey("Rank", on_delete=models.CASCADE)
    assigned_code = models.CharField(max_length=20, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.assigned_code:  # Only auto-generate if not provided
            # Use the rank code prefix (e.g. "DO-1", "ER-4", etc.)
            prefix = self.rank.code.split(".")[0]  

            # Find last assigned_code with same prefix
            last_ur = (
                UserRank.objects
                .filter(rank__code__startswith=prefix)
                .order_by("-assigned_code")
                .first()
            )

            if last_ur:
                # Extract last number part after the dot
                last_num = int(last_ur.assigned_code.split(".")[-1])
                next_code = f"{prefix}.{last_num+1:03d}"
            else:
                # Start sequence
                next_code = f"{prefix}.001"

            self.assigned_code = next_code

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.assigned_code} - {self.rank.name}"





    



class Certificate(models.Model):
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name






# Create your models here.
class Users(AbstractUser):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    profile_image = models.ImageField(
        upload_to="users/",  # saves images in MEDIA_ROOT/users/
        blank=True,
        null=True
    )
    age = models.IntegerField(null=True, blank=True)
    middle_name = models.CharField(max_length=100, blank=True)
    #gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')], blank=True)
    blood_type = models.CharField(max_length=5, blank=True)
    smoker = models.BooleanField(default=False) # Changed from 'smokers' to singular
    us_visa_status = models.CharField(max_length=50, blank=True, help_text="e.g., B1/B2, C1/D, None")
    schengen_visa_status = models.CharField(max_length=50, blank=True)

    date_of_birth = models.DateField(
    auto_now=False,        # automatically set to current date on each save (use for created/updated dates, not birthdays)
    auto_now_add=False,    # automatically set only when object is first created
    null=True,             # allow storing NULL in DB
    blank=True,            # allow leaving it empty in forms/admin
    help_text="YYYY-MM-DD format",  # helper text in admin/forms
    verbose_name="Date of Birth"    # human-readable field name
)
    marital_status = models.CharField(max_length=40 , choices=Marital_Status.choices , default="Single")
    user_status = models.CharField(max_length=40 , choices=User_Status.choices , default="On Site")
    nationality = models.CharField(max_length=50 , null=True)
    Place_Of_Birth = models.CharField(max_length=100 ,null=True, blank=True)
    Nearest_Port = models.CharField(max_length=200 , null=True)
    Height_Cm = models.IntegerField(default=0)
    Weight_Kg = models.IntegerField(default=0)


    college_or_school = models.CharField(
    max_length=200,
    null=True,
    blank=True,
    verbose_name="College Or School"
    )

    codes = models.ManyToManyField(Rank , blank=True)

        # Marlins Test fields
    marlins_test_issued_date = models.DateField(
        null=True, blank=True,
        verbose_name="Marlins Test Issued Date"
    )
    marlins_test_result = models.DecimalField(
        max_digits=5, decimal_places=2,
        null=True, blank=True,
        verbose_name="Marlins Test Result (%)",
        help_text="Enter percentage score, e.g., 85.50"
    )
    marlins_test_issued_by = models.CharField(
        max_length=150,
        null=True, blank=True,
        verbose_name="Marlins Test Issued By (Authority)"
    )
    marlins_test_issued_at = models.CharField(
        max_length=150,
        null=True, blank=True,
        verbose_name="Marlins Test Issued At (Location)"
    )


    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    address = models.CharField(max_length=100 , null=True)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

        # --- Travel Documents ---
    passport_no = models.CharField(max_length=50, null=True, blank=True)
    passport_issue_date = models.DateField(null=True, blank=True)
    passport_expiry_date = models.DateField(null=True, blank=True)
    passport_issued_by = models.CharField(max_length=100, null=True, blank=True)
    passport_place_of_issue = models.CharField(max_length=100, null=True, blank=True)

    seaman_book_no = models.CharField(max_length=50, null=True, blank=True)
    seaman_book_issue_date = models.DateField(null=True, blank=True)
    seaman_book_expiry_date = models.DateField(null=True, blank=True)
    seaman_book_issued_by = models.CharField(max_length=100, null=True, blank=True)
    seaman_book_place_of_issue = models.CharField(max_length=100, null=True, blank=True)

    other_seaman_book_no = models.CharField(max_length=50, null=True, blank=True)
    other_seaman_book_issue_date = models.DateField(null=True, blank=True)
    other_seaman_book_expiry_date = models.DateField(null=True, blank=True)
    other_seaman_book_issued_by = models.CharField(max_length=100, null=True, blank=True)
    other_seaman_book_place_of_issue = models.CharField(max_length=100, null=True, blank=True)


        # ... existing fields ...

    # === Professional Qualification / Certificate of Competency ===
    coc_certificate_name = models.CharField(max_length=100, blank=True, null=True)
    coc_certificate_number = models.CharField(max_length=50, blank=True, null=True)
    coc_issue_date = models.DateField(blank=True, null=True)
    coc_expiry_date = models.DateField(blank=True, null=True)
    coc_issued_by = models.CharField(max_length=100, default="EAMS")
    coc_issued_at = models.CharField(max_length=100, default="Alex.")

    goc_certificate_number = models.CharField(max_length=50, blank=True, null=True)
    goc_issue_date = models.DateField(blank=True, null=True)
    goc_expiry_date = models.DateField(blank=True, null=True)
    goc_issued_by = models.CharField(max_length=100, default="NTRA")
    goc_issued_at = models.CharField(max_length=100, default="Cairo")


    # Next of Kin / Emergency Contact
    next_of_kin_full_name = models.CharField(max_length=255, blank=True, null=True)
    next_of_kin_relationship = models.CharField(max_length=100, blank=True, null=True)
    next_of_kin_address_country = models.CharField(max_length=255, blank=True, null=True)
    next_of_kin_phone = models.CharField(max_length=50, blank=True, null=True)
    next_of_kin_email = models.EmailField(blank=True, null=True)


    # Health Certificates & Vaccinations
    health_flag_state = models.CharField(max_length=100, blank=True, null=True)
    health_number = models.CharField(max_length=100, blank=True, null=True)
    health_issue_date = models.DateField(blank=True, null=True)
    health_expiry_date = models.DateField(blank=True, null=True)
    health_issued_by = models.CharField(max_length=255, blank=True, null=True)
    health_issued_at = models.CharField(max_length=255, blank=True, null=True)

    # Specific certificates
    international_medical_number = models.CharField(max_length=100, blank=True, null=True)
    international_medical_issue_date = models.DateField(blank=True, null=True)
    international_medical_expiry_date = models.DateField(blank=True, null=True)

    yellow_fever_number = models.CharField(max_length=100, blank=True, null=True)
    yellow_fever_issue_date = models.DateField(blank=True, null=True)
    yellow_fever_expiry_date = models.DateField(blank=True, null=True)

    cholera_number = models.CharField(max_length=100, blank=True, null=True)
    cholera_issue_date = models.DateField(blank=True, null=True)
    cholera_expiry_date = models.DateField(blank=True, null=True)

    # COVID-19 Vaccination
    covid_vaccine_name = models.CharField(max_length=100, blank=True, null=True)
    covid_first_dose = models.DateField(blank=True, null=True)
    covid_second_dose = models.DateField(blank=True, null=True)
    covid_other_doses_or_remarks = models.TextField(blank=True, null=True)


    


    #certificates = MultiSelectField(choices=CERTIFICATES, blank=True, null=True)
    certificates = models.ManyToManyField(Certificate , blank=True)
    
    # codes = MultiSelectField(choices=RANKS, blank=True, null=True)\
    #codes = MultiSelectField(max_length=780 , choices=RANKS , default="Select Any Job" )






    

    def __str__(self):
        return self.first_name


# --- New Contract Model ---
class Contract(models.Model):
    """
    Represents a specific work assignment for a user on a ship.
    This is the most important new model for tracking employment history.
    """
    CONTRACT_STATUS = [
        ('Active', 'Active'),
        ('Completed', 'Completed'),
        ('Pending', 'Pending'),
    ]
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='contracts')
    ship = models.ForeignKey('ships.Ship', on_delete=models.CASCADE, related_name='contracts')
    rank = models.ForeignKey(Rank, on_delete=models.SET_NULL, null=True, help_text="The rank for this specific contract.")
    
    sign_on_date = models.DateField()
    sign_off_date = models.DateField(null=True, blank=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=CONTRACT_STATUS, default='Pending')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-sign_on_date']

    def __str__(self):
        return f"{self.user.email} on {self.ship.ship_name} ({self.sign_on_date})"