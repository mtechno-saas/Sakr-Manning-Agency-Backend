from django.db import migrations, models
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0013_company_address_contact_person_alt_phone_notes'),
    ]

    operations = [
        migrations.AddField(
            model_name='joborderposition',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='joborderposition',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, default=timezone.now),
            preserve_default=False,
        ),
    ]
