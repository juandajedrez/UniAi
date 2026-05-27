from Django.utils.logger import log_debug, log_dic, log_error, log_success
log_debug("Cargando utils de app_calendar")

import calendar
from datetime import date, datetime, timedelta
from collections import defaultdict
from .models import *
from django.contrib.auth.models import User
from app_class.models import Course
from typing import List
# Definir un tipo con TypedDict para mayor claridad
from typing import TypedDict

class EventParam(TypedDict):
    id: int
    type: str
    title: str
    description: str
    startDateTime: datetime
    endDateTime: datetime
    status: str
    location: str
    createdBy: str
    advisor: str

def get_events_for_recurrence(
    user: User,
    start_date: datetime,
    end_date: datetime,
    query: str = "",
    type_filter: str = ""
) -> List[EventParam]:
    try:
        log_debug(f"Construyendo eventos recurrentes para {user.username} entre {start_date} y {end_date}")

        # Traer eventos recurrentes del usuario
        recurrences = Event_recurrence.objects.filter(createdBy=user.profile)
        log_debug(f"Se encontraron {recurrences.count()} eventos recurrentes iniciales")

        # Aplicar filtros
        if query:
            log_debug(f"Aplicando filtro de búsqueda en recurrentes: {query}")
            recurrences = recurrences.filter(title__icontains=query)
        if type_filter:
            log_debug(f"Aplicando filtro de tipo en recurrentes: {type_filter}")
            recurrences = recurrences.filter(type=type_filter)

        events_valid: List[EventParam] = []

        for recurrence in recurrences:
            log_debug(f"Expandiendo recurrencia '{recurrence.title}' con regla {recurrence.recurrenceRule}")
            base_event = {
                "id": recurrence.id,
                "type": recurrence.type,
                "title": recurrence.title,
                "description": recurrence.description,
                "status": recurrence.status,
                "location": recurrence.location,
                "createdBy": str(recurrence.createdBy),
                "advisor": str(getattr(recurrence, "advisor", "")),
            }

            current_start = recurrence.startDateTime
            current_end = recurrence.endDateTime

            # Expandir según la regla de recurrencia
            while current_start <= end_date:
                if current_start >= start_date:
                    events_valid.append({
                        **base_event,
                        "startDateTime": current_start,
                        "endDateTime": current_end,
                    })
                    log_debug(f"Evento expandido: {recurrence.title} en {current_start}")

                if recurrence.recurrenceRule == "DAILY":
                    current_start += timedelta(days=1)
                    current_end += timedelta(days=1)
                elif recurrence.recurrenceRule == "WEEKLY":
                    current_start += timedelta(weeks=1)
                    current_end += timedelta(weeks=1)
                elif recurrence.recurrenceRule == "MONTHLY":
                    # aproximación: sumar 30 días
                    current_start += timedelta(days=30)
                    current_end += timedelta(days=30)
                elif recurrence.recurrenceRule == "YEARLY":
                    # aproximación: sumar 365 días
                    current_start += timedelta(days=365)
                    current_end += timedelta(days=365)
                else:
                    log_error(f"Regla de recurrencia desconocida: {recurrence.recurrenceRule}", Exception("Regla inválida"))
                    break

        log_success(f"Eventos recurrentes construidos exitosamente: {len(events_valid)} generados")
        return events_valid

    except Exception as e:
        log_error("Error al construir eventos recurrentes", e)
        return []

def build_events_list(
    user: User,
    start_date: datetime,
    end_date: datetime,
    query: str = "",
    type_filter: str = ""
) -> List[EventParam]:
    try:
        log_debug(f"Construyendo lista de eventos para {user.username} entre {start_date} y {end_date}")

        # Todos los eventos (incluye asesorías porque Advising extiende de Event)
        events = Event.objects.filter(
            startDateTime__gte=start_date,
            startDateTime__lt=end_date,
            isRecurrent=False
        ).order_by("startDateTime")


        # Aplicar filtros globales
        if query:
            events = events.filter(title__icontains=query)
        if type_filter:
            events = events.filter(type=type_filter)

        # Lista de eventos por curso (como estudiante y como profesor)
        events_courses: List[List[Event]] = []

        for course in user.profile.courses_as_student.all():
            log_debug(f"Procesando eventos del curso (estudiante): {course.name}")
            qs = course.events.filter(
                startDateTime__gte=start_date,
                startDateTime__lt=end_date
            )
            if query:
                qs = qs.filter(title__icontains=query)
            if type_filter:
                qs = qs.filter(type=type_filter)
            events_courses.append(qs.order_by("startDateTime"))

        for course in user.profile.courses_as_teacher.all():
            log_debug(f"Procesando eventos del curso (profesor): {course.name}")
            qs = course.events.filter(
                startDateTime__gte=start_date,
                startDateTime__lt=end_date
            )
            if query:
                qs = qs.filter(title__icontains=query)
            if type_filter:
                qs = qs.filter(type=type_filter)
            events_courses.append(qs.order_by("startDateTime"))

        # Construir lista final
        event_list: List[EventParam] = []

        for e in events:
            event_list.append({
                "id": e.id,
                "type": e.type,
                "title": e.title,
                "description": e.description,
                "startDateTime": e.startDateTime,
                "endDateTime": e.endDateTime,
                "status": e.status,
                "location": e.location,
                "createdBy": e.createdBy,
            })

        for c in events_courses:
            for e in c:
                event_list.append({
                    "id": e.id,
                    "type": e.type,
                    "title": e.title,
                    "description": e.description,
                    "startDateTime": e.startDateTime,
                    "endDateTime": e.endDateTime,
                    "status": e.status,
                    "location": e.location,
                    "createdBy": e.createdBy,
                })

        # Eventos donde el usuario es participante
        events_as_participant = Event.objects.filter(
            participants=user.profile,
            startDateTime__gte=start_date,
            startDateTime__lt=end_date
        ).order_by("startDateTime")

        if query:
            events_as_participant = events_as_participant.filter(title__icontains=query)
        if type_filter:
            events_as_participant = events_as_participant.filter(type=type_filter)

        for e in events_as_participant:
            event_list.append({
                "id": e.id,
                "type": e.type,
                "title": e.title,
                "description": e.description,
                "startDateTime": e.startDateTime,
                "endDateTime": e.endDateTime,
                "status": e.status,
                "location": e.location,
                "createdBy": e.createdBy,
            })

        # Agregar eventos recurrentes expandidos en el rango
        log_debug("Expandiendo eventos recurrentes en el rango de fechas")
        event_list.extend(
            get_events_for_recurrence(
                user,
                start_date=start_date,
                end_date=end_date,
                query=query,
                type_filter=type_filter
            )
        )

        log_success(f"Lista de eventos construida exitosamente con {len(event_list)} elementos")
        print("Eventos finales", event_list)
        return event_list

    except Exception as e:
        log_error("Error al construir la lista de eventos", e)
        return []


# Vista mensual
def build_month_view(events: List[EventParam], year=None, month=None, first_weekday: str = "MONDAY"):
    log_debug(f"Construyendo vista mensual para {month}/{year} con primer día {first_weekday}")
    # Mapear string a número de weekday
    weekday_map = {"MONDAY": 0, "TUESDAY": 1, "WEDNESDAY": 2,
                   "THURSDAY": 3, "FRIDAY": 4, "SATURDAY": 5, "SUNDAY": 6}
    first_weekday_num = weekday_map.get(first_weekday.upper(), 0)

    cal = calendar.Calendar(firstweekday=first_weekday_num)

    # Agrupar eventos por día
    events_by_day = defaultdict(list)
    for e in events:
        day = e["startDateTime"].date()
        events_by_day[day].append(e)

    # Construir semanas
    weeks = []
    week = []
    for day in cal.itermonthdates(year, month):
        week.append({
            "date": day,
            "events": events_by_day.get(day, [])
        })
        if len(week) == 7:
            weeks.append(week)
            week = []

    log_success(f"Vista mensual construida con {len(weeks)} semanas")
    return weeks, month


# Vista semanal
def build_week_view(events: List[EventParam], start_date: date, end_date: date):
    log_debug(f"Construyendo vista semanal desde {start_date} hasta {end_date}")
    week_days = []

    # Agrupar eventos por día
    events_by_day = defaultdict(list)
    for e in events:
        day = e["startDateTime"].date()
        if start_date <= day <= end_date:  # filtro por rango
            events_by_day[day].append(e)

    # Construir los días de la semana dentro del rango
    current_day = start_date
    while current_day <= end_date:
        week_days.append({
            "date": current_day,
            "events": events_by_day.get(current_day, [])
        })
        current_day += timedelta(days=1)

    log_success(f"Vista semanal construida con {len(week_days)} días")
    return week_days


# Vista diaria
def build_day_view(events: List[EventParam], target_date: date):
    log_debug(f"Construyendo vista diaria para {target_date}")
    day_events = [e for e in events if e["startDateTime"].date() == target_date]
    log_success(f"Vista diaria construida con {len(day_events)} eventos")
    return target_date, day_events


# Vista anual
def build_year_view(events: List[EventParam], year: int):
    log_debug(f"Construyendo vista anual para {year}")
    months = []

    events_by_month = defaultdict(list)
    for e in events:
        if e["startDateTime"].year == year:
            events_by_month[e["startDateTime"].month].append(e)

    for m in range(1, 13):
        months.append({
            "name": calendar.month_name[m],
            "events": events_by_month.get(m, [])
        })

    log_success(f"Vista anual construida con {len(months)} meses")
    return months
