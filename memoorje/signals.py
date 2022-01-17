from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from memoorje.models import Capsule, CapsuleContent, CapsuleRecipient, PartialKey


@receiver(post_delete, sender=CapsuleContent)
@receiver(post_save, sender=CapsuleContent)
def touch_capsule(instance: CapsuleContent, **kwargs):
    instance.capsule.touch()


@receiver(post_delete, sender=CapsuleRecipient)
@receiver(post_save, sender=CapsuleRecipient)
def send_recipient_change_notification(instance: CapsuleRecipient, **kwargs):
    instance.capsule.send_notification(recipients_changed=True)


@receiver(post_save, sender=PartialKey)
def send_release_init_notification(instance: PartialKey, created: bool, **kwargs):
    if created and instance.capsule.partial_keys.count() == 1:
        instance.capsule.send_notification(release_initiated=True)


@receiver(post_save, sender=Capsule)
def set_recursive_capsule_relation(instance: Capsule, created: bool, **kwargs):
    if created:
        instance.capsule = instance
        instance.save()
