import os

from django.apps import AppConfig
from .utils.logger import *


class DjangoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Django'
    title("Cargando apps")
    log_debug(f"Configurando app: {name}")
    def ready(self):
        try:
            from app_ai.scripts.load_public_info import load_public_info_from_txt
            
            import Django.utils.signals
            from .settings import BASE_DIR
            DIR = os.path.join(BASE_DIR, "app_ai", "data","documents", "informacion_publica.txt")

            load_public_info_from_txt(DIR)
            log_success("Señales generales cargadas exitosamente")
        except Exception as e:
            log_error("Error cargando las señales", e)
            log_warning("El sistema está funcionando sin señales generales")

            
