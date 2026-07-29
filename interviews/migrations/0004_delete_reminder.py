# Generated for the Reminder-model move to the dedicated reminders app.
#
# When the Reminder model was extracted from the interviews app into its
# own reminders app (commit c6ef0817), the table was recreated as
# reminders_reminder. The old interviews_reminder table may still exist
# on production as a no-op leftover — we drop it in a follow-up if
# confirmed empty. This migration is STATE-ONLY: it tells Django that
# the Reminder model is intentionally no longer in the interviews app,
# so makemigrations stops proposing it as a deletion on every run.
#
# It does NOT touch the database (DeleteModel is a state operation in
# Django, not a schema operation), so any data that might still be in
# interviews_reminder on a long-running prod instance is preserved.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        # The most-recent leaf of this app's migration graph. We must
        # chain off 0003 (not 0002) because 0003 was the head at the
        # time 0004 was written, and Django disallows a graph where
        # two migrations both claim to be the leaf of an app.
        ('interviews', '0003_interview_more_fields'),
        # The new home of Reminder.
        ('reminders', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Reminder',
        ),
    ]
