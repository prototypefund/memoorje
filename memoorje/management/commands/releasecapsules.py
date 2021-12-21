from django.core.management import BaseCommand

from memoorje.models import Capsule


class Command(BaseCommand):
    help = "Sends notifications to capsule receivers when the capsule was released"

    def handle(self, *args, **options):
        for capsule in Capsule.objects.all():
            passwords = capsule.release()
            if passwords is not None:
                for receiver, password in passwords.items():
                    receiver.send_release_notification(password)
