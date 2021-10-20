from djeveric.emails import ConfirmationEmail


class CapsuleReceiverConfirmationEmail(ConfirmationEmail):
    def get_body(self, context):
        return f"pk: {context['pk']}, token: {context['token']}"
