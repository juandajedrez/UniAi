from django.apps import AppConfig

from Django.utils.logger import log_debug


class AppAdminConfig(AppConfig):
    name = 'app_admin'
    log_debug(f"Configurando app: {name}")
