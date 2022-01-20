from decimal import Decimal

from django.utils.timezone import get_current_timezone
from rest_framework.reverse import reverse as drf_reverse
from rest_framework.test import APITestCase


def format_decimal(decimal, exp_str):
    return "{:f}".format(decimal.quantize(Decimal(exp_str)))


def format_time(time):
    return time.astimezone(get_current_timezone()).isoformat()


def reverse(basename, instance, response=None):
    return drf_reverse(f"{basename}-detail", [instance.pk], request=response.wsgi_request if response else None)


class MemoorjeAPITestCase(APITestCase):
    base_url = "/api"

    def get_api_url(self, url, **kwargs):
        """
        Prepend the path to the full url for this test class.
        :param url: an url fragment
        :return: the url fragment prepended with the base url
        """
        return f"{self.base_url}{url.format(**kwargs)}"
