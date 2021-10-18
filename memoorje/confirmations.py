from djeveric import BaseConfirmation

from memoorje.emails import CapsuleReceiverConfirmationEmail
from memoorje.models import CapsuleReceiver


class CapsuleReceiverConfirmation(BaseConfirmation):
    confirmation_email_class = CapsuleReceiverConfirmationEmail

    def confirm(self, instance: CapsuleReceiver):
        pass

    def is_confirmed(self) -> bool:
        pass
