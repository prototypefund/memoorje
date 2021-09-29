from django.apps import AppConfig


class MemoorjeConfig(AppConfig):
    name = "memoorje"

    def ready(self):
        from django.utils.module_loading import autodiscover_modules

        autodiscover_modules("signals")
