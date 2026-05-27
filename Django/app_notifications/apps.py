from django.apps import AppConfig

from Django.utils.logger import log_debug


class AppNotificationsConfig(AppConfig):
    name = 'app_notifications'
    log_debug(f"Configurando app: {name}")