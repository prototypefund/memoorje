import secrets
import string
import struct
import subprocess
from typing import Iterable, Mapping

from django.conf import settings
from memoorje_crypto.formats import EncryptionV1

from memoorje.models import Capsule, CapsuleRecipient, Keyslot, PartialKey


class RecryptError(Exception):
    pass


def recrypt_capsule(capsule: "Capsule", partial_keys: Iterable["PartialKey"]) -> Mapping["CapsuleRecipient", str]:
    password = _combine_partial_keys(partial_keys)
    secret = _decrypt_secret(capsule, password)
    return _create_recipient_keyslots(capsule, secret)


def _combine_partial_keys(partial_keys: Iterable["PartialKey"]) -> bytes:
    keys_as_input_str = "\n".join([key.data.hex() for key in partial_keys])
    with subprocess.Popen(
        [settings.SECRET_SHARE_COMBINE_PATH], stdin=subprocess.PIPE, stdout=subprocess.PIPE
    ) as combine_process:
        stdout, _ = combine_process.communicate(input=keys_as_input_str.encode())
    if combine_process.returncode == 0:
        return stdout
    else:
        raise RecryptError("secret-share-combine returned non-zero exit status.")


def _create_recipient_keyslots(capsule: "Capsule", secret: bytes) -> Mapping["CapsuleRecipient", str]:
    result = {}
    for recipient in capsule.recipients.all():
        new_password = _generate_password()
        new_data = _encrypt_secret(secret, new_password.encode())
        capsule.keyslots.create(purpose=Keyslot.Purpose.PASSWORD, data=new_data)
        result[recipient] = new_password
    return result


def _decrypt_secret(capsule: "Capsule", sss_password: bytes) -> bytes:
    try:
        sss_keyslot = capsule.keyslots.get(purpose=Keyslot.Purpose.SSS)
        secret = sss_keyslot.decrypt(sss_password)
        return secret
    except (Keyslot.DoesNotExist, Keyslot.MultipleObjectsReturned) as e:
        raise RecryptError(f"Not exactly one keyslot with purpose SSS found for capsule {capsule.pk}.") from e
    except struct.error as e:
        raise RecryptError(f"Decryption of secret failed for capsule {capsule.pk}.") from e


def _encrypt_secret(secret: bytes, password: bytes) -> bytes:
    encryption = EncryptionV1(iv_size_bytes=64)
    return encryption.encrypt(password, secret)


def _generate_password() -> str:
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return "".join(secrets.choice(alphabet) for _ in range(settings.RECIPIENT_PASSWORD_LENGTH))
