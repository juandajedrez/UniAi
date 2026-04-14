from django.contrib import admin
from .models import Event, Calendar

# --- Admin para Event ---
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "startDateTime", "endDateTime", "location", "status", "createdBy")
    search_fields = ("title", "description", "location", "createdBy__username")
    list_filter = ("status", "location", "startDateTime", "endDateTime")

# --- Admin para Calendar ---
@admin.register(Calendar)
class CalendarAdmin(admin.ModelAdmin):
    list_display = ("user", "timeZone", "firstDay", "get_events")
    search_fields = ("user__username", "timeZone")
    list_filter = ("timeZone", "firstDay")

    def get_events(self, obj):
        return ", ".join([e.title for e in obj.events.all()])
    get_events.short_description = "Eventos"
