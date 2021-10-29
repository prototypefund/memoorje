from datetime import date

from dateutil.relativedelta import relativedelta
from django.core.management import BaseCommand

from memoorje.models import Capsule, User


class Command(BaseCommand):
    help = "Sends reminders to users with elapsed remind interval"

    def handle(self, *args, **options):
        for user in User.objects.all():
            # send reminders only to users owning at least one capsule
            if user.capsules.exists():
                remind_interval = relativedelta(months=user.remind_interval)
                if user.last_reminder_sent_on is None:
                    # the first reminder is sent relative to the creation of the oldest capsule
                    oldest_capsule: Capsule = user.capsules.order_by("created_on").first()
                    if date.today() >= (oldest_capsule.created_on.date() + remind_interval):
                        user.send_reminder()
                elif date.today() >= (user.last_reminder_sent_on + remind_interval):
                    # further reminders are sent according to the interval set
                    user.send_reminder()
