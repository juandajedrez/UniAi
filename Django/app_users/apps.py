from django.apps import AppConfig

from Django.utils.logger import log_debug, log_warning, log_error, log_success


class AppUsersConfig(AppConfig):
    name = 'app_users'
    log_debug(f"Configurando app: {name}")
    def ready(self):
        try:
            import app_users.signals
            log_success("Señales users cargadas exitosamente")
        except Exception as e:
            log_error("Error cargando las señales", e)
            log_warning("El sistema está funcionando sin señales users")
