from base64 import b64encode

from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.fields import CharField, FileField


class BinaryField(FileField):
    def to_internal_value(self, data: InMemoryUploadedFile):
        return data.read()

    def to_representation(self, value: bytes):
        return b64encode(value).decode()


class HexDigestField(CharField):
    def to_internal_value(self, data: str) -> bytes:
        return bytes.fromhex(super().to_internal_value(data))

    def to_representation(self, value: bytes) -> str:
        return value.hex()
