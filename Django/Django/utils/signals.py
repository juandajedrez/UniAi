"""
Archivo de señales para la aplicación Django. 
Aquí se definen las señales personalizadas 
y los receptores para manejar eventos específicos en la aplicación, 
como la creación de eventos, notificaciones, cambios en el perfil de usuario, entre otros.
"""

# Importaciones necesarias
from django.db.models.signals import post_save, post_delete, pre_save, pre_delete, m2m_changed
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver, Signal
from .scripts import *

log_debug("Cargando signals.py")

# -----------------------------
# Señales personalizadas
# -----------------------------
log_debug("Creando señales personalizadas")
notification_read = Signal()       # Notificación leída
system_error = Signal()            # Error del sistema (para monitoreo)





# ------------------ Chat ----------------------------
@receiver(post_save, sender=Message)
def on_new_message(sender, instance: Message, created, **kwargs):
    if created:
        log_success(f"Nuevo mensaje en chat {instance.chat.id} de {instance.sender.username}")


# ------------------ Classroom ----------------------------
@receiver(post_save, sender=Classroom)
def on_classroom_created(sender, instance: Classroom, created, **kwargs):
    if created:
        log_success(f"Aula creada: {instance.roomNumber} en {instance.location}")
    else:
        log_success(f"Aula actualizada: {instance.roomNumber} en {instance.location}")

@receiver(post_delete, sender=Classroom)
def on_classroom_deleted(sender, instance: Classroom, **kwargs):
    log_success(f"Aula eliminada: {instance.roomNumber} en {instance.location}")

# ------------------ Course ----------------------------
@receiver(post_save, sender=Course)
def on_course_created(sender, instance: Course, created, **kwargs):
    if created:
        log_success(f"Curso creado: {instance.name}")
    else:
        log_success(f"Curso actualizado: {instance.name}")

@receiver(post_delete, sender=Course)
def on_course_deleted(sender, instance: Course, **kwargs):
    log_success(f"Curso eliminado: {instance.name}")

# ------------------ Department ----------------------------
@receiver(post_save, sender=Department)
def on_department_created(sender, instance: Department, created, **kwargs):
    if created:
        log_success(f"Departamento creado: {instance.name} (Director: {instance.director.username})")
    else:
        log_success(f"Departamento actualizado: {instance.name} (Director: {instance.director.username})")

@receiver(post_delete, sender=Department)
def on_department_deleted(sender, instance: Department, **kwargs):
    log_success(f"Departamento eliminado: {instance.name} (Director: {instance.director.username})")

# ------------------ Program ----------------------------
@receiver(post_save, sender=Program)
def on_program_created(sender, instance: Program, created, **kwargs):
    if created:
        log_success(f"Programa creado: {instance.name} (Director: {instance.director.username})")
    else:
        log_success(f"Programa actualizado: {instance.name} (Director: {instance.director.username})")

@receiver(post_delete, sender=Program)
def on_program_deleted(sender, instance: Program, **kwargs):
    log_success(f"Programa eliminado: {instance.name} (Director: {instance.director.username})")

# ------------------ Notifications ----------------------------
@receiver(post_save, sender=Notifications)
def on_notification_created(sender, instance: Notifications, created, **kwargs):
    if created:
        log_success(f"Notificación creada para {instance.user.username} con estado {instance.status}")
    else:
        log_success(f"Notificación actualizada para {instance.user.username} con estado {instance.status}")

@receiver(post_delete, sender=Notifications)
def on_notification_deleted(sender, instance: Notifications, **kwargs):
    log_success(f"Notificación eliminada para {instance.user.username}")

# ------------------ Advertisement ----------------------------
@receiver(post_save, sender=Advertisement)
def on_advertisement_created(sender, instance: Advertisement, created, **kwargs):
    if created:
        log_success(f"Anuncio creado para comunidad {instance.community} con estado {instance.status}")
    else:
        log_success(f"Anuncio actualizado para comunidad {instance.community} con estado {instance.status}")
    for profile in Profile.objects.filter(role=instance.community) if instance.community != "GLOBAL" else Profile.objects.all():
        Notifications.objects.create(
            user=profile.user,
            content=f"Nuevo anuncio para {instance.get_community_display()}: {instance.content[:50]}..."
        )
    if instance.community == "GLOBAL":
        log_success(f"Anuncio global enviado a todos los usuarios: {instance.content[:50]}...")
        for profile in Profile.objects.all():
            Notifications.objects.create(
                user=profile.user,
                content=f"Nuevo anuncio global: {instance.content[:50]}..."
            )
@receiver(post_delete, sender=Advertisement)
def on_advertisement_deleted(sender, instance: Advertisement, **kwargs):
    log_success(f"Anuncio eliminado para comunidad {instance.community}")

# ------------------ AdvertisementCourse ----------------------------
@receiver(post_save, sender=AdvertisementCourse)
def on_advertisement_course_created(sender, instance: AdvertisementCourse, created, **kwargs):
    if created:
        log_success(f"Anuncio de curso creado en {instance.community.name} con estado {instance.status}")
    else:
        log_success(f"Anuncio de curso actualizado en {instance.community.name} con estado {instance.status}")

@receiver(post_delete, sender=AdvertisementCourse)
def on_advertisement_course_deleted(sender, instance: AdvertisementCourse, **kwargs):
    log_success(f"Anuncio de curso eliminado en {instance.community.name}")


# ------------------ Señales personalizadas ----------------------------
@receiver(notification_read)
def on_notification_read(sender, notification, **kwargs):
    log_success(f"Notificación {notification.id} marcada como leída por {notification.user.username}")


@receiver(system_error)
def on_system_error(sender, error_message, **kwargs):
    log_debug(f"Error del sistema detectado: {error_message}")
