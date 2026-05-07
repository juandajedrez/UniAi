from django.apps import AppConfig
from Django.utils.logger import log_debug, log_success, log_error, log_warning

class AppCalendarConfig(AppConfig):
    name = 'app_calendar'
    log_debug(f"Configurando app: {name}")
    def ready(self):
        try:
            import app_calendar.signals
            log_success("Señales calendar cargadas exitosamente")
        except Exception as e:
            log_error("Error cargando las señales", e)
            log_warning("El sistema está funcionando sin señales calendar")