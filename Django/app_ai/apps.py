from django.apps import AppConfig

from Django.utils.logger import log_debug


class AppAiConfig(AppConfig):
    name = 'app_ai'
    log_debug(f"Configurando app: {name}")
