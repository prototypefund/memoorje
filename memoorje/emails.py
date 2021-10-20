from djeveric import BaseConfirmationEmail


class CapsuleReceiverConfirmationEmail(BaseConfirmationEmail):
    def get_message(self, context):
        return f"Token: {context['token']}"
