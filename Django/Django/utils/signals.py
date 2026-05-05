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
user_registered = Signal()         # Nuevo usuario registrado
user_profile_updated = Signal()    # Perfil de usuario actualizado
user_password_changed = Signal()   # Contraseña de usuario cambiada
user_role_changed = Signal()       # Rol de usuario cambiado
system_error = Signal()            # Error del sistema (para monitoreo)
advising_requested = Signal()      # Solicitud de asesoría
advising_accepted = Signal()       # Aceptación de asesoría
advising_rejected = Signal()       # Rechazo de asesoría
join_event = Signal()              # Invitacion a un evento

# ------------------ Login ----------------------------
@receiver(user_logged_in)
def on_user_logged_in(sender, request, user, **kwargs):
    log_info(f"Usuario {user.first_name} inició sesión desde {request.META.get('REMOTE_ADDR')}")

# ------------------ Logout ----------------------------
@receiver(user_logged_out)
def on_user_logged_out(sender, request, user, **kwargs):
    log_info(f"Usuario {user.first_name} cerró sesión desde {request.META.get('REMOTE_ADDR')}")

# ------------------ Eventos ----------------------------

@receiver(m2m_changed, sender=Event.participants.through)
def on_event_participants_changed(sender, instance: Event, action, pk_set, **kwargs):
    if action == "post_add":
        # Notificar a los agregados
        for profile_id in pk_set:
            p = instance.participants.get(pk=profile_id)
            log_info(f"{p.user.first_name} ha sido agregado al evento {instance.title}")
            send_notification(
                p.user,
                f"Has sido agregado al evento '{instance.title}'."
            )

    elif action == "post_remove":
        # Notificar a los eliminados
        for profile_id in pk_set:
            from app_users.models import Profile
            p = Profile.objects.get(pk=profile_id)
            log_info(f"{p.user.first_name} ha sido eliminado del evento {instance.title}")
            send_notification(
                p.user,
                f"Has sido eliminado del evento '{instance.title}'."
            )

@receiver(pre_save, sender=Event)
def before_event_updated(sender, instance: Event, **kwargs):
    # Solo si el evento ya existe (update, no create)
    if instance.pk:
        try:
            old_event = Event.objects.get(pk=instance.pk)
        except Event.DoesNotExist:
            return

        # Comparar atributos (excepto participants)
        fields_to_check = ["title", "description", "startDateTime", "endDateTime", "location", "status", "type"]

        changed = False
        for field in fields_to_check:
            old_value = getattr(old_event, field)
            new_value = getattr(instance, field)
            if old_value != new_value:
                changed = True
                break

        # Si hubo cambios en alguno de esos campos → notificar
        if changed:
            for p in instance.participants.all():
                log_info(f"Notificando al usuario {p.user.first_name}, sobre cambios en el evento {instance.title}")
                
                send_notification(
                    p.user,  # suponiendo que participants es Profile y necesitas el User
                    f"El evento '{instance.title}' ha sido actualizado."
                )


@receiver(post_save, sender=Event)
def on_event_created(sender, instance: Event, created: bool, **kwargs):
    course = kwargs.get("course", None)
    profile = kwargs.get("user", instance.createdBy)
    if created:
        if course:
            add_event_to_class(course, instance)
            send_advertisement_course(
                f"Nuevo evento de clase: {instance.title}",
                f"Se ha creado un nuevo evento para la clase {course.name}.",
                course
            )
            log_success(f"Evento de clase creado: {instance.title} para la clase {course.name}")
        else:
            add_event_to_calendar(profile.calendar, instance)
            log_success(f"Evento creado: {instance.title} por {profile.user.first_name}")
    else:
        if course:

            send_advertisement_course(
                f"Evento de clase actualizado: {instance.title}",
                f"Se ha actualizado el evento para la clase {course.name}.",
                course
            )
            log_success(f"Evento de clase actualizado: {instance.title} para la clase {course.name}")
        else:
            log_success(f"Evento actualizado: {instance.title} por {profile.user.first_name}")

@receiver(post_delete, sender=Event)
def on_event_deleted(sender, instance: Event, **kwargs):
    course = kwargs.get("course", None)
    user = kwargs.get("user", instance.createdBy.user)
    if course:
        send_advertisement_course(
            f"Evento de clase eliminado: {instance.title}",
            f"Se ha eliminado el evento para la clase {course.name}.",
            course
        )
        log_success(f"Evento de clase eliminado: {instance.title} para la clase {course.name}")
    else:
        for p in instance.participants.all():
                send_notification(
                    p,
                    f"El evento {instance.title} se ha eliminado"
            )
        log_success(f"Evento eliminado: {instance.title} por {user.first_name}")
        

# ------------------ Calendario ----------------------------
@receiver(post_save, sender=Calendar)
def on_calendar_created(sender, instance: Calendar, created, **kwargs):
    if created:
        log_success(f"Calendario creado para {instance.user.user.first_name}")
    else:
        log_success(f"Calendario actualizado para {instance.user.user.first_name}")

@receiver(post_delete, sender=Calendar)
def on_calendar_deleted(sender, instance: Calendar, **kwargs):
    log_success(f"Calendario eliminado para {instance.user.user.first_name}")

# ------------------ Asesorías ----------------------------
@receiver(post_save, sender=Advising)
def on_advising_create(sender, instance: Advising, created, **kwargs):
    if created:
        log_success(f"Asesoría: {instance.title} creada por {instance.createdBy.user.first_name} con el docente {instance.advisor.user.first_name}")
    else:
        log_success(f"Asesoría modificada: {instance.title} con el docente {instance.advisor.user.first_name}")

@receiver(post_delete, sender=Advising)
def on_advising_delete(sender, instance: Advising, **kwargs):
    log_success(f"Asesoría {instance.title} con el docente {instance.advisor.user.first_name} eliminada")

@receiver(advising_requested)
def on_advising_requested(sender, advising: Advising, **kwargs):
    log_debug(f"Asesoría solicitada: {advising.title}")

@receiver(advising_accepted)
def on_advising_accepted(sender, advising: Advising, **kwargs):
    log_debug(f"Asesoría aceptada: {advising.title}")

@receiver(advising_rejected)
def on_advising_rejected(sender, advising: Advising, **kwargs):
    log_debug(f"Asesoría rechazada: {advising.title}")

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
        send_notification(
            profile.user,
            f"Nuevo anuncio para {instance.get_community_display()}: {instance.content[:50]}..."
        )
    if instance.community == "GLOBAL":
        log_success(f"Anuncio global enviado a todos los usuarios: {instance.content[:50]}...")
        for profile in Profile.objects.all():
            send_notification(
                profile.user,
                f"Nuevo anuncio global: {instance.content[:50]}..."
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

# ------------------ Señales personalizadas ----------------------------
@receiver(notification_read)
def on_notification_read(sender, notification, **kwargs):
    log_success(f"Notificación {notification.id} marcada como leída por {notification.user.username}")

@receiver(user_registered)
def on_user_registered(sender, profile:Profile, **kwargs):
    Calendar.objects.create(user=profile, timeZone="UTC", firstDay="MONDAY")

    "Pendiente: Crear IA para el usuario"

    #Enviar notificacion para cambiar contraseña
    send_notification(
        content="Bienvenido a UniAI! Por favor, cambia tu contraseña para asegurar tu cuenta.",
        user=profile.user)
    #Enviar notificacion para completar perfil
    send_notification(
        content="Por favor, completa tu perfil para disfrutar de todas las funciones de UniAI.",
        user=profile.user)

    #Crear chat con sigo mismo para guardar mensajes importantes
    chat = Chat.objects.create(description=f"Chat de {profile.user.first_name}", status="RECEIVED")
    chat.users.add(profile.user)
    log_success(f"Nuevo usuario registrado: {profile.user.username} ({profile.user.email})")

@receiver(user_profile_updated)
def on_user_profile_updated(sender, profile, **kwargs):
    log_success(f"Perfil actualizado: {profile.user.username} ({profile.get_role_display()})")

@receiver(user_password_changed)
def on_user_password_changed(sender, user, **kwargs):
    log_success(f"Contraseña cambiada para el usuario: {user.username}")

@receiver(user_role_changed)
def on_user_role_changed(sender, profile, old_role, new_role, **kwargs):
    log_success(f"Rol cambiado para {profile.user.username}: {old_role} → {new_role}")

@receiver(system_error)
def on_system_error(sender, error_message, **kwargs):
    log_debug(f"Error del sistema detectado: {error_message}")
