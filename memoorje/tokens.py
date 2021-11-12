from typing import Iterable

from djeveric.tokens import TokenGeneratorProxy


class CapsuleReceiverTokenGeneratorProxy(TokenGeneratorProxy):
    def check_token(self, token: str):
        *_, token = token.partition("-")
        return super().check_token(token)

    def make_token(self):
        return "{}-{}".format(self.instance.pk, super().make_token())

    def get_token_data(self) -> Iterable[str]:
        return [
            # The pk of the capsule receiver ensures that users get access only to the capsule for this receiver.
            # If the receiver is revoked, the token gets invalid.
            str(self.instance.pk),
            # The access is read-only for a given state of the capsule. If the capsule was changed (which shouldn't
            # happen), access will be denied.
            str(self.instance.capsule.updated_on),
        ]
