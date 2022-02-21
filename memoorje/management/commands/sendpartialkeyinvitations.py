from datetime import timedelta

from django.conf import settings
from django.core.management import BaseCommand
from django.utils.timezone import now

from memoorje.models import Capsule


class Command(BaseCommand):
    help = "Sends invitations for providing partial keys to trustees"

    def handle(self, *args, **options):
        for capsule in Capsule.objects.filter(is_released=False):
            first_key = capsule.partial_keys.order_by("created_on").first()
            if (
                first_key is not None
                and not capsule.are_partial_key_invitations_sent
                and (first_key.created_on < (now() - timedelta(days=settings.CAPSULE_RELEASE_GRACE_PERIOD_DAYS)))
            ):
                for trustee in capsule.trustees.all():
                    trustee.send_partial_key_invitation()
                Capsule.objects.update(id=capsule.id, are_partial_key_invitations_sent=True)
