from djeveric.emails import ConfirmationEmail
from templated_email import get_templated_mail


class TemplatedEmail(ConfirmationEmail):
    template_name: str

    def get_template_name(self):
        return self.template_name

    def send(self, context):
        template_name = self.get_template_name()
        mail = get_templated_mail(
            context=context,
            template_name=template_name,
            to=[self.email],
        )
        mail.send()


# mails sent to the capsule owner


class CapsuleHintsEmail(TemplatedEmail):
    template_name = "owner_capsule_hints_notification"


class RecipientsChangedNotificationEmail(TemplatedEmail):
    template_name = "owner_recipients_changed_notification"


class ReleaseInitiatedNotificationEmail(TemplatedEmail):
    template_name = "owner_release_initiated_notification"


class ReminderEmail(TemplatedEmail):
    template_name = "owner_reminder"


# mails sent to the capsule recipients


class CapsuleRecipientConfirmationEmail(TemplatedEmail):
    template_name = "recipient_confirmation"


class CapsuleRecipientReleaseNotificationEmail(TemplatedEmail):
    template_name = "recipient_release_notification"


# mails sent to the capsule trustees


class TrusteePartialKeyInvitationEmail(TemplatedEmail):
    template_name = "trustee_partial_key_invitation"
