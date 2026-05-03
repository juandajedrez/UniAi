from Django.utils.logger import log_debug
log_debug("Cargando admin de app_notifications")

from django.contrib import admin
from .models import Notifications, Advertisement, AdvertisementCourse


# --- Admin para Notifications ---
@admin.register(Notifications)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "timestamp", "short_content")
    search_fields = ("user__username", "content")
    list_filter = ("status", "timestamp")

    def short_content(self, obj):
        return obj.content[:50] + ("..." if len(obj.content) > 50 else "")
    short_content.short_description = "Contenido"

# --- Admin para Advertisement ---
@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ("id", "community", "status", "timestamp", "short_content")
    search_fields = ("content",)
    list_filter = ("community", "status", "timestamp")

    def short_content(self, obj):
        return obj.content[:50] + ("..." if len(obj.content) > 50 else "")
    short_content.short_description = "Contenido"

# --- Admin para AdvertisementCourse ---
@admin.register(AdvertisementCourse)
class AdvertisementCourseAdmin(admin.ModelAdmin):
    list_display = ("id", "community", "status", "timestamp", "short_content")
    search_fields = ("content", "community__name")
    list_filter = ("status", "timestamp", "community")

    def short_content(self, obj):
        return obj.content[:50] + ("..." if len(obj.content) > 50 else "")
    short_content.short_description = "Contenido"
