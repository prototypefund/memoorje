from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from memoorje.models import Capsule, CapsuleContent, Keyslot


@receiver(post_delete, sender=CapsuleContent)
@receiver(post_save, sender=CapsuleContent)
@receiver(post_delete, sender=Keyslot)
@receiver(post_save, sender=Keyslot)
def touch_capsule(instance: CapsuleContent, **kwargs):
    instance.capsule.touch()


@receiver(post_save, sender=Capsule)
def set_recursive_capsule_relation(instance: Capsule, created: bool, **kwargs):
    if created:
        instance.capsule = instance
        instance.save()
