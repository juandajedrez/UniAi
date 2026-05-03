from django.apps import AppConfig

from Django.utils.logger import log_debug


class AppUsersConfig(AppConfig):
    name = 'app_users'
    log_debug(f"Configurando app: {name}")
