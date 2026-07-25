from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Reminder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(help_text='Reminder message / details')),
                ('reminder_date', models.DateField(help_text='Date the reminder is for')),
                ('reminder_time', models.TimeField(help_text='Time the reminder is for')),
                ('is_completed', models.BooleanField(default=False, help_text='Mark as done when the user has acted on the reminder')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(help_text='Crew member (or other user) the reminder is for', on_delete=django.db.models.deletion.CASCADE, related_name='reminders', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Reminder',
                'verbose_name_plural': 'Reminders',
                'ordering': ['reminder_date', 'reminder_time'],
            },
        ),
    ]
