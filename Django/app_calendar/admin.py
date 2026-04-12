from django.contrib import admin
from .models import Calendar, Event, CalendarEvent, CourseEvent

@admin.register(Calendar)
class CalendarAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "timeZone")
    search_fields = ("user__username", "timeZone")

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "startDateTime", "endDateTime", "location", "status", "createdBy")
    search_fields = ("title", "description", "location", "createdBy__username")
    list_filter = ("status", "startDateTime", "endDateTime")
    filter_horizontal = ("participants",)  # interfaz más cómoda para seleccionar usuarios

@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = ("id", "calendar", "event")
    search_fields = ("calendar__user__username", "event__title")

@admin.register(CourseEvent)
class CourseEventAdmin(admin.ModelAdmin):
    list_display = ("id", "course", "event")
    search_fields = ("course__name", "event__title")
