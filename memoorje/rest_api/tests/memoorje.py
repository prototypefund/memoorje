from contextlib import contextmanager
from tempfile import TemporaryFile

from rest_framework.test import APITestCase


@contextmanager
def create_test_data_file(data):
    with TemporaryFile() as f:
        f.write(data)
        f.seek(0)
        yield f


class MemoorjeAPITestCase(APITestCase):
    base_url = "/api"

    def get_api_url(self, url, **kwargs):
        """
        Prepend the path to the full url for this test class.
        :param url: an url fragment
        :return: the url fragment prepended with the base url
        """
        return f"{self.base_url}{url.format(**kwargs)}"
