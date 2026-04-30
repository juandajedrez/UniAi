from django.contrib import admin
from .models import Event, Advising, Event_recurrence, Calendar

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "startDateTime", "endDateTime", "location", "type", "status", "createdBy")
    list_filter = ("type", "status", "createdBy")
    search_fields = ("title", "description", "location")
    ordering = ("startDateTime",)
    date_hierarchy = "startDateTime"

@admin.register(Advising)
class AdvisingAdmin(admin.ModelAdmin):
    list_display = ("title", "advisor", "startDateTime", "endDateTime", "location", "createdBy")
    list_filter = ("status", "advisor")
    search_fields = ("title", "description", "advisor__username")
    ordering = ("startDateTime",)
    date_hierarchy = "startDateTime"

@admin.register(Event_recurrence)
class EventRecurrenceAdmin(admin.ModelAdmin):
    list_display = ("title", "recurrenceRule", "startDateTime", "endDateTime", "createdBy")
    list_filter = ("recurrenceRule", "createdBy")
    search_fields = ("title", "description")
    ordering = ("startDateTime",)
    date_hierarchy = "startDateTime"

@admin.register(Calendar)
class CalendarAdmin(admin.ModelAdmin):
    list_display = ("user", "timeZone", "firstDay")
    search_fields = ("user__username", "timeZone")
    filter_horizontal = ("events", "event_recurrence", "advisings")
