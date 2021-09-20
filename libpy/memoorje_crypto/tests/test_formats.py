import os
import unittest

from memoorje_crypto.formats import EncryptionV1
from tests import FILES_DIR


class EncryptionV1Test(unittest.TestCase):
    def test_encrypted_data_can_be_decrypted(self):
        data = b"my encrypted data"
        password = "abc123"
        encryption = EncryptionV1(iv_size_bytes=64)
        encrypted_data = encryption.encrypt(password, data)
        self.assertTrue(
            EncryptionV1.does_handle_data_stream(encrypted_data),
            "EncryptionV1 should handle its own encrypted data",
        )
        self.assertEqual(
            data,
            EncryptionV1.decrypt(password, encrypted_data),
            "Data encrypted by EncryptionV1 must also be decipherable by it.",
        )

    def test_previously_encrypted_data_can_be_decrypted(self):
        encryption = EncryptionV1()
        with open(os.path.join(FILES_DIR, "encrypted-v1.bin"), "rb") as encrypted_file:
            self.assertEqual(
                encryption.decrypt("abc123", encrypted_file.read()),
                b"This has been encrypted upfront",
            )
