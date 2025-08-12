from django.db import models
from django import forms
from multiselectfield import MultiSelectField

class Marital_Status(models.TextChoices):
    SINGLE = 'SINGLE'
    MARRIED = 'MARRIED'



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







# Create your models here.
class Users(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.IntegerField()

    date_of_birth = models.DateField(
    auto_now=False,        # automatically set to current date on each save (use for created/updated dates, not birthdays)
    auto_now_add=False,    # automatically set only when object is first created
    null=True,             # allow storing NULL in DB
    blank=True,            # allow leaving it empty in forms/admin
    help_text="YYYY-MM-DD format",  # helper text in admin/forms
    verbose_name="Date of Birth"    # human-readable field name
)
    marital_status = models.CharField(max_length=40 , choices=Marital_Status.choices , default="Single")
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


    salary = models.DecimalField(max_digits=7,decimal_places=2)
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


    

    certificates = MultiSelectField(choices=CERTIFICATES, blank=True, null=True)




    

    def __str__(self):
        return self.first_name
