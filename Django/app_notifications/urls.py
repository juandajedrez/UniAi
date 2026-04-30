from django.urls import path
from . import views

urlpatterns = [
    path("", views.notifications_list, name="notifications_list"),
    path("<int:pk>/", views.notification_detail, name="notification_detail"),
    path("course/<int:course_id>/ads/", views.course_ads, name="course_ads"),
    path("course/<int:course_id>/ads/new/", views.create_course_ad, name="create_course_ad"),
]
