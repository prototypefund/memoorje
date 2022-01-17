from datetime import timedelta

from django.conf import settings
from django.core.management import BaseCommand
from django.utils.timezone import now

from memoorje.models import Capsule


class Command(BaseCommand):
    help = "Sends hints about a capsule to the owner"

    def handle(self, *args, **options):
        def recipient_is_inactive(recipient):
            return not recipient.is_active() and (
                (now() - recipient.created_on) >= timedelta(days=settings.INACTIVE_RECIPIENT_HINT_DAYS)
            )

        for capsule in Capsule.objects.all():
            # send hints for capsules with inactive recipients
            inactive_recipients = [r for r in capsule.recipients.all() if recipient_is_inactive(r)]
            if len(inactive_recipients) > 0:
                capsule.send_hints(inactive_recipients=inactive_recipients)
