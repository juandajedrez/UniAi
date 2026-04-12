from django.contrib import admin
from .models import Notifications, UserNotification

@admin.register(Notifications)
class NotificationsAdmin(admin.ModelAdmin):
    list_display = ("id", "content", "timestamp", "status")
    search_fields = ("content", "status")
    list_filter = ("status", "timestamp")

@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "event", "notification")
    search_fields = ("user__username", "event__title", "notification__content")
    list_filter = ("notification__status",)
