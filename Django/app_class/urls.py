from django.urls import path
from . import views
from Django.utils.logger import log_debug

log_debug("Cargando urls de app_class")
urlpatterns = [
    path("my-courses/", views.my_courses, name="my_courses"),
    path("course/<int:course_id>/", views.course_detail, name="course_detail"),
    path("course/<int:course_id>/participants/", views.course_participants, name="course_participants"),
]
