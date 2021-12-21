import logging

from django.core.management import BaseCommand

from memoorje.crypto import RecryptError
from memoorje.models import Capsule

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Sends notifications to capsule receivers when the capsule was released"

    def handle(self, *args, **options):
        for capsule in Capsule.objects.all():
            try:
                passwords = capsule.release()
                if passwords is not None:
                    for receiver, password in passwords.items():
                        receiver.send_release_notification(password)
            except RecryptError as e:
                logger.info(f"Capsule {capsule.pk} is not released yet and has partial keys but releasing failed ({e})")
