from django.urls import path

from . import views
from django.contrib.auth.views import LogoutView
from Django.utils.logger import log_debug
log_debug("Cargando urls de Users")
urlpatterns = [
    path("auth/", views.auth_view, name="auth"),
    path("register/", views.register_view, name="register"),
    # Caso 1: Usuario no logueado, pide reset por correo
    path("password-reset/", views.password_reset_request_view, name="password_reset_request"),
    # Confirmar código y nueva contraseña
    path("password-reset/confirm/", views.password_reset_confirm_view, name="password_reset_confirm"),
    # Caso 2: Usuario logueado, cambiar contraseña con la actual
    path("password-change/", views.password_change_view, name="password_change"),
    # Vista de confirmación genérica
    path("password-reset/done/", views.password_reset_done_view, name="password_reset_done"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_detail, name="profile_detail"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("socialmedia/delete/<int:pk>/", views.delete_social_media, name="delete_social_media"),
    path("contact/<int:profile_id>/", views.view_contact, name="view_contact_detail"),
    path("contacts/", views.view_contacts_list, name="view_contacts_list"),
    path("contact/<int:profile_id>/chat/", views.contact_chat, name="contact_chat"),
]
