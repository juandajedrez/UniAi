from django.apps import AppConfig
from .utils.logger import *

class DjangoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Django'
    title("Cargando apps")
    log_debug(f"Configurando app: {name}")
    def ready(self):
        try:
            import Django.utils.signals
            log_success("Señales cargadas exitosamente")
        except Exception as e:
            log_error("Error cargando las señales", e)
            log_warning("El sistema está funcionando sin señales")

            
