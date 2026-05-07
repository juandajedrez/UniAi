from Django.utils.logger import log_debug, log_error, log_info, log_success
log_debug("Cargando signals.py en app_calendar")

from django.dispatch import receiver, Signal
from django.db.models.signals import post_save, post_delete, pre_save, pre_delete, m2m_changed
from app_notifications.models import AdvertisementCourse, Notifications
from .models import *
from app_users.models import Profile

advising_requested = Signal()      # Solicitud de asesoría
advising_accepted = Signal()       # Aceptación de asesoría
advising_rejected = Signal()       # Rechazo de asesoría
join_event = Signal()              # Invitacion a un evento

# ------------------ Eventos ----------------------------

@receiver(m2m_changed, sender=Event.participants.through)
def on_event_participants_changed(sender, instance: Event, action, pk_set, **kwargs):
    if action == "post_add":
        # Notificar a los agregados
        for profile_id in pk_set:
            p = instance.participants.get(pk=profile_id)
            log_info(f"{p.user.first_name} ha sido agregado al evento {instance.title}")
            Notifications.objects.create(
                user=p.user,
                content=f"Has sido agregado al evento '{instance.title}'."
            )

    elif action == "post_remove":
        # Notificar a los eliminados
        for profile_id in pk_set:
            from app_users.models import Profile
            p = Profile.objects.get(pk=profile_id)
            log_info(f"{p.user.first_name} ha sido eliminado del evento {instance.title}")
            Notifications.objects.create(
                user=p.user,
                content=f"Has sido eliminado del evento '{instance.title}'."
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
                Notifications.objects.create(
                    user=p.user,
                    content=f"El evento '{instance.title}' ha sido actualizado."
                )


@receiver(post_save, sender=Event)
def on_event_created(sender, instance: Event, created: bool, **kwargs):
    course = kwargs.get("course", None)
    profile: Profile = kwargs.get("user", instance.createdBy)
    if created:
        if course:
            course.events.add(instance)
            AdvertisementCourse.objects.create(
                content=f"Nuevo evento de clase: {instance.title}",
                description=f"Se ha creado un nuevo evento para la clase {course.name}.",
                course=course
            )
            log_success(f"Evento de clase creado: {instance.title} para la clase {course.name}")
        else:
            log_success(f"Evento creado: {instance.title} por {profile.user.first_name}")
    else:
        if course:

            AdvertisementCourse.objects.create(
                content=f"Evento de clase actualizado: {instance.title}",
                description=f"Se ha actualizado el evento para la clase {course.name}.",
                course=course
            )
            log_success(f"Evento de clase actualizado: {instance.title} para la clase {course.name}")
        else:
            log_success(f"Evento actualizado: {instance.title} por {profile.user.first_name}")

@receiver(post_delete, sender=Event)
def on_event_deleted(sender, instance: Event, **kwargs):
    course = kwargs.get("course", None)
    user = kwargs.get("user", instance.createdBy.user)
    if course:
        AdvertisementCourse.objects.create(
            content=f"Evento de clase eliminado: {instance.title}",
            description=f"Se ha eliminado el evento para la clase {course.name}.",
            course=course
        )
        log_success(f"Evento de clase eliminado: {instance.title} para la clase {course.name}")
    else:
        for p in instance.participants.all():
                Notifications.objects.create(
                    user=p.user,
                    content=f"El evento {instance.title} se ha eliminado"
                )
        log_success(f"Evento eliminado: {instance.title} por {user.first_name}")
        

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