from django.urls import path
from . import views

urlpatterns = [
    path("my-courses/", views.my_courses, name="my_courses"),
    path("course/<int:course_id>/", views.course_detail, name="course_detail"),
    path("course/<int:course_id>/participants/", views.course_participants, name="course_participants"),
]
