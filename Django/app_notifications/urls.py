from Django.utils.logger import log_debug
log_debug("Cargando urls de app_notifications")

from django.urls import path
from . import views, apis

urlpatterns = [
    path("", views.notifications_list, name="notifications_list"),
    path("<int:pk>/", views.notification_detail, name="notification_detail"),
    path("course/<int:course_id>/ads/", views.course_ads, name="course_ads"),
    path("course/<int:course_id>/ads/new/", views.create_course_ad, name="create_course_ad"),
    path("has_new/", apis.has_new_notifications, name="has_new_notifications"),
    path("get/news/", apis.get_notifications, name="get_notifications"),
    path("read/all/", apis.read_all_notifications, name="read_all_notifications"),
    path("advertisements/", views.advertisement_list, name="advertisement_list"),
    path("advertisements/new/", views.create_advertisement, name="create_advertisement"),
]
