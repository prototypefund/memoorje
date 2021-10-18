from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from memoorje.confirmations import CapsuleReceiverConfirmation
from memoorje.models import CapsuleContent, CapsuleReceiver


@receiver(post_delete, sender=CapsuleContent)
@receiver(post_save, sender=CapsuleContent)
def touch_capsule(instance: CapsuleContent, **kwargs):
    instance.capsule.touch()


@receiver(post_save, sender=CapsuleReceiver)
def send_confirmation_request(instance: CapsuleReceiver, **kwargs):
    CapsuleReceiverConfirmation(instance).send_request()
