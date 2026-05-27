



from Django.utils.logger import log_debug, log_error, log_info, log_success
log_debug("Cargando signals.py en app_users")

from Django import settings
from django.db.models.signals import post_save, post_delete
from django.dispatch import Signal, receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out
from .models import *
from app_notifications.models import Notifications
from app_chat.models import Chat
from django.core.mail import send_mail

# -----------------------------
# Señales personalizadas
# -----------------------------
log_debug("Creando señales personalizadas")
user_registered = Signal()         # Nuevo usuario registrado
user_profile_updated = Signal()    # Perfil de usuario actualizado
user_password_changed = Signal()   # Contraseña de usuario cambiada
user_role_changed = Signal()       # Rol de usuario cambiado
user_registered_error = Signal()   # Error al registrar usuario

# ------------------ Login ----------------------------
@receiver(user_logged_in)
def on_user_logged_in(sender, request, user, **kwargs):
    log_info(f"Usuario {user.first_name} inició sesión desde {request.META.get('REMOTE_ADDR')}")

# ------------------ Logout ----------------------------
@receiver(user_logged_out)
def on_user_logged_out(sender, request, user, **kwargs):
    log_info(f"Usuario {user.first_name} cerró sesión desde {request.META.get('REMOTE_ADDR')}")

# ------------------ Profile ----------------------------
@receiver(post_save, sender=Profile)
def on_profile_created(sender, instance: Profile, created, **kwargs):
    if created:
        log_success(f"Perfil creado: {instance.user.username} ({instance.get_role_display()})")
    else:
        log_success(f"Perfil actualizado: {instance.user.username} ({instance.get_role_display()})")

@receiver(post_delete, sender=Profile)
def on_profile_deleted(sender, instance: Profile, **kwargs):
    log_success(f"Perfil eliminado: {instance.user.username} ({instance.get_role_display()})")

# ------------------ SocialMedia ----------------------------
@receiver(post_save, sender=SocialMedia)
def on_socialmedia_created(sender, instance: SocialMedia, created, **kwargs):
    if created:
        log_success(f"Red social creada: {instance.name or 'Sin nombre'} para {instance.profile.user.username}")
    else:
        log_success(f"Red social actualizada: {instance.name or 'Sin nombre'} para {instance.profile.user.username}")

@receiver(post_delete, sender=SocialMedia)
def on_socialmedia_deleted(sender, instance: SocialMedia, **kwargs):
    log_success(f"Red social eliminada: {instance.name or 'Sin nombre'} para {instance.profile.user.username}")

@receiver(user_registered)
def on_user_registered(sender, profile:Profile, **kwargs):
    
    "Pendiente: Crear IA para el usuario"

    #Enviar notificacion para cambiar contraseña
    try:
        Notifications.objects.create(
            user=profile.user,
            content="Bienvenido a UniAI! Por favor, cambia tu contraseña para asegurar tu cuenta."
        )
        #Enviar notificacion para completar perfil
        Notifications.objects.create(
            user=profile.user,
            content="Por favor, completa tu perfil para disfrutar de todas las funciones de UniAI."
        )
        
    except Exception as e:
        log_error(f"Error al crear notificaciones para {profile.user.username}", e)

    #Crear chat con sigo mismo para guardar mensajes importantes
    chat: Chat = Chat.objects.create(description=f"Chat de {profile.user.first_name}", state="ACTIVE")
    chat.users.add(profile.user)
    try:
        send_mail(
            subject="Usuario registrado",
            message="Tu cuenta ha sido creada exitosamente.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[profile.user.email]
        )
        log_info(f"Correo de bienvenida enviado a {profile.user.username} ({profile.user.email})")
    except Exception as e:
        log_error(f"Error al enviar correo de bienvenida a {profile.user.username}", e)
    log_success(f"Nuevo usuario registrado: {profile.user.username} ({profile.user.email})")

@receiver(user_profile_updated)
def on_user_profile_updated(sender, profile: Profile, **kwargs):
    log_success(f"Perfil actualizado: {profile.user.username} ({profile.get_role_display()})")

@receiver(user_password_changed)
def on_user_password_changed(sender, user: User, **kwargs):
    log_success(f"Contraseña cambiada para el usuario: {user.username}")

@receiver(user_role_changed)
def on_user_role_changed(sender, profile: Profile, old_role: str, new_role: str, **kwargs):
    log_success(f"Rol cambiado para {profile.user.username}: {old_role} → {new_role}")

@receiver(user_registered_error)
def on_user_registered_error(sender, profile:Profile, **kwargs):
    log_info(f"deshaciendo registro de usuario: {profile.user.username} ({profile.user.email})")
    #Eliminar el usuario y perfil creado
    try:
        profile.user.delete()
    except Exception as e:
        log_error(f"Error al eliminar usuario {profile.user.username}", e)

# ------------------ User ----------------------------
@receiver(post_save, sender=User)
def on_user_created(sender, instance: User, created, **kwargs):
    if created:
        log_success(f"Usuario creado: {instance.username} ({instance.email})")
    else:
        log_success(f"Usuario actualizado: {instance.username} ({instance.email})")

@receiver(post_delete, sender=User)
def on_user_deleted(sender, instance: User, **kwargs):
    log_success(f"Usuario eliminado: {instance.username} ({instance.email})")
