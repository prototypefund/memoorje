from django.conf import settings
from django.db.models import FileField
from django.db.models.fields.files import FieldFile
from django.urls import reverse

from memoorje.data_storage.storage import CapsuleDataStorage


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
