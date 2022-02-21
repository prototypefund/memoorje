from datetime import timedelta
import logging

from django.conf import settings
from django.core.management import BaseCommand
from django.utils.timezone import now

from memoorje.crypto import RecryptError
from memoorje.models import Capsule

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Sends notifications to capsule recipients when the capsule was released"

    def handle(self, *args, **options):
        for capsule in Capsule.objects.filter(partial_keys__isnull=False, is_released=False).distinct():
            has_grace_period_elapsed = now() >= (
                capsule.partial_keys.order_by("created_on").first().created_on
                + timedelta(days=settings.CAPSULE_RELEASE_GRACE_PERIOD_DAYS)
            )
            if has_grace_period_elapsed:
                try:
                    passwords = capsule.release()
                    if passwords is not None:
                        # send passwords to recipients
                        for recipient, password in passwords.items():
                            recipient.send_release_notification(password)
                        # remove partial keys
                        capsule.partial_keys.all().delete()
                except RecryptError as e:
                    logger.info(
                        f"Capsule {capsule.pk} is not released yet and has partial keys but releasing failed ({e})"
                    )
