from django.urls import re_path
from . import consumers
from Django.utils.logger import log_debug
log_debug("Cargando routing.py")

websocket_urlpatterns = [
    re_path(r"ws/presence/$", consumers.PresenceConsumer.as_asgi()),
]
