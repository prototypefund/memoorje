from contextlib import contextmanager
from tempfile import TemporaryFile

from rest_framework.reverse import reverse
from rest_framework.test import APITestCase


@contextmanager
def create_test_data_file(data):
    with TemporaryFile() as f:
        f.write(data)
        f.seek(0)
        yield f


def get_url(basename, instance, response=None):
    return reverse(f"{basename}-detail", [instance.pk], request=response.wsgi_request if response else None)


class MemoorjeAPITestCase(APITestCase):
    base_url = "/api"

    def get_api_url(self, url, **kwargs):
        """
        Prepend the path to the full url for this test class.
        :param url: an url fragment
        :return: the url fragment prepended with the base url
        """
        return f"{self.base_url}{url.format(**kwargs)}"
