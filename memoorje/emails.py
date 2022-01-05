from djeveric.emails import ConfirmationEmail


class BaseEmail(ConfirmationEmail):
    pass


class CapsuleHintsEmail(BaseEmail):
    def get_body(self, context: dict[str]) -> str:
        return "Your capsule has inactive recipients"


class RecipientsChangedNotificationEmail(BaseEmail):
    def get_body(self, context: dict[str]) -> str:
        return "Recipients of your capsule have changed"


class ReleaseInitiatedNotificationEmail(BaseEmail):
    def get_body(self, context: dict[str]) -> str:
        return "Release of the capsule has been initiated"


class CapsuleReceiverConfirmationEmail(BaseEmail):
    def get_body(self, context: dict[str]) -> str:
        return f"pk: {context['pk']}, token: {context['token']}"


class CapsuleReceiverReleaseNotificationEmail(BaseEmail):
    def get_body(self, context: dict[str]) -> str:
        return "{password} {token}".format(**context)


class ReminderEmail(BaseEmail):
    def get_body(self, context: dict[str]) -> str:
        return "Check recipient data for your capsules"


class TrusteePartialKeyInvitationEmail(BaseEmail):
    def get_body(self, context: dict[str]) -> str:
        return "You are invited to provide your partial key"
