import uuid

from django.core.files.storage import FileSystemStorage


class CapsuleDataStorage(FileSystemStorage):
    def get_valid_name(self, name):
        return str(uuid.uuid4())

    def url(self, name):
        raise NotImplementedError("use url property of CapsuleDataField instead")
