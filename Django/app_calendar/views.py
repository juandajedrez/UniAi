# Importar funciones de log para depuración, éxito y errores
from Django.utils.logger import log_debug, log_success, log_error
log_debug("Cargando views de app_calendar")  # Debug: verificar carga del módulo

# Importaciones de Django y módulos propios
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import *
from django.contrib.auth.models import User
from .forms import AdvisingRequestForm, EventForm
from django.http import HttpResponseForbidden
from .utils import EventParam, build_events_list, build_month_view, build_week_view, build_day_view, build_year_view
from datetime import timedelta, date, datetime
from django.utils import timezone

@login_required
def user_calendar(request):
    view = request.GET.get("view", "agenda")
    query = request.GET.get("q", "")
    type_filter = request.GET.get("type", "")

    log_debug(f"Entrando a user_calendar con vista={view}, query={query}, type_filter={type_filter}")

    # Rango de fechas
    start_date_str = request.GET.get("start_date")
    end_date_str = request.GET.get("end_date")

    if start_date_str and end_date_str:
        start_date = timezone.make_aware(datetime.fromisoformat(start_date_str))
        # convertir end_date_str y ponerlo al final del día
        end_date_raw = datetime.fromisoformat(end_date_str)
        end_date = timezone.make_aware(
            end_date_raw.replace(hour=23, minute=59, second=59, microsecond=999999)
        )
        log_debug(f"Usando rango de fechas desde parámetros: {start_date} a {end_date}")

    else:
        today = timezone.now()
        start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if today.month == 12:
            end_date = today.replace(year=today.year+1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0) - timedelta(seconds=1)
        else:
            end_date = today.replace(month=today.month+1, day=1, hour=0, minute=0, second=0, microsecond=0) - timedelta(seconds=1)
        log_debug(f"Usando rango de fechas por defecto: {start_date} a {end_date}")


    events_list = build_events_list(
        request.user,
        start_date=start_date,
        end_date=end_date,
        query=query,
        type_filter=type_filter
    )
    log_success(f"Lista de eventos construida con {len(events_list)} elementos")

    context = {
        "view": view,
        "query": query,
        "type_filter": type_filter,
        "today": timezone.now().date(),
    }

    # Navegación según vista
    if view == "month":
        log_debug("Construyendo vista mensual")
        month_days, current_month = build_month_view(events_list, year=start_date.year, month=start_date.month)
        context["month_days"] = month_days
        context["current_month"] = current_month

        # prev/next mes
        prev_month_end = start_date - timedelta(days=1)
        prev_month_start = prev_month_end.replace(day=1)
        next_month_start = end_date + timedelta(days=1)
        next_month_end = (next_month_start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

        context.update({
            "start_date": start_date,
            "end_date": end_date,
            "prev_month_start": prev_month_start,
            "prev_month_end": prev_month_end,
            "next_month_start": next_month_start,
            "next_month_end": next_month_end,
        })
        log_success("Vista mensual construida correctamente")

    elif view == "week":
        log_debug("Construyendo vista semanal")
        week_days = build_week_view(events_list, start_date.date(), end_date.date())
        context["week_days"] = week_days

        prev_week_start = start_date.date() - timedelta(days=7)
        prev_week_end = end_date.date() - timedelta(days=7)
        next_week_start = start_date.date() + timedelta(days=7)
        next_week_end = end_date.date() + timedelta(days=7)

        today_date = timezone.now().date()
        today_week_start = today_date - timedelta(days=today_date.weekday())
        today_week_end = today_week_start + timedelta(days=6)

        context.update({
            "prev_week_start": prev_week_start,
            "prev_week_end": prev_week_end,
            "next_week_start": next_week_start,
            "next_week_end": next_week_end,
            "today_week_start": today_week_start,
            "today_week_end": today_week_end,
        })
        log_success("Vista semanal construida correctamente")


    elif view == "day":
        log_debug("Construyendo vista diaria")
        target_date_str = request.GET.get("target_date")
        if target_date_str:
            target_date = datetime.fromisoformat(target_date_str).date()
        else:
            target_date = date.today()
        context["day_date"], context["day_events"] = build_day_view(events_list, target_date)

        # prev/next día
        prev_day = target_date - timedelta(days=1)
        next_day = target_date + timedelta(days=1)

        context.update({
            "prev_day": prev_day,
            "next_day": next_day,
        })
        log_success("Vista diaria construida correctamente")

    elif view == "year":
        log_debug("Construyendo vista anual")
        year_str = request.GET.get("year")
        year = int(year_str) if year_str else datetime.today().year
        context["year_months"] = build_year_view(events_list, year)

        # prev/next año
        prev_year = year - 1
        next_year = year + 1

        context.update({
            "prev_year": prev_year,
            "next_year": next_year,
        })
        log_success("Vista anual construida correctamente")

    else:
        log_debug("Construyendo vista agenda")
        context["agenda_events"] = sorted(events_list, key=lambda e: e["startDateTime"])
        log_success("Vista agenda construida correctamente")

    return render(request, "user_calendar.html", context)




@login_required
def user_advisings(request):
    # Listar asesorías creadas por el usuario
    advisings = Advising.objects.filter(createdBy=request.user.profile).order_by("-startDateTime")
    log_success("Lista de asesorías del usuario cargada correctamente")
    return render(request, "user_advisings.html", {"advisings": advisings})


@login_required
def request_advising(request):
    # Validar que solo estudiantes puedan solicitar asesorías
    if request.user.profile.role != "STUDENT":
        log_error("Intento de solicitud de asesoría por usuario no estudiante", Exception("Rol inválido"))
        return HttpResponseForbidden("Solo los estudiantes pueden solicitar asesorías.")

    if request.method == "POST":
        form = AdvisingRequestForm(request.POST)
        if form.is_valid():
            # Crear asesoría pendiente
            advising = form.save(commit=False)
            advising.createdBy = request.user.profile
            advising.title = f"Asesoría con {advising.advisor.user.first_name}"
            advising.type = "ADVISING"
            advising.status = "Pending"
            advising.isRecurrent = False
            advising.save()
            log_success("Asesoría solicitada exitosamente")
            return redirect("user_advisings")
    else:
        form = AdvisingRequestForm(user=request.user)

    return render(request, "request_advising.html", {"form": form})


@login_required
def pending_advisings(request):
    # Validar que solo docentes puedan gestionar asesorías
    if request.user.profile.role != "TEACHER":
        log_error("Intento de acceso a asesorías pendientes por usuario no docente", Exception("Rol inválido"))
        return HttpResponseForbidden("Solo los docentes pueden gestionar asesorías.")

    advisings = Advising.objects.filter(advisor=request.user.profile, status="Pending").order_by("startDateTime")
    log_success("Lista de asesorías pendientes cargada correctamente")
    return render(request, "pending_advisings.html", {"advisings": advisings})


@login_required
def create_event(request):
    # Crear evento nuevo
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.createdBy = request.user.profile
            event.save()
            log_success("Evento creado exitosamente")
            return redirect("user_calendar")
    else:
        form = EventForm()
    return render(request, "create_event.html", {"form": form})


@login_required
def edit_event(request, event_id):
    # Editar evento existente
    event = get_object_or_404(Event, pk=event_id, createdBy=request.user.profile)
    if request.method == "POST":
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            log_success("Evento actualizado con éxito")
            return redirect("user_calendar")
    else:
        form = EventForm(instance=event)
    return render(request, "edit_event.html", {"form": form})


@login_required
def event_detail(request, event_id):
    # Ver detalle de un evento
    event = get_object_or_404(Event, pk=event_id)

    # Detectar tipo de evento
    if isinstance(event, Advising):
        kind = "Asesoría"
        extra_fields = {"Asesor": event.advisor}
    elif isinstance(event, Event_recurrence):
        kind = "Evento recurrente"
        extra_fields = {"Regla de recurrencia": event.recurrenceRule}
    else:
        kind = "Evento"
        extra_fields = {}

    # Validar permisos de acceso
    is_creator = (event.createdBy == request.user.profile)
    is_participant = (request.user.profile in event.participants.all())

    if not (is_creator or is_participant):
        log_error(f"Usuario {request.user.username} intentó acceder sin permiso al evento {event_id}", Exception("Acceso denegado"))
        return HttpResponseForbidden("No tienes permiso para ver este evento.")

    log_success(f"Detalle del evento {event_id} cargado correctamente")
    return render(
        request,
        "event_detail.html",
        {"event": event, "kind": kind, "extra_fields": extra_fields, "is_creator": is_creator, "is_participant": is_participant}
    )
