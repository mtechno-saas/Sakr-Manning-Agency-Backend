from django.db import models

class Marital_Status(models.TextChoices):
    SINGLE = 'SINGLE'
    MARRIED = 'MARRIED'


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
    

    def __str__(self):
        return self.first_name
