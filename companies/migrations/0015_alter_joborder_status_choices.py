from django.db import migrations, models


class Migration(migrations.Migration):
    """Add 'Hold' and 'Closed' to JobOrder.STATUS_CHOICES so the frontend
    filter (Open / Closed / Hold) maps to real values."""

    dependencies = [
        ("companies", "0014_joborderposition_created_at_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="joborder",
            name="status",
            field=models.CharField(
                choices=[
                    ("Pending", "Pending Review"),
                    ("Open", "Open / Sourcing"),
                    ("Hold", "On Hold"),
                    ("Closed", "Closed"),
                    ("Active", "Active"),
                    ("In Progress", "In Progress / Interviewing"),
                    ("Fulfilled", "Fulfilled"),
                    ("Cancelled", "Cancelled"),
                ],
                default="Pending",
                max_length=30,
            ),
        ),
    ]
