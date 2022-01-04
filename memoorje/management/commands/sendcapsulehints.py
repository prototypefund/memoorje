from datetime import timedelta

from django.conf import settings
from django.core.management import BaseCommand
from django.utils.timezone import now

from memoorje.models import Capsule


class Command(BaseCommand):
    help = "Sends hints about a capsule to the owner"

    def handle(self, *args, **options):
        def receiver_is_inactive(receiver):
            return not receiver.is_active() and (
                (now() - receiver.created_on) >= timedelta(days=settings.INACTIVE_RECEIVER_HINT_DAYS)
            )

        for capsule in Capsule.objects.all():
            # send hints for capsules with inactive receivers
            inactive_receivers = [r for r in capsule.receivers.all() if receiver_is_inactive(r)]
            if len(inactive_receivers) > 0:
                capsule.send_hints(inactive_receivers=inactive_receivers)
