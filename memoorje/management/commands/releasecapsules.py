import logging

from django.core.management import BaseCommand

from memoorje.crypto import RecryptError
from memoorje.models import Capsule

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Sends notifications to capsule recipients when the capsule was released"

    def handle(self, *args, **options):
        for capsule in Capsule.objects.filter(partial_keys__isnull=False, is_released=False).distinct():
            try:
                passwords = capsule.release()
                if passwords is not None:
                    # send passwords to recipients
                    for recipient, password in passwords.items():
                        recipient.send_release_notification(password)
                    # remove partial keys
                    capsule.partial_keys.all().delete()
            except RecryptError as e:
                logger.info(f"Capsule {capsule.pk} is not released yet and has partial keys but releasing failed ({e})")
