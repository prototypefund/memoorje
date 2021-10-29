from djeveric.emails import ConfirmationEmail


class BaseEmail(ConfirmationEmail):
    pass


class CapsuleReceiverConfirmationEmail(BaseEmail):
    def get_body(self, context: dict[str]) -> str:
        return f"pk: {context['pk']}, token: {context['token']}"


class ReminderEmail(BaseEmail):
    def get_body(self, context: dict[str]) -> str:
        return "Check recipient data for your capsules"
