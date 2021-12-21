from django.test import TestCase

from memoorje.crypto import (
    _combine_partial_keys,
    _create_recipient_keyslots,
    _decrypt_secret,
    _encrypt_secret,
    RecryptError,
)
from memoorje.models import Keyslot, PartialKey
from memoorje.tests.mixins import CapsuleReceiverMixin, KeyslotMixin


class CryptoTestCase(KeyslotMixin, CapsuleReceiverMixin, TestCase):
    def test_combine_partial_keys_returns_password(self):
        """Given a password and corresponding partial keys, _combine_partial_keys() shall reconstruct the password."""
        password = b"Arbitrary Password!"
        partial_keys = [
            PartialKey(
                data=bytes.fromhex(
                    "01ecbb2bee4722db397100e83b9702aad04776a9c8d5ce24930dc4815f6ca51a3789"
                    "d26a308016d4e04e413042e61b1e5cbf247ef7d6360143920fc3ca62506e2c1e8d0d"
                )
            ),
            PartialKey(
                data=bytes.fromhex(
                    "02a76763d4633e22d858383ddb87ff624992683809971bb658142221ee208c795089"
                    "d26a308016d4e04e413042e61b1e5cbf247ef7d6360143920fc3ca62506e2c1e8d0d"
                )
            ),
        ]
        result = _combine_partial_keys(partial_keys)
        self.assertEqual(result, password)

    def test_combine_insufficient_keys_raises_error(self):
        """Providing insufficient key data to _combine_partial_keys() raises an error."""
        partial_keys = [
            PartialKey(
                data=bytes.fromhex(
                    "01ecbb2bee4722db397100e83b9702aad04776a9c8d5ce24930dc4815f6ca51a3789"
                    "d26a308016d4e04e413042e61b1e5cbf247ef7d6360143920fc3ca62506e2c1e8d0d"
                )
            ),
        ]
        self.assertRaises(RecryptError, _combine_partial_keys, partial_keys)

    def test_decrypt_secret_returns_secret(self):
        """Given a capsule and a valid password, _decrypt_secret() shall return the secret."""
        password = b"My password"
        secret = b"Very hidden secret!"
        self.create_keyslot(purpose=Keyslot.Purpose.SSS, data=_encrypt_secret(secret, password))
        result = _decrypt_secret(self.capsule, password)
        self.assertEqual(result, secret)

    def test_decrypt_secret_raises_error_on_invalid_keyslot_data(self):
        """If the keyslot data is invalid _decrypt_secret() raises an error."""
        self.create_keyslot(purpose=Keyslot.Purpose.SSS, data=b"invalid data")
        self.assertRaises(RecryptError, _decrypt_secret, self.capsule, b"invalid password")

    def test_create_recipient_keyslots_returns_valid_passwords(self):
        secret = b"Very hidden secret!"
        self.create_capsule_receiver()
        passwords = _create_recipient_keyslots(self.capsule, secret)
        self.assertIn(self.capsule_receiver, passwords)
        self.assertEqual(self.capsule.keyslots.filter(purpose=Keyslot.Purpose.PASSWORD).count(), 1)
        keyslot = self.capsule.keyslots.get(purpose=Keyslot.Purpose.PASSWORD)
        result = keyslot.decrypt(passwords[self.capsule_receiver])
        self.assertEqual(result, secret)
