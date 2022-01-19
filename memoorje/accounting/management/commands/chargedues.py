from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.management import BaseCommand
from django.utils.timezone import now

from memoorje.accounting.models import Transaction
from memoorje.models import Capsule


class Command(BaseCommand):
    help = "Charge monthly dues from users' accounts"

    def handle(self, *args, **options):
        def has_dues_paid_after(c, t):
            return (
                c.transactions.filter(type=Transaction.Type.MONTHLY_DUE)
                .order_by("created_on")
                .exclude(created_on__lt=t)
                .exists()
            )

        def charge_due(c):
            c.transactions.create(
                account_holder=c.owner, type=Transaction.Type.MONTHLY_DUE, amount=-settings.MONTHLY_DUE_PER_CAPSULE
            )

        for capsule in Capsule.objects.all():
            due_time = capsule.created_on + relativedelta(months=1)
            while due_time <= now():
                if not has_dues_paid_after(capsule, due_time):
                    charge_due(capsule)
                due_time += relativedelta(months=1)
