from base64 import b64encode

from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.fields import FileField


class BinaryField(FileField):
    def to_internal_value(self, data: InMemoryUploadedFile):
        return data.read()

    def to_representation(self, value: bytes):
        return b64encode(value).decode()
