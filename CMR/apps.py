from django.apps import AppConfig
from django.core import checks


class CMRAppConfig(AppConfig):
    name = 'CMR'

    def ready(self) -> None:
        from CMR.checks import check_dev_mode

        checks.register(check_dev_mode)
