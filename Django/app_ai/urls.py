from Django.utils.logger import log_debug
log_debug("Cargando urls de app_ai")

from django.urls import path
from . import views

urlpatterns = [    
    path("chat/",       views.chat_view,   name="chat"),
    path("chat/stream/",views.chat_stream, name="chat_stream"),
    path("chat/limpiar/",views.limpiar_chat,name="limpiar_chat"),
]