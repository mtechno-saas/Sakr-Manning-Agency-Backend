from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('interviews', '0002_reminder'),
        ('companies', '0014_joborderposition_created_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='interview',
            name='principal',
            field=models.ForeignKey(
                blank=True,
                help_text='Company doing the hiring',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='interviews',
                to='companies.company',
            ),
        ),
        migrations.AddField(
            model_name='interview',
            name='position',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='interview',
            name='type',
            field=models.CharField(
                blank=True,
                choices=[('Phone', 'Phone'), ('Video', 'Video'), ('In-Person', 'In-Person')],
                max_length=20,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='interview',
            name='duration_minutes',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='interview',
            name='location',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='interview',
            name='result',
            field=models.CharField(
                blank=True,
                choices=[('Pending', 'Pending'), ('Pass', 'Pass'), ('Fail', 'Fail'), ('Hold', 'Hold')],
                max_length=20,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='interview',
            name='feedback',
            field=models.TextField(blank=True, null=True),
        ),
    ]
