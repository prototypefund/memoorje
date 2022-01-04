from djeveric.emails import ConfirmationEmail


class BaseEmail(ConfirmationEmail):
    pass


class CapsuleHintsEmail(BaseEmail):
    def get_body(self, context: dict[str]) -> str:
        return "Your capsule has inactive recipients"


class CapsuleReceiverConfirmationEmail(BaseEmail):
    def get_body(self, context: dict[str]) -> str:
        return f"pk: {context['pk']}, token: {context['token']}"


class CapsuleReceiverReleaseNotificationEmail(BaseEmail):
    def get_body(self, context: dict[str]) -> str:
        return "{password} {token}".format(**context)


class ReminderEmail(BaseEmail):
    def get_body(self, context: dict[str]) -> str:
        return "Check recipient data for your capsules"
