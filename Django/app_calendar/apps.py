from django.apps import AppConfig
from Django.utils.logger import log_debug, log_success, log_error, log_warning

class AppCalendarConfig(AppConfig):
    name = 'app_calendar'
    log_debug(f"Configurando app: {name}")