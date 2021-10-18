import json

from djeveric import BaseConfirmationEmail


class CapsuleReceiverConfirmationEmail(BaseConfirmationEmail):
    def get_message(self, context):
        return json.dumps(
            {
                "token": context["token"],
            }
        )
