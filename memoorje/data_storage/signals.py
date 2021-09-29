from django.db.models.signals import pre_delete
from django.dispatch import receiver

from memoorje.models import CapsuleContent


@receiver(pre_delete, sender=CapsuleContent)
def delete_data_file(sender, instance: CapsuleContent, **kwargs):
    instance.data.delete(False)
