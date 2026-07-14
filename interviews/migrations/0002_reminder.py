from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('interviews', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reminder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(help_text='Reminder details / message body')),
                ('reminder_date', models.DateField()),
                ('reminder_time', models.TimeField()),
                ('is_completed', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(help_text='Crew member the reminder is for', on_delete=django.db.models.deletion.CASCADE, related_name='reminders', to='api.users')),
            ],
            options={
                'ordering': ['reminder_date', 'reminder_time'],
            },
        ),
    ]
