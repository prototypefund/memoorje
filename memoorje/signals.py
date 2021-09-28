from django.db.models.signals import post_delete, post_save, pre_delete
from django.dispatch import receiver

from memoorje.models import CapsuleContent


@receiver(post_delete, sender=CapsuleContent)
@receiver(post_save, sender=CapsuleContent)
def touch_capsule(sender, instance: CapsuleContent, **kwargs):
    instance.capsule.touch()


@receiver(pre_delete, sender=CapsuleContent)
def delete_data_file(sender, instance: CapsuleContent, **kwargs):
    instance.data.delete(False)
