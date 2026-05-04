from Django.utils.logger import log_debug
log_debug("Cargando apis de app_calendar")

from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import *
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from Django.utils.scripts import log_debug, log, log_error, log_info, log_success, add_participants_to_event
from Django.utils.signals import join_event

@login_required
def accept_advising(request, advising_id):
    if request.user.profile.role != "TEACHER":
        return HttpResponseForbidden("Solo los docentes pueden aceptar asesorías.")
    adv = get_object_or_404(Advising, pk=advising_id)
    adv.status = "SCHEDULED"
    return redirect("pending_advisings")

@login_required
def reject_advising(request, advising_id):
    if request.user.profile.role != "TEACHER":
        return HttpResponseForbidden("Solo los docentes pueden rechazar asesorías.")
    adv = get_object_or_404(Advising, pk=advising_id)
    adv.status = "CANCELLED"
    return redirect("pending_advisings")

