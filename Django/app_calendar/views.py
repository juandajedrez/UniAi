from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import *
from django.contrib.auth.models import User
from .forms import AdvisingRequestForm, EventForm
from django.http import HttpResponseForbidden
from .utils import build_month_view, build_week_view, build_day_view, build_year_view

@login_required
def user_calendar(request):
    view = request.GET.get("view", "agenda")  # vista por defecto agenda
    q = request.GET.get("q", "")
    type_filter = request.GET.get("type", "")

    events = Event.objects.filter(createdBy=request.user)
    if q:
        events = events.filter(title__icontains=q)
    if type_filter:
        events = events.filter(type=type_filter)

    # Preparar datos según vista
    context = {"view": view, "events": events}

    if view == "month":
        month_days, current_month = build_month_view(events)
        context["month_days"] = month_days
        context["current_month"] = current_month
    elif view == "week":
        context["week_days"] = build_week_view(events)
    elif view == "day":
        context["day_date"], context["day_events"] = build_day_view(events)
    elif view == "year":
        context["year_months"] = build_year_view(events)
        

    return render(request, "user_calendar.html", context)


@login_required
def user_advisings(request):
    advisings = Advising.objects.filter(createdBy=request.user).order_by("-startDateTime")
    return render(request, "user_advisings.html", {"advisings": advisings})

@login_required
def request_advising(request):
    if request.user.profile.role != "STUDENT":
        return HttpResponseForbidden("Solo los estudiantes pueden solicitar asesorías.")

    if request.method == "POST":
        form = AdvisingRequestForm(request.POST)
        if form.is_valid():
            advising = form.save(commit=False)
            advising.createdBy = request.user
            advising.title = f"Asesoría con {advising.advisor.username}"
            advising.type = "ADVISING"
            advising.status = "Pending"
            advising.isRecurrent = False
            advising.save()
            return redirect("user_advisings")
    else:
        form = AdvisingRequestForm(user=request.user)

    return render(request, "request_advising.html", {"form": form})

@login_required
def pending_advisings(request):
    if request.user.profile.role != "TEACHER":
        return HttpResponseForbidden("Solo los docentes pueden gestionar asesorías.")

    advisings = Advising.objects.filter(advisor=request.user, status="Pending").order_by("startDateTime")
    return render(request, "pending_advisings.html", {"advisings": advisings})

@login_required
def accept_advising(request, advising_id):
    if request.user.profile.role != "TEACHER":
        return HttpResponseForbidden("Solo los docentes pueden aceptar asesorías.")
    adv = get_object_or_404(Advising, pk=advising_id)
    adv.status = "SCHEDULED"
    adv.save()
    return redirect("pending_advisings")

@login_required
def reject_advising(request, advising_id):
    if request.user.profile.role != "TEACHER":
        return HttpResponseForbidden("Solo los docentes pueden rechazar asesorías.")
    adv = get_object_or_404(Advising, pk=advising_id)
    adv.status = "CANCELLED"
    adv.save()
    return redirect("pending_advisings")

@login_required
def create_event(request):
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.createdBy = request.user
            event.save()
            return redirect("user_calendar")
    else:
        form = EventForm()
    return render(request, "create_event.html", {"form": form})

@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, pk=event_id, createdBy=request.user)

    # Detectar tipo de objeto
    if isinstance(event, Advising):
        kind = "Asesoría"
        extra_fields = {
            "Asesor": event.advisor,
        }
    elif isinstance(event, Event_recurrence):
        kind = "Evento recurrente"
        extra_fields = {
            "Regla de recurrencia": event.recurrenceRule,
        }
    else:
        kind = "Evento"
        extra_fields = {}

    return render(
        request,
        "event_detail.html",
        {"event": event, "kind": kind, "extra_fields": extra_fields}
    )

