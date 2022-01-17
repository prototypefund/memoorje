from django.test import TestCase

from memoorje.crypto import (
    _combine_partial_keys,
    _create_recipient_keyslots,
    _decrypt_secret,
    _encrypt_secret,
    RecryptError,
)
from memoorje.models import Keyslot
from memoorje.tests.mixins import CapsuleRecipientMixin, KeyslotMixin, PartialKeyMixin


class CryptoTestCase(KeyslotMixin, CapsuleRecipientMixin, PartialKeyMixin, TestCase):
    def test_combine_partial_keys_returns_password(self):
        """Given a password and corresponding partial keys, _combine_partial_keys() shall reconstruct the password."""
        self.create_combinable_partial_keys()
        result = _combine_partial_keys(self.capsule.partial_keys.all())
        self.assertEqual(result, self.combined_secret)

    def test_combine_insufficient_keys_raises_error(self):
        """Providing insufficient key data to _combine_partial_keys() raises an error."""
        self.create_combinable_partial_keys()
        self.assertRaises(RecryptError, _combine_partial_keys, [self.capsule.partial_keys.first()])

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
        self.create_capsule_recipient()
        passwords = _create_recipient_keyslots(self.capsule, secret)
        self.assertIn(self.capsule_recipient, passwords)
        self.assertEqual(self.capsule.keyslots.filter(purpose=Keyslot.Purpose.PASSWORD).count(), 1)
        keyslot = self.capsule.keyslots.get(purpose=Keyslot.Purpose.PASSWORD)
        result = keyslot.decrypt(passwords[self.capsule_recipient])
        self.assertEqual(result, secret)
