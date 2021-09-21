from django.apps import AppConfig


class MemoorjeConfig(AppConfig):
    name = "memoorje"

    def ready(self):
        # noinspection PyUnresolvedReferences
        from . import signals  # noqa: F401
