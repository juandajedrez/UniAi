from Django.utils.logger import log_debug
log_debug("Cargando utils de app_calendar")

import calendar
from datetime import date, datetime, timedelta
from collections import defaultdict


# Vista mensual
def build_month_view(events, year=None, month=None):
    today = date.today()
    year = year or today.year
    month = month or today.month

    cal = calendar.Calendar(firstweekday=0)  # lunes=0
    month_days = []

    events_by_day = defaultdict(list)
    for e in events:
        day = e.startDateTime.date()
        events_by_day[day].append(e)

    # Agrupar en semanas (listas de 7 días)
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
    return weeks, month



# Vista semanal
def build_week_view(events, ref_date=None):
    ref_date = ref_date or date.today()
    start_week = ref_date - timedelta(days=ref_date.weekday())  # lunes
    week_days = []

    events_by_day = defaultdict(list)
    for e in events:
        day = e.startDateTime.date()
        events_by_day[day].append(e)

    for i in range(7):
        day = start_week + timedelta(days=i)
        week_days.append({
            "date": day,
            "events": events_by_day.get(day, [])
        })
    return week_days

# Vista diaria
def build_day_view(events, ref_date=None):
    ref_date = ref_date or date.today()
    day_events = [e for e in events if e.startDateTime.date() == ref_date]
    return ref_date, day_events

# Vista anual
def build_year_view(events, year=None):
    today = date.today()
    year = year or today.year
    months = []

    events_by_month = defaultdict(list)
    for e in events:
        if e.startDateTime.year == year:
            events_by_month[e.startDateTime.month].append(e)

    for m in range(1, 13):
        months.append({
            "name": calendar.month_name[m],
            "events": events_by_month.get(m, [])
        })
    return months
