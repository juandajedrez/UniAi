from django.apps import AppConfig
from Django.utils.logger import log_debug


class AppChatConfig(AppConfig):
    name = 'app_chat'
    log_debug(f"Configurando app: {name}")
