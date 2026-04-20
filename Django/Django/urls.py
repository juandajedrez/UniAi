from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
    path("admin/panel/", admin.site.urls),          # Panel de administración
    path("admin/", include("app_admin.urls")),          # Panel de administración
    path("users/", include("app_users.urls")),    # Rutas de la app users
    path("class/", include("app_class.urls")),  # Rutas de la app class
    path("chat/", include("app_chat.urls")),      # Rutas de la app chat
    path("calendar/", include("app_calendar.urls")),  # Rutas de la app calendar
    path("notifications/", include("app_notifications.urls")),  # Rutas de la app notifications

    path("home/", views.home_view, name="home"),
    path("", views.blank_view),
]
#handler404 = "Django.views.custom_page_not_found"

