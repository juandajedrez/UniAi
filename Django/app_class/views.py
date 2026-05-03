from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Course
from app_users.models import Profile
from Django.utils.logger import log_debug
log_debug("Cargando views de app_class")

@login_required
def my_courses(request):
    profile = get_object_or_404(Profile, user=request.user)
    courses = Course.objects.filter(students=profile) | Course.objects.filter(teachers=profile)
    return render(request, "my_courses.html", {"courses": courses})


@login_required
def course_detail(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    return render(request, "course_detail.html", {"course": course})


@login_required
def course_participants(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    teachers = course.teachers.all()
    students = course.students.all()
    return render(request, "course_participants.html", {
        "course": course,
        "teachers": teachers,
        "students": students
    })
