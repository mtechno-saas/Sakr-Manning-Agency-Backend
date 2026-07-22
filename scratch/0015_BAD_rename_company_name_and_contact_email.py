# Generated for production: rename Company.name -> Company.company_name
# and Company.email -> Company.contact_email. The refactor was committed
# in code but the column rename was never migrated.

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("companies", "0014_joborderposition_created_at_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="company",
            old_name="name",
            new_name="company_name",
        ),
        migrations.RenameField(
            model_name="company",
            old_name="email",
            new_name="contact_email",
        ),
    ]
