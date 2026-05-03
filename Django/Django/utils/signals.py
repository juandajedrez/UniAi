""" Archivo de señales para la aplicación Django. 
Aquí se definen las señales personalizadas 
y los receptores para manejar eventos específicos en la aplicación, 
como la creación de eventos, notificaciones, cambios en el perfil de usuario, entre otros."""

#Importaciones necesarias
from django.db.models.signals import post_save, post_delete
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver, Signal
from .scripts import *
log_debug("Cargando signals.py")
# -----------------------------
# Señales personalizadas
# -----------------------------
log_debug("Creando señales personalizadas")
notification_sent = Signal()       # Notificación enviada
notification_read = Signal()       # Notificación leída
user_registered = Signal()         # Nuevo usuario registrado
user_profile_updated = Signal()    # Perfil de usuario actualizado
user_password_changed = Signal()   # Contraseña de usuario cambiada
user_role_changed = Signal()       # Rol de usuario cambiado
system_error = Signal()            # Error del sistema (para monitoreo)
class_event_created = Signal()     # Evento de clase creado
class_event_updated = Signal()     # Evento de clase actualizado
advising_requested = Signal()      # Solicitud de asesoría
advising_accepted = Signal()       # Aceptación de asesoría
advising_rejected = Signal()       # Rechazo de asesoría
class_event_deleted = Signal()     # Evento de clase eliminado

# ------------------ Eventos ----------------------------

# Lógica para manejar la creación o actualización de eventos
@receiver(post_save, sender=Event)
def on_event_created(sender, instance:Event, created:bool, course:Course = None, **kwargs):
    if created:
        if course:
            add_event_to_class(course, instance)
            send_advertisement_course(f"Nuevo evento de clase: {instance.title}", f"Se ha creado un nuevo evento para la clase {course.name}.", course)
            log_success(f"Evento de clase creado: {instance.title} para la clase {course.name}")
        else:
            add_event_to_calendar(instance.createdBy, instance)
            log_success(f"Evento creado: {instance.title} por {instance.createdBy.user.first_name}")
    else:
        if course:
            send_advertisement_course(f"Evento de clase actualizado: {instance.title}", f"Se ha actualizado el evento para la clase {course.name}.", course)
            log_success(f"Evento de clase actualizado: {instance.title} para la clase {course.name}")
        else:
            log_success(f"Evento actualizado: {instance.title} por {instance.createdBy.user.first_name}")

# Lógica para manejar la eliminación de eventos    
@receiver(post_delete, sender=Event)
def on_event_deleted(sender, instance:Event, course:Course, **kwargs):
    if course:
        send_advertisement_course(f"Evento de clase eliminado: {instance.title}", f"Se ha eliminado el evento para la clase {course.name}.", course)
        log_success(f"Evento de clase eliminado: {instance.title} para la clase {course.name}")
    else:
        log_success(f"Evento eliminado: {instance.title} por {instance.createdBy.user.first_name}")



# ------------------ Calendario ----------------------------
# Lógica para manejar la creación o actualización de Calendarios
@receiver(post_save, sender=Calendar)
def on_Calendar_created(sender, instance:Calendar, created, **kwargs):
    if created:
        log_success(f"Calendaro creado para {instance.user.first_name}")
    else:
        log_success(f"Calendaro actualizado para {instance.user.first_name}")

# Lógica para manejar la eliminación de Calendaros    
@receiver(post_delete, sender=Calendar)
def on_Calendar_deleted(sender, instance:Calendar, **kwargs):
    log_success(f"Calendaro eliminado para {instance.user.first_name}")


# ------------------ Asesorias ----------------------------
@receiver(advising_requested)
def on_advising_requested(sender, advising: Advising, **kwargs):
    pass

@receiver(advising_accepted)
def on_advising_accepted(sender, advising: Advising, **kwargs):
    pass

@receiver(advising_rejected)
def on_advising_rejected(sender, advising: Advising, **kwargs):
    pass


# # -----------------------------
# # Notificaciones
# # -----------------------------
# @receiver(post_save, sender=Notifications)
# def on_notification_created(sender, instance, created, **kwargs):
#     if created:
#         pass

# @receiver(notification_sent)
# def on_notification_sent(sender, notification, **kwargs):
#     pass

# @receiver(notification_read)
# def on_notification_read(sender, notification, **kwargs):
#     pass

# # -----------------------------
# # Usuarios
# # -----------------------------
# @receiver(user_logged_in)
# def on_user_logged_in(sender, request, user, **kwargs):
#     pass

# @receiver(user_logged_out)
# def on_user_logged_out(sender, request, user, **kwargs):
#     pass

# @receiver(user_registered)
# def on_user_registered(sender, user, **kwargs):
#     pass

# @receiver(user_profile_updated)
# def on_user_profile_updated(sender, user, **kwargs):
#     pass

# @receiver(user_password_changed)
# def on_user_password_changed(sender, user, **kwargs):
#     pass

# @receiver(user_role_changed)
# def on_user_role_changed(sender, user, **kwargs):
#     pass

# # -----------------------------
# # Sistema
# # -----------------------------
# @receiver(system_error)
# def on_system_error(sender, error, **kwargs):
#     pass

# # -----------------------------
# # Chat
# # -----------------------------
# @receiver(post_save, sender=Message)
# def on_new_chat_message(sender, instance, created, **kwargs):
#     if created:
#         pass

# @receiver(Signal())
# def on_chat_message_read(sender, message, **kwargs):
#     pass
