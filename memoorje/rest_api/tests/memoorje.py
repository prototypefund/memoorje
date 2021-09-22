from rest_framework.test import APITestCase


class MemoorjeAPITestCase(APITestCase):
    base_url = "/api"

    def get_api_url(self, url: str, **kwargs):
        """
        Prepend the path to the full url for this test class.
        :param url: an url fragment
        :return: the url fragment prepended with the base url
        """
        base_url, *query = url.split("?")
        base_url += "" + (("?" + "".join(query)) if query else "")
        return f"{self.base_url}{base_url.format(**kwargs)}"
