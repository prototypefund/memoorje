from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from rest_registration.signals import user_registered

from memoorje.models import Capsule, CapsuleContent, CapsuleRecipient, JournalEntry, PartialKey, User


@receiver(post_delete, sender=CapsuleContent)
@receiver(post_save, sender=CapsuleContent)
def touch_capsule(instance: CapsuleContent, **kwargs):
    instance.capsule.touch()


@receiver(post_delete, sender=CapsuleRecipient)
@receiver(post_save, sender=CapsuleRecipient)
def create_journal_entry(instance, **kwargs):
    def _create_journal_entry(action):
        entry = JournalEntry(user=instance.capsule.owner, capsule=instance.capsule, action=action)
        entry.entity = instance
        entry.save()

    if "created" in kwargs:
        if kwargs["created"]:
            _create_journal_entry(JournalEntry.Action.CREATE)
        else:
            _create_journal_entry(JournalEntry.Action.UPDATE)
    else:
        _create_journal_entry(JournalEntry.Action.DELETE)


@receiver(post_save, sender=PartialKey)
def send_release_init_notification(instance: PartialKey, created: bool, **kwargs):
    if created and instance.capsule.partial_keys.count() == 1:
        instance.capsule.send_notification(release_initiated=True)


@receiver(user_registered)
def send_user_registration_confirmation(user: User, **kwargs):
    user.send_registration_confirmation()


@receiver(post_save, sender=Capsule)
def set_recursive_capsule_relation(instance: Capsule, created: bool, **kwargs):
    if created:
        instance.capsule = instance
        instance.save()
