from cProfile import Profile

from Django.utils.logger import log_debug
log_debug("Cargando apis de app_calendar")

from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import *
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden, JsonResponse
from Django.utils.scripts import log_debug, log, log_error, log_info, log_success
from app_notifications.models import Notifications
@login_required
def accept_advising(request, advising_id):
    adv = get_object_or_404(Advising, pk=advising_id)
    if request.user.profile != adv.advisor:
        log_error("permiso denegado",f"el usuario {request.user.first_name} no es el docente, y no puede aceptar asesorias")
        return HttpResponseForbidden("Solo el docente puede aceptar la asesoría.")
    adv.status = "SCHEDULED"
    log_info(f"El docente {request.user.first_name}, aceptó la asesoria: {adv.title}")
    return redirect("pending_advisings")

@login_required
def reject_advising(request, advising_id):
    adv: Advising = get_object_or_404(Advising, pk=advising_id)
    if request.user.profile != adv.advisor:
        log_error("permiso denegado",f"el usuario {request.user.first_name} no es el docente, y no puede rechazar asesorias")
        return HttpResponseForbidden("Solo el docente puede rechazar la asesoría.")
    adv.status = "CANCELLED"
    log_info(f"El docente {request.user.first_name}, rechazó la asesoria: {adv.title}")
    return redirect("pending_advisings")

@login_required
def reject_event(request, event_id):
    event: Event = get_object_or_404(Event, pk=event_id)
    profile: Profile = request.user.profile
    if profile in event.participants.all():
        log_info(f"el usuario {profile.user.first_name} rechazó la invitacion al evento {event.title}")
        event.participants.remove(profile)
        Notifications.objects.create(
            user=event.createdBy.user,
            message=f"El usuario {profile.user.first_name} ha rechazado la invitación al evento {event.title}"
        )
        return redirect("user_calendar")
    else:
        log_error("permiso denegado",f"el usuario {profile.user.first_name} no pertenece al evento {event.title}")
        return HttpResponseForbidden("No perteneces a este evento")
    

def remove_event (request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if request.user.profile != event.createdBy:
        log_error("permiso denegado",f"el usuario {request.user.first_name} no es el creador del evento {event.title}, y no puede eliminarlo")
        return HttpResponseForbidden("Solo el creador del evento puede eliminarlo.")
    log_info(f"el usuario {request.user.first_name} eliminó el evento {event.title}")
    event.delete()
    return redirect("user_calendar")



