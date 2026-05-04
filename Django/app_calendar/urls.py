from django.urls import path
from . import views, apis
from Django.utils.logger import log_debug

log_debug("Cargando urls de app_calendar")
urlpatterns = [
    # Calendario del usuario
    path("", views.user_calendar, name="user_calendar"),
    # Crear nuevo evento
    path("event/new/", views.create_event, name="create_event"),
    # Detalles del evento
    path("event/<int:event_id>/", views.event_detail, name="event_detail"),
    # Editar evento
    path("event/<int:event_id>/edit/", views.edit_event, name="edit_event"),
    # Asesorías
    path("event/advisings/", views.user_advisings, name="user_advisings"),
    # Solicitar nueva asesoría
    path("event/advisings/request/", views.request_advising, name="request_advising"),
    # Pendientes de aprobación (solo para profesores)
    path("event/advisings/pending/", views.pending_advisings, name="pending_advisings"),
    # Aceptar o rechazar asesoría (solo para profesores)
    path("event/advisings/<int:advising_id>/accept/", apis.accept_advising, name="accept_advising"),
    path("event/advisings/<int:advising_id>/reject/", apis.reject_advising, name="reject_advising"),
    ]
