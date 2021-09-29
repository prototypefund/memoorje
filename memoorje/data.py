import uuid

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db.models import FileField
from django.db.models.fields.files import FieldFile
from django.urls import reverse


class CapsuleDataFile(FieldFile):
    @property
    def url(self):
        self._require_file()
        return reverse("capsule-data", args=[self.instance.pk])


class CapsuleDataField(FileField):
    attr_class = CapsuleDataFile

    def __init__(self, **kwargs):
        kwargs.setdefault("storage", CapsuleDataStorage(location=settings.CAPSULE_DATA_DIR))
        super().__init__(**kwargs)


class CapsuleDataStorage(FileSystemStorage):
    def get_valid_name(self, name):
        return str(uuid.uuid4())

    def url(self, name):
        raise NotImplementedError("use url property of CapsuleDataField instead")
