from datetime import timedelta

from django.conf import settings
from django.core.management import BaseCommand
from django.utils.timezone import now

from memoorje.models import User


class Command(BaseCommand):
    help = "Sends a notification about new journal entries to user"

    def handle(self, *args, **options):
        for user in User.objects.all():
            journal_entries = user.journal_entries.order_by("created_on").filter(
                created_on__lte=now() - timedelta(minutes=settings.JOURNAL_NOTIFICATION_GRACE_PERIOD_MINUTES)
            )
            if user.latest_notified_journal_entry is not None:
                journal_entries = journal_entries.filter(created_on__gt=user.latest_notified_journal_entry.created_on)
            latest_entry = journal_entries.last()
            if latest_entry is not None:
                user.send_journal_notification()
                user.latest_notified_journal_entry = latest_entry
                user.save()
