from Django.utils.logger import log_debug
log_debug("Cargando urls de app_ai")

from django.urls import path
from . import views

urlpatterns = []