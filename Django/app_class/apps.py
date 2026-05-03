from django.apps import AppConfig
from Django.utils.logger import log_debug

class AppClassConfig(AppConfig):
    name = 'app_class'
    log_debug(f"Configurando app: {name}")
