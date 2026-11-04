from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0076_health_cert_no_expiry"),
    ]

    operations = [
        migrations.AddField(
            model_name="users",
            name="granted_permissions",
            field=models.JSONField(blank=True, default=list),
        ),
    ]
