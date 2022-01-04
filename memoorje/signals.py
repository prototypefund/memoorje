from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from memoorje.models import Capsule, CapsuleContent, CapsuleReceiver


@receiver(post_delete, sender=CapsuleContent)
@receiver(post_save, sender=CapsuleContent)
def touch_capsule(instance: CapsuleContent, **kwargs):
    instance.capsule.touch()


@receiver(post_delete, sender=CapsuleReceiver)
@receiver(post_save, sender=CapsuleReceiver)
def send_notification(instance: CapsuleReceiver, **kwargs):
    instance.capsule.send_notification(recipients_changed=True)


@receiver(post_save, sender=Capsule)
def set_recursive_capsule_relation(instance: Capsule, created: bool, **kwargs):
    if created:
        instance.capsule = instance
        instance.save()
