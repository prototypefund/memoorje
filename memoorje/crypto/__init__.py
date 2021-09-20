"""
This module contains encryption formats used by memoorje.

Once implemented and officially published the inner workings of any format MUST NOT be changed.
Specifically the VERSION field MUST NEVER be changed.

Encryption formats created here will need a second working TypeScript/EcmaScript implementation in libjs/crypto
that is compatible with the Web Cryptography API or any other cryptographic library available for browsers.
"""

import collections
import dataclasses
import io
import struct
import typing

try:
    from Crypto.Cipher import AES
    from Crypto.Hash import SHA256
    from Crypto.Protocol.KDF import PBKDF2
    from Crypto.Random import get_random_bytes
except ImportError:
    # We’ve encountered different import names for the cryptodome modules.
    from Cryptodome.Cipher import AES
    from Cryptodome.Hash import SHA256
    from Cryptodome.Protocol.KDF import PBKDF2
    from Cryptodome.Random import get_random_bytes

__all__ = [
    "EncryptionV1",
]


class _DataStreamPositionTracker:
    def __init__(self, data: bytes, initial_position: int = 0):
        self._position = initial_position
        self._data = data

    def get(self, byte_count: typing.Optional[int] = None):
        if byte_count is not None:
            new_position = self._position + byte_count
        else:
            new_position = len(self._data)
        result = self._data[self._position : new_position]
        self._position = new_position
        return result


class _EncryptionFormatMeta(type):
    @property
    def VERSION_FIELD_STRUCT(cls) -> struct.Struct:
        return struct.Struct(f">{len(cls.VERSION)}s")


class _EncryptionFormat(metaclass=_EncryptionFormatMeta):
    VERSION: bytes = None

    @classmethod
    def _parse_version(cls, data: bytes) -> bytes:
        raw_version_data = data[0 : cls.VERSION_FIELD_STRUCT.size]
        return cls.VERSION_FIELD_STRUCT.unpack(raw_version_data)[0]

    @classmethod
    def does_handle_data_stream(cls, data: bytes) -> bool:
        return cls._parse_version(data) == cls.VERSION

    @classmethod
    def _create_buffer(cls) -> typing.IO:
        buffer = io.BytesIO()
        # Write version. We will use it later to determine if the data
        # stream we receive can be processed by this encryption handler.
        buffer.write(cls.VERSION_FIELD_STRUCT.pack(cls.VERSION))
        return buffer

    @classmethod
    def decrypt(cls, password: str, data: bytes) -> bytes:
        raise NotImplementedError()

    def encrypt(self, password: str, data: bytes) -> bytes:
        raise NotImplementedError()


class EncryptionV1(_EncryptionFormat):
    """
    This encryption format is based on AES-GCM for data encryption,
    and PBKDF2+SHA256 for key derivation.

    Administrators may configure:
        A custom salt size and hash iterations for the key derivation algorithm.
        A custom iv size and encryption key size for the encryption.

    The format looks like this:
    ╔═════════════════════════════════════════════════════════════════════════════╗
    ╟─── HEADER ──────────────────────────────────────────────────────────────────╢
    ║ version                                                                     ║
    ║ metadata [ salt size, iv size, encryption key size, hash iteration count ]  ║
    ║ salt                                                                        ║
    ║ iv                                                                          ║
    ╟─── PAYLOAD ─────────────────────────────────────────────────────────────────╢
    ║ encrypted data                                                              ║
    ╚═════════════════════════════════════════════════════════════════════════════╝
    """

    VERSION = b"memoorje:encdata:v1"
    METADATA_FIELD_STRUCT = struct.Struct(">HHHL")
    METADATA_FIELD = collections.namedtuple(
        "METADATA_FIELD",
        [
            "salt_size_bytes",
            "iv_size_bytes",
            "encryption_key_size_bytes",
            "hash_iterations",
        ],
    )

    @dataclasses.dataclass()
    class Header:
        metadata: "EncryptionV1.METADATA_FIELD"
        salt: bytes
        iv: bytes

    def __init__(
        self,
        salt_size_bytes: int = 64,
        iv_size_bytes: int = 12,
        encryption_key_size_bytes: int = 32,
        hash_iterations: int = 250_000,
    ):
        """
        :param salt_size_bytes:
            The salt is used in key derivation to limit the practical feasibility
            of precomputed keys. It should be unique and therefore must not be smaller than 32 bytes.
        :param iv_size_bytes:
            AES usually takes IVs of 16 bytes which corresponds to the cipher block size, but
            in GCM mode it’s recommended to use 12 bytes. One can use more, but that doesn’t
            seem to increase security and may potentially impact speed and interoperability.
            See: https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-38d.pdf
        :param encryption_key_size_bytes:
            This refers to the key length used for encryption and can be either be
            16 bytes (128 bits), 24 bytes (196 bits), or 32 bytes (256 bits).
        :param hash_iterations:
            The hash is applied multiple times during key derivation. It should be increased
            along with the general computational power of the targeted devices.
        """
        # Enforce lower boundaries for configurable options so users don’t accidentally shoot themselves in the foot.
        assert salt_size_bytes >= 32
        assert iv_size_bytes >= 12
        assert encryption_key_size_bytes in (16, 24, 32)
        assert hash_iterations >= 100_000

        self.salt_size_bytes = salt_size_bytes
        self.iv_size_bytes = iv_size_bytes
        self.encryption_key_size_bytes = encryption_key_size_bytes
        self.hash_iterations = hash_iterations

    @classmethod
    def _create_cipher(
        cls,
        password: str,
        salt: bytes,
        iv: bytes,
        encryption_key_size_bytes: int,
        hash_iterations: int,
    ):
        key = PBKDF2(
            password,
            salt,
            dkLen=encryption_key_size_bytes,
            count=hash_iterations,
            hmac_hash_module=SHA256,
        )
        return AES.new(key, AES.MODE_GCM, iv)

    @classmethod
    def _split_data(cls, data: bytes) -> typing.Tuple[Header, bytes]:
        tracker = _DataStreamPositionTracker(data, cls.VERSION_FIELD_STRUCT.size)
        raw_metadata = tracker.get(cls.METADATA_FIELD_STRUCT.size)
        metadata = cls.METADATA_FIELD(*cls.METADATA_FIELD_STRUCT.unpack(raw_metadata))
        salt = tracker.get(metadata.salt_size_bytes)
        iv = tracker.get(metadata.iv_size_bytes)
        return cls.Header(metadata, salt, iv), tracker.get()

    def encrypt(self, password: str, data: bytes):
        salt = get_random_bytes(self.salt_size_bytes)
        iv = get_random_bytes(self.iv_size_bytes)
        cipher = self._create_cipher(password, salt, iv, self.encryption_key_size_bytes, self.hash_iterations)

        buffer = self._create_buffer()
        # Write metadata. We will need this information later to recreate the
        # exact cipher and derived cryptographic key that was used for encryption.
        buffer.write(
            self.METADATA_FIELD_STRUCT.pack(
                *self.METADATA_FIELD(
                    self.salt_size_bytes,
                    self.iv_size_bytes,
                    self.encryption_key_size_bytes,
                    self.hash_iterations,
                )
            )
        )
        # Write salt and iv used in key derivation and cipher.
        # As no one stops users from configuring awfully large salt or iv sizes it’s best not to put these in
        # the actual metadata field, but only their respective sizes, as the metadata field would otherwise
        # need to reserve a lot of space, whether it’s actually used or not.
        # Both the salt and the iv are allowed to be stored in plain text, so this is not a security issue.
        buffer.write(salt)
        buffer.write(iv)
        # Write encrypted data. This marks the end of our header.
        cipher_text, digest = cipher.encrypt_and_digest(data)
        buffer.write(cipher_text)
        buffer.write(digest)

        # now return the header and encrypted data stored in the buffer as a single byte stream
        buffer.seek(0)
        return buffer.read()

    @classmethod
    def decrypt(cls, password: str, data: bytes) -> bytes:
        header, encrypted_data = cls._split_data(data)
        cipher = cls._create_cipher(
            password,
            header.salt,
            header.iv,
            header.metadata.encryption_key_size_bytes,
            header.metadata.hash_iterations,
        )
        return cipher.decrypt_and_verify(encrypted_data[:-16], encrypted_data[-16:])
