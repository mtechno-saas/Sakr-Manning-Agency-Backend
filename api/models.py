# from django.db import models
from django.core.validators import FileExtensionValidator
from django.db import models
from django import forms
from django.core.management.base import BaseCommand
from multiselectfield import MultiSelectField
from django.utils.text import slugify
from django.db.models import Max
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from companies.models import Company

class Marital_Status(models.TextChoices):
    SINGLE = 'SINGLE'
    MARRIED = 'MARRIED'


class User_Status(models.TextChoices):
    VACATION = 'VACATION', 'VACATION'
    ON_SITE = 'ON_SITE', 'ON_SITE'
    MEDICAL_VACATION = 'MEDICAL VACATION', 'MEDICAL VACATION'



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


class Rank(models.Model):
    code = models.CharField(max_length=780, unique=True)
    name = models.CharField(max_length=780)

    def __str__(self):
        return f"{self.code} - {self.name}"
    

class UserRank(models.Model):
    user = models.ForeignKey("Users", on_delete=models.CASCADE, related_name="user_ranks")
    rank = models.ForeignKey("Rank", on_delete=models.CASCADE)
    assigned_code = models.CharField(max_length=20, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.assigned_code:
            prefix = self.rank.code.split(".")[0]
            last_ur = (
                UserRank.objects
                .filter(rank__code__startswith=prefix)
                .order_by("-assigned_code")
                .first()
            )
            if last_ur:
                last_num = int(last_ur.assigned_code.split(".")[-1])
                next_code = f"{prefix}.{last_num+1:03d}"
            else:
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


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, password, **extra_fields)

class LanguageProficiency(models.Model):
    # Language Options
    LANGUAGE_CHOICES = [
        ('English', 'English'),
        ('Spanish', 'Spanish'),
        ('French', 'French'),
        ('German', 'German'),
        ('Italian', 'Italian'),
        ('Portuguese', 'Portuguese'),
        ('Dutch', 'Dutch'),
        ('Russian', 'Russian'),
        ('Chinese (Mandarin)', 'Chinese (Mandarin)'),
        ('Japanese', 'Japanese'),
        ('Korean', 'Korean'),
        ('Arabic', 'Arabic'),
        ('Hindi', 'Hindi'),
        ('Greek', 'Greek'),
        ('Polish', 'Polish'),
        ('Turkish', 'Turkish'),
        ('Swedish', 'Swedish'),
        ('Norwegian', 'Norwegian'),
        ('Danish', 'Danish'),
        ('Finnish', 'Finnish'),
        ('Czech', 'Czech'),
        ('Romanian', 'Romanian'),
        ('Ukrainian', 'Ukrainian'),
        ('Thai', 'Thai'),
        ('Vietnamese', 'Vietnamese'),
        ('Indonesian', 'Indonesian'),
        ('Malay', 'Malay'),
        ('Tagalog', 'Tagalog'),
        ('Other', 'Other'),
    ]
    
    # CEFR Level Options
    CEFR_CHOICES = [
        ('A1', 'A1 - Beginner'),
        ('A2', 'A2 - Elementary'),
        ('B1', 'B1 - Intermediate'),
        ('B2', 'B2 - Upper Intermediate'),
        ('C1', 'C1 - Advanced'),
        ('C2', 'C2 - Proficient'),
    ]

    # Linking to your specific 'Users' model
    # related_name='languages' allows you to call user.languages.all()
    user = models.ForeignKey(
        'Users', 
        on_delete=models.CASCADE, 
        related_name='languages'
    )
    
    # Fields as requested
    language = models.CharField(max_length=100, choices=LANGUAGE_CHOICES)
    general_marks = models.IntegerField(default=0)
    
    # Proficiency Levels
    PROFICIENCY_CHOICES = [
        ('Elementary', 'Elementary'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
        ('Native', 'Native'),
    ]
    speaking_level = models.CharField(max_length=50, choices=PROFICIENCY_CHOICES, blank=True, null=True)
    writing_level = models.CharField(max_length=50, choices=PROFICIENCY_CHOICES, blank=True, null=True)
    reading_level = models.CharField(max_length=50, choices=PROFICIENCY_CHOICES, blank=True, null=True)
    
    cefr_level = models.CharField(
        max_length=2, 
        choices=CEFR_CHOICES, 
        default='A1'
    )
    cefr_description = models.TextField(
        blank=True, 
        null=True, 
        help_text="Detailed description of the language ability based on CEFR"
    )

    attachment = models.FileField(upload_to='languages/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Language Proficiency"
        verbose_name_plural = "Language Proficiencies"

    def __str__(self):
        return f"{self.language} for {self.user.email}"
class Users(AbstractBaseUser, PermissionsMixin):
    # Authentication
    email = models.EmailField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    profile_image = models.ImageField(upload_to="users/", blank=True, null=True)

    # Personal Info
    age = models.IntegerField(null=True, blank=True)
    blood_type = models.CharField(max_length=5, blank=True)
    smoker = models.BooleanField(default=False)
    us_visa_status = models.CharField(max_length=50, blank=True)
    schengen_visa_status = models.CharField(max_length=50, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    marital_status = models.CharField(max_length=40, default="Single")
    register_code = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        help_text="Registration code from system or document"
    )

    # Position Information
    APPLICATION_POSITION_CHOICES = [
        ('Master', 'Master'),
        ('1st. Officer – Chief Off.', '1st. Officer – Chief Off.'),
        ('2nd. Officer', '2nd. Officer'),
        ('3rd. Officer', '3rd. Officer'),
        ('Tug Master', 'Tug Master'),
        ('Boson', 'Boson'),
        ('A.B – O.S', 'A.B – O.S'),
        ('Steward / Galley Boy', 'Steward / Galley Boy'),
        ('Cook / 2nd. Cook / Ass. Cook / Baker / Pastry', 'Cook / 2nd. Cook / Ass. Cook / Baker / Pastry'),
        ('Carpenter', 'Carpenter'),
        ('Waiter', 'Waiter'),
        ('Purser', 'Purser'),
        ('Doctor', 'Doctor'),
        ('1st. Engineer', '1st. Engineer'),
        ('2nd. Engineer', '2nd. Engineer'),
        ('3rd. Engineer', '3rd. Engineer'),
        ('Electrical Engineer – E/E – ETO', 'Electrical Engineer – E/E – ETO'),
        ('Assistant Electrician', 'Assistant Electrician'),
        ('4th. Engineer', '4th. Engineer'),
        ('Electrician', 'Electrician'),
        ('Motor Man / Mechanic', 'Motor Man / Mechanic'),
        ('Oiler', 'Oiler'),
        ('Fitter – Welder', 'Fitter – Welder'),
        ('Wiper', 'Wiper'),
        ('Other', 'Other'),
    ]
    application_for_position = models.CharField(
        max_length=100, choices=APPLICATION_POSITION_CHOICES,
        blank=True, null=True, help_text="Application for position"
    )
    other_position = models.CharField(max_length=255, blank=True, null=True, help_text="Other position if not in the list")
    available_date = models.DateField(blank=True, null=True, help_text="Date of availability")

    register_date = models.DateField(
        null=True,
        blank=True,
        help_text="User registration date"
    )

    last_updated_date = models.DateTimeField(
        auto_now=True,
        help_text="Last time user data was updated"
    )
    user_status = models.CharField(max_length=40, choices=User_Status.choices, default=User_Status.ON_SITE)
    
    # Blacklist Status
    is_blacklisted = models.BooleanField(default=False)
    blacklist_reason = models.TextField(blank=True, null=True)

    nationality = models.CharField(max_length=50, null=True, blank=True)
    Place_Of_Birth = models.CharField(max_length=100, null=True, blank=True)
    Nearest_Port = models.CharField(max_length=200, null=True)
    Height_Cm = models.IntegerField(default=0)
    Weight_Kg = models.IntegerField(default=0)

    # Education
    college_or_school = models.CharField(max_length=200, null=True, blank=True)

    # Contact
    address = models.CharField(max_length=100, null=True)
    phone_number = models.CharField(max_length=20, blank=True)
    tel_number = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    # Admin/Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Travel Documents
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

    # Professional Qualification / Certificate of Competency
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
    next_of_kin_phone2 = models.CharField(max_length=50, blank=True, null=True)
    next_of_kin_email = models.EmailField(blank=True, null=True)

    # Health Certificates & Vaccinations
    health_flag_state = models.CharField(max_length=100, blank=True, null=True)
    health_number = models.CharField(max_length=100, blank=True, null=True)
    health_issue_date = models.DateField(blank=True, null=True)
    health_expiry_date = models.DateField(blank=True, null=True)
    health_issued_by = models.CharField(max_length=255, blank=True, null=True)
    health_issued_at = models.CharField(max_length=255, blank=True, null=True)

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

    # New fields from Word document
    overall_size = models.CharField(max_length=50, blank=True, null=True)
    shirt_size = models.CharField(max_length=50, blank=True, null=True)
    trouser_size = models.CharField(max_length=50, blank=True, null=True)
    shoes_size = models.CharField(max_length=50, blank=True, null=True)
    english_language_level = models.CharField(max_length=50, blank=True, null=True)
    other_language = models.CharField(max_length=50, blank=True, null=True)
    other_language_level = models.CharField(max_length=50, blank=True, null=True)
    disease_history = models.TextField(blank=True, null=True)
    accident_history = models.TextField(blank=True, null=True)
    psychiatric_treatment_history = models.TextField(blank=True, null=True)
    addiction_history = models.TextField(blank=True, null=True)
    declaration_consent = models.BooleanField(default=False)
    declaration_date = models.DateField(blank=True, null=True)
    declaration_place = models.CharField(max_length=100, blank=True, null=True)
    initial_assessment_comments = models.TextField(blank=True, null=True)
    responsible_person_name = models.CharField(max_length=100, blank=True, null=True)
    assessment_date = models.DateField(blank=True, null=True)

    salary = models.CharField(max_length=100, blank=True, null=True)
    marlins_test_result = models.CharField(max_length=100, blank=True, null=True)
    marlins_test_issued_date = models.DateField(null=True, blank=True)
    marlins_test_issued_at = models.CharField(max_length=100, blank=True, null=True)
    marlins_test_issued_by = models.CharField(max_length=100, blank=True, null=True)
    marlins_test_attachment = models.FileField(upload_to='marlins_tests/', blank=True, null=True)

    ces_test_result = models.CharField(max_length=100, blank=True, null=True)
    ces_test_issued_date = models.DateField(null=True, blank=True)
    ces_test_issued_at = models.CharField(max_length=100, blank=True, null=True)
    ces_test_issued_by = models.CharField(max_length=100, blank=True, null=True)
    ces_test_attachment = models.FileField(upload_to='ces_tests/', blank=True, null=True)

    certificates = models.ManyToManyField(Certificate, blank=True)
    codes = models.ManyToManyField(Rank, blank=True)

    # Auth & Permissions
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('HR Manager', 'HR Manager'),
        ('Recruiter', 'Recruiter'),
        ('Employee', 'Employee'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Employee')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    generated_id = models.CharField(max_length=12, unique=True, null=True, blank=True, help_text="Auto-generated 12-digit ID")

    # Synced from Document
    title = models.CharField(max_length=255, null=True, blank=True, help_text="Synced from Document title")
    file = models.FileField(upload_to="user_files/", null=True, blank=True, help_text="Synced from Document file")
    position = models.CharField(max_length=100, null=True, blank=True, help_text="Synced from Document position")

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name"]

    class Meta:
        ordering = ['-created_at']
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email


# =====================
# COMPANY MODEL
# =====================
class Company(models.Model):
    """Company/Client Management"""
    COMPANY_TYPE_CHOICES = [
        ('Ship Owner', 'Ship Owner'),
        ('Ship Manager', 'Ship Manager'),
        ('Crewing Agency', 'Crewing Agency'),
        ('Training Center', 'Training Center'),
        ('Other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Prospect', 'Prospect'),
    ]

    name = models.CharField(max_length=255)
    company_type = models.CharField(max_length=50, choices=COMPANY_TYPE_CHOICES, default='Ship Owner')
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    contact_person_email = models.EmailField(blank=True, null=True)
    contact_person_phone = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    open_positions = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Companies"
        ordering = ['name']

    def __str__(self):
        return self.name


# =====================
# CONTRACT MODEL
# =====================
class Contract(models.Model):
    """Contract Management"""
    CONTRACT_STATUS = [
        ('Active', 'Active'),
        ('Completed', 'Completed'),
        ('Pending', 'Pending'),
        ('Signed', 'Signed'),
        ('Pending Signature', 'Pending Signature'),
        ('Draft', 'Draft'),
        ('Cancelled', 'Cancelled'),
    ]
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('GBP', 'British Pound'),
        ('EGP', 'Egyptian Pound'),
    ]

    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='contracts')
    ship = models.ForeignKey('ships.Ship', on_delete=models.CASCADE, related_name='contracts')
    company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, null=True, blank=True, related_name='api_contracts')
    rank = models.ForeignKey(Rank, on_delete=models.SET_NULL, null=True)

    sign_on_date = models.DateField()
    sign_off_date = models.DateField(null=True, blank=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    
    # Contract Details (Workflow Step 6)
    repatriation_terms = models.TextField(blank=True, null=True, help_text="Terms regarding repatriation rights")
    leave_pay_terms = models.TextField(blank=True, null=True, help_text="Details on leave pay calculation")
    
    status = models.CharField(max_length=20, choices=CONTRACT_STATUS, default='Pending')

    signed_file = models.FileField(upload_to='contracts/signed/', null=True, blank=True)
    signed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-sign_on_date']

    def __str__(self):
        return f"{self.user.email} on {self.ship.ship_name} ({self.sign_on_date})"


# =====================
# INTERVIEW MODEL
# =====================
class Interview(models.Model):
    """Interview Scheduling and Management"""
    INTERVIEW_TYPE_CHOICES = [
        ('Phone', 'Phone'),
        ('Video', 'Video'),
        ('In-Person', 'In-Person'),
        ('Technical', 'Technical'),
    ]
    STATUS_CHOICES = [
        ('Scheduled', 'Scheduled'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('Rescheduled', 'Rescheduled'),
        ('No Show', 'No Show'),
    ]
    RESULT_CHOICES = [
        ('Pending', 'Pending'),
        ('Passed', 'Passed'),
        ('Failed', 'Failed'),
        ('On Hold', 'On Hold'),
    ]

    candidate = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='interviews')
    company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, null=True, blank=True, related_name='api_interviews')
    position = models.ForeignKey(Rank, on_delete=models.SET_NULL, null=True, blank=True)

    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    duration_minutes = models.IntegerField(default=30)

    interview_type = models.CharField(max_length=20, choices=INTERVIEW_TYPE_CHOICES, default='Video')
    location = models.CharField(max_length=255, blank=True, null=True)
    meeting_link = models.URLField(blank=True, null=True)

    interviewer_name = models.CharField(max_length=255, blank=True, null=True)
    interviewer_email = models.EmailField(blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Scheduled')
    result = models.CharField(max_length=20, choices=RESULT_CHOICES, default='Pending')
    notes = models.TextField(blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)

    created_by = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, related_name='created_interviews')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-scheduled_date', '-scheduled_time']

    def __str__(self):
        return f"Interview: {self.candidate.email} - {self.scheduled_date}"


# =====================
# CV SUBMISSION MODEL
# =====================
class CVSubmission(models.Model):
    """CV/Application Submissions"""
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Under Review', 'Under Review'),
        ('Interviewed', 'Interviewed'),
        ('Shortlisted', 'Shortlisted'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Hired', 'Hired'),
    ]

    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='cv_submissions')
    company = models.ForeignKey('companies.Company', on_delete=models.SET_NULL, null=True, blank=True, related_name='api_cv_submissions')
    position = models.ForeignKey(Rank, on_delete=models.SET_NULL, null=True, blank=True)

    cv_file = models.FileField(upload_to='cv_submissions/', null=True, blank=True)
    cover_letter = models.TextField(blank=True, null=True)
    experience_years = models.IntegerField(default=0)
    expected_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    availability_date = models.DateField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    submitted_date = models.DateTimeField(auto_now_add=True)

    reviewed_by = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_submissions')
    reviewed_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    rating = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-submitted_date']

    def __str__(self):
        return f"CV: {self.user.email} - {self.position}"


class Reference(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='references')
    company_name = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    tel = models.CharField(max_length=50)
    email = models.EmailField()

    def __str__(self):
        return f"Reference for {self.user.email} from {self.company_name}"


class SeaService(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='sea_services')
    company_name = models.CharField(max_length=255, blank=True, default='')
    rank = models.CharField(max_length=255, blank=True, default='')
    vessel_name_imo = models.CharField(max_length=255, blank=True, default='')
    vessel_name = models.CharField(max_length=255, blank=True, default='', help_text='Vessel Name')
    imo_number = models.CharField(max_length=50, blank=True, default='', help_text='IMO Number')
    flag = models.CharField(max_length=100, blank=True, default='')
    signed_on = models.DateField(blank=True, null=True)
    signed_off = models.DateField(blank=True, null=True)
    period = models.CharField(max_length=100, blank=True, default='')
    vessel_type = models.CharField(max_length=100, blank=True, default='')
    
    # Separate ship detail fields
    dwt = models.CharField(max_length=100, blank=True, default='', help_text='Deadweight Tonnage')
    grt = models.CharField(max_length=100, blank=True, default='', help_text='Gross Register Tonnage')
    engine_type = models.CharField(max_length=100, blank=True, default='', help_text='Engine Type')
    bh = models.CharField(max_length=100, blank=True, default='', help_text='Brake Horsepower')
    kw = models.CharField(max_length=100, blank=True, default='', help_text='Kilowatts')
    
    file = models.FileField(
        upload_to='sea_services/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx', 'doc', 'jpg', 'jpeg', 'png'])],
        blank=True, null=True
    )
    reason_for_sign_off = models.CharField(max_length=255, blank=True, default='')

    def __str__(self):
        return f"Sea service for {self.user.email} on {self.vessel_name}"


class BlacklistRecord(models.Model):
    """
    Step 3D: Check blacklist, disciplinary records
    """
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='blacklist_records')
    reason = models.TextField()
    date_added = models.DateField(auto_now_add=True)
    added_by = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, related_name='added_blacklist_records')
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Blacklist: {self.user.email} - {self.reason[:20]}"


class PerformanceAppraisal(models.Model):
    """
    Step 10D: Collect performance feedback
    Step 3D: Previous performance appraisals
    """
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='appraisals')
    vessel_name = models.CharField(max_length=255)
    appraisal_date = models.DateField()
    
    rating = models.PositiveIntegerField(help_text="1 to 5 scale", default=3)
    comments = models.TextField(blank=True)
    
    evaluator_name = models.CharField(max_length=255, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-appraisal_date']

    def __str__(self):
        return f"Appraisal for {self.user.email} ({self.rating}/5) on {self.vessel_name}"


# =====================
# DOCUMENT MODEL
# =====================
class Document(models.Model):
    """
    Document model for storing user uploaded files (PDF/DOCX).
    """
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=255)
    file = models.FileField(
        upload_to='documents/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx'])]
    )
    
    POSITION_CHOICES = [
        ('Master', 'Master'),
        ('1st. Officer – Chief Off.', '1st. Officer – Chief Off.'),
        ('2nd. Officer', '2nd. Officer'),
        ('3rd. Officer', '3rd. Officer'),
        ('Tug Master', 'Tug Master'),
        ('Boson', 'Boson'),
        ('A.B – O.S', 'A.B – O.S'),
        ('Steward / Galley Boy', 'Steward / Galley Boy'),
        ('Cook / 2nd. Cook / Ass. Cook / Baker / Pastry', 'Cook / 2nd. Cook / Ass. Cook / Baker / Pastry'),
        ('Carpenter', 'Carpenter'),
        ('Waiter', 'Waiter'),
        ('Purser', 'Purser'),
        ('Doctor', 'Doctor'),
        ('1st. Engineer', '1st. Engineer'),
        ('2nd. Engineer', '2nd. Engineer'),
        ('3rd. Engineer', '3rd. Engineer'),
        ('Electrical Engineer – E/E – ETO', 'Electrical Engineer – E/E – ETO'),
        ('Assistant Electrician', 'Assistant Electrician'),
        ('4th. Engineer', '4th. Engineer'),
        ('Electrician', 'Electrician'),
        ('Motor Man / Mechanic', 'Motor Man / Mechanic'),
        ('Oiler', 'Oiler'),
        ('Fitter – Welder', 'Fitter – Welder'),
        ('Wiper', 'Wiper'),
        ('Other', 'Other'),
    ]

    name = models.CharField(max_length=255, help_text="Name of the person", null=True, blank=True)
    email = models.EmailField(help_text="Email address", null=True, blank=True)
    phone_number = models.CharField(max_length=50, help_text="Phone number", null=True, blank=True)
    position = models.CharField(
        max_length=100,
        choices=POSITION_CHOICES,
        help_text="Position/Rank",
        null=True, 
        blank=True
    )

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Active', 'Active'),
        ('Blacklist', 'Blacklist'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending',
        help_text="Document status"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.user.email})"


# =====================
# LANGUAGE MODEL
# =====================
class UserLanguage(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='user_languages')
    language = models.CharField(max_length=100)
    general_remarks = models.TextField(blank=True, null=True)
    
    # Proficiency Levels
    SPEAKING_CHOICES = [
        ('Elementary', 'Elementary'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
        ('Native', 'Native'),
    ]
    WRITING_CHOICES = [
        ('Elementary', 'Elementary'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
        ('Native', 'Native'),
    ]
    READING_CHOICES = [
        ('Elementary', 'Elementary'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
        ('Native', 'Native'),
    ]
    
    speaking_level = models.CharField(max_length=50, choices=SPEAKING_CHOICES, blank=True, null=True)
    writing_level = models.CharField(max_length=50, choices=WRITING_CHOICES, blank=True, null=True)
    reading_level = models.CharField(max_length=50, choices=READING_CHOICES, blank=True, null=True)
    
    # CEFR Level
    CEFR_CHOICES = [
        ('A1', 'A1'),
        ('A2', 'A2'),
        ('B1', 'B1'),
        ('B2', 'B2'),
        ('C1', 'C1'),
        ('C2', 'C2'),
    ]
    cefr_level = models.CharField(max_length=10, choices=CEFR_CHOICES, blank=True, null=True)
    cefr_description = models.TextField(blank=True, null=True, help_text="Description of selected CEFR Level")
    
    attachment = models.FileField(upload_to='languages/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.language} ({self.user.email})"


# =====================
# NEXT OF KIN MODEL
# =====================
class NextOfKin(models.Model):
    """Emergency Contact / Next of Kin - multiple per user"""
    RELATIONSHIP_CHOICES = [
        ('Father', 'Father'),
        ('Mother', 'Mother'),
        ('Brother', 'Brother'),
        ('Sister', 'Sister'),
        ('Wife', 'Wife'),
        ('Husband', 'Husband'),
        ('Son', 'Son'),
        ('Daughter', 'Daughter'),
        ('Uncle', 'Uncle'),
        ('Aunt', 'Aunt'),
        ('Friend', 'Friend'),
        ('Other', 'Other'),
    ]

    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='next_of_kins')
    full_name = models.CharField(max_length=255)
    relationship = models.CharField(max_length=100, choices=RELATIONSHIP_CHOICES)
    address_country = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=50)
    phone2 = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Next of Kin"
        verbose_name_plural = "Next of Kin"

    def __str__(self):
        return f"{self.full_name} ({self.relationship}) - {self.user.email}"



# =====================
# PERSONAL DOCUMENT MODEL
# =====================
class PersonalDocument(models.Model):
    """Travel/Personal Documents"""
    DOCUMENT_TYPE_CHOICES = [
        ("BAHAMAS SEAMAN'S BOOK", "BAHAMAS SEAMAN'S BOOK"),
        ("BELIZE SEAMAN'S BOOK", "BELIZE SEAMAN'S BOOK"),
        ("BERMUDA SEAMAN'S BOOK", "BERMUDA SEAMAN'S BOOK"),
        ("EU national ID", "EU national ID"),
        ("Exit Interview", "Exit Interview"),
        ("LIBERIAN SEAMAN'S BOOK", "LIBERIAN SEAMAN'S BOOK"),
        ("Local ID Card", "Local ID Card"),
        ("LUXEMBOURG SEAMAN'S BOOK", "LUXEMBOURG SEAMAN'S BOOK"),
        ("PALAU SEAMAN'S BOOK", "PALAU SEAMAN'S BOOK"),
        ("PANAMA SEAMAN'S BOOK", "PANAMA SEAMAN'S BOOK"),
        ("Passport", "Passport"),
        ("PERMESSO SOGGIORNO PERMANENTE", "PERMESSO SOGGIORNO PERMANENTE"),
        ("PERMESSO SOGGIORNO TEMPORANEO", "PERMESSO SOGGIORNO TEMPORANEO"),
        ("Personal Record Sheet", "Personal Record Sheet"),
        ("RESIDENCE CERTIFICATE", "RESIDENCE CERTIFICATE"),
        ("SEAFARERS' ID. DOC. ILO 185", "SEAFARERS' ID. DOC. ILO 185"),
        ("Seaman's Book", "Seaman's Book"),
        ("Seaman's Book/Card or ID", "Seaman's Book/Card or ID"),
        ("U.K. SEAMAN'S BOOK", "U.K. SEAMAN'S BOOK"),
    ]

    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='personal_documents')
    document_type = models.CharField(max_length=100, choices=DOCUMENT_TYPE_CHOICES)
    
    document_number = models.CharField(max_length=50, blank=True, null=True)
    issue_date = models.DateField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    issuing_country = models.CharField(max_length=100, blank=True, null=True)
    issued_by = models.CharField(max_length=255, blank=True, null=True, help_text="Authority or entity that issued the document")
    place_of_issue = models.CharField(max_length=255, blank=True, null=True, help_text="City or office where the document was issued")
    
    file = models.FileField(
        upload_to='personal_documents/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx', 'doc', 'jpg', 'jpeg', 'png'])],
        blank=True,
        null=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.document_type} - {self.user.email}"


# =====================
# DECLARATION MODEL
# =====================
class Declaration(models.Model):
    """
    Health Declaration for seafarers.
    Tracks medical history and consent information required for sea service.
    """
    user = models.ForeignKey(
        Users, 
        on_delete=models.CASCADE, 
        related_name='declarations',
        help_text="User making the declaration"
    )
    
    # Question 1: Disease History
    has_disease = models.BooleanField(
        default=False,
        help_text="Did you suffer, or presently suffer from, any disease likely to render you unfit for sea service?"
    )
    disease_details = models.TextField(
        blank=True, 
        null=True,
        help_text="If yes, please provide details about the disease"
    )
    
    # Question 2: Accident History
    has_accident = models.BooleanField(
        default=False,
        help_text="Did you suffer any accident which rendered you temporary and/or partially disabled?"
    )
    accident_details = models.TextField(
        blank=True, 
        null=True,
        help_text="If yes, please provide details about the accident"
    )
    
    # Question 3: Psychiatric Treatment
    has_psychiatric_treatment = models.BooleanField(
        default=False,
        help_text="Did you ever undergo psychiatric treatment?"
    )
    psychiatric_treatment_details = models.TextField(
        blank=True, 
        null=True,
        help_text="If yes, please provide details about the psychiatric treatment"
    )
    
    # Question 4: Addiction Status
    has_addiction = models.BooleanField(
        default=False,
        help_text="Are you addicted to alcohol or drugs of any kind?"
    )
    addiction_details = models.TextField(
        blank=True, 
        null=True,
        help_text="If yes, please provide details about the addiction"
    )
    
    # Consent and Declaration Info
    consent_given = models.BooleanField(
        default=False,
        help_text="Whether user has given consent for data processing"
    )
    declaration_place = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text="Location where declaration was signed"
    )
    declaration_date = models.DateField(
        blank=True, 
        null=True,
        help_text="Date when declaration was signed"
    )
    signature = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        help_text="Digital signature or signature reference"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Declaration"
        verbose_name_plural = "Declarations"
    
    def __str__(self):
        return f"Declaration by {self.user.email} on {self.declaration_date or 'N/A'}"