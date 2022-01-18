from django.conf import settings
from djeveric.emails import ConfirmationEmail
from templated_email import get_templated_mail


class TemplatedEmail(ConfirmationEmail):
    template_name: str

    def format_link(self, key, **kwargs):
        return settings.FRONTEND_LINKS[key].format(**kwargs)

    def get_context(self, **kwargs):
        return kwargs

    def get_template_name(self):
        return self.template_name

    def send(self, **kwargs):
        template_name = self.get_template_name()
        mail = get_templated_mail(
            context=self.get_context(**kwargs),
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

    def get_context(self, **kwargs):
        recipient = kwargs["instance"]
        capsule = recipient.capsule
        return {
            "capsule": capsule,
            "confirm_link": self.format_link(
                "capsule_recipient_confirm", pk=recipient.pk, token=recipient.make_confirmation_token()
            ),
            "justification_link": self.format_link("capsule_recipient_confirm_justify"),
        }


class CapsuleRecipientReleaseNotificationEmail(TemplatedEmail):
    template_name = "recipient_release_notification"

    def get_context(self, **kwargs):
        recipient = kwargs["instance"]
        password = kwargs["password"]
        capsule = recipient.capsule
        token = recipient.recipient_token_generator_proxy.make_token()
        return {
            "access_link": self.format_link("capsule_token_access", pk=capsule.pk, token=token),
            "capsule": recipient.capsule,
            "justification_link": self.format_link("capsule_token_access_justify"),
            "password": password,
        }


# mails sent to the capsule trustees


class TrusteePartialKeyInvitationEmail(TemplatedEmail):
    template_name = "trustee_partial_key_invitation"

    def get_context(self, **kwargs):
        capsule = kwargs["instance"].capsule
        return {
            "capsule": capsule,
            "justification_link": self.format_link("partial_key_create_justify"),
            "partial_key_link": self.format_link("partial_key_create", capsule_pk=capsule.pk),
        }
