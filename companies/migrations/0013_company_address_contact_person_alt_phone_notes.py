from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0012_company_contact_phone_company_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='contact_person',
            field=models.CharField(
                blank=True,
                help_text='Primary contact name at the company',
                max_length=200,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='company',
            name='alt_phone',
            field=models.CharField(
                blank=True,
                help_text='Alternative phone number',
                max_length=50,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='company',
            name='address',
            field=models.TextField(
                blank=True,
                help_text='Full postal address',
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='company',
            name='notes',
            field=models.TextField(
                blank=True,
                help_text='Internal notes about this company',
                null=True,
            ),
        ),
    ]
