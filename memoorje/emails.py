from urllib.parse import quote_plus

from django.conf import settings
from djeveric.emails import ConfirmationEmail
from html2text import HTML2Text
from rest_registration.signers.register import RegisterSigner
from rest_registration.signers.reset_password import ResetPasswordSigner
from rest_registration.utils.users import get_user_verification_id
from templated_email import get_templated_mail


def convert_html_to_text(html):
    converter = HTML2Text()
    converter.inline_links = False
    converter.protect_links = False
    converter.use_automatic_links = False
    converter.wrap_links = False
    return converter.handle(html)


class TemplatedEmail(ConfirmationEmail):
    template_name: str

    def format_link(self, key, **kwargs):
        quoted_kwargs = {k: quote_plus(str(v)) for k, v in kwargs.items()}
        return settings.FRONTEND_LINKS[key].format(**quoted_kwargs)

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

    def get_context(self, **kwargs):
        capsule = kwargs["instance"]
        inactive_recipients = kwargs["inactive_recipients"]
        return {
            "capsule": capsule,
            "inactive_recipients": inactive_recipients,
            "justify_link": self.format_link("capsule_hints_justify"),
        }


class JournalNotificationEmail(TemplatedEmail):
    template_name = "owner_journal_notification"

    def get_context(self, **kwargs):
        return {
            "justify_link": self.format_link("user_journal_justify"),
        }


class ReleaseInitiatedNotificationEmail(TemplatedEmail):
    template_name = "owner_release_initiated_notification"

    def get_context(self, **kwargs):
        capsule = kwargs["instance"]
        return {
            "capsule": capsule,
            "abort_link": self.format_link("capsule_release_abort", pk=capsule.pk),
            "justify_link": self.format_link("capsule_release_abort_justify"),
        }


class ReminderEmail(TemplatedEmail):
    template_name = "owner_reminder"

    def get_context(self, **kwargs):
        user = kwargs["instance"]
        return {
            "check_link": self.format_link("user_reminder_check"),
            "justify_link": self.format_link("user_reminder_check_justify"),
            "user": user,
        }


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


# mails sent to any user


class UserRegistrationConfirmationEmail(TemplatedEmail):
    template_name = "user_registration_confirmation"

    def get_context(self, **kwargs):
        user = kwargs["instance"]
        return {
            "confirm_link": self.format_link("user_registration_confirm", **self.get_signed_data(user)),
            "justification_link": self.format_link("user_registration_confirm_justify"),
        }

    def get_signed_data(self, user):
        signer = RegisterSigner({"user_id": get_user_verification_id(user)}, strict=False)
        return signer.get_signed_data()


class UserResetPasswordEmail(TemplatedEmail):
    template_name = "user_reset_password"

    def get_context(self, **kwargs):
        user = kwargs["instance"]
        return {
            "reset_link": self.format_link("user_password_reset", **self.get_signed_data(user)),
            "justification_link": self.format_link("user_password_reset_justify"),
        }

    def get_signed_data(self, user):
        signer = ResetPasswordSigner({"user_id": get_user_verification_id(user)}, strict=False)
        return signer.get_signed_data()
