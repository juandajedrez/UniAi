from Django.utils.logger import log_debug
log_debug("Cargando urls de app_chat")

from django.urls import path
from . import views

urlpatterns = [
    path("", views.chat_list, name="chat_list"),
    path("<int:chat_id>/", views.chat_view, name="chat_view"),
    path("<int:chat_id>/detail/", views.chat_detail, name="chat_detail"),

]
