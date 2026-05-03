from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Notifications, AdvertisementCourse
from django.http import HttpResponseForbidden
from app_class.models import Course
from app_users.models import Profile
from .forms import AdvertisementCourseForm
from Django.utils.logger import log_debug
log_debug("Cargando views de app_notifications")

# Lista de notificaciones del usuario
@login_required
def notifications_list(request):
    notifications = Notifications.objects.filter(user=request.user).order_by("-timestamp")
    return render(request, "notifications_list.html", {"notifications": notifications})

# Detalle de una notificación
@login_required
def notification_detail(request, pk):
    notification = get_object_or_404(Notifications, pk=pk, user=request.user)

    # Si está en estado RECEIVED, lo marcamos como READ al abrir
    if notification.status == "RECEIVED":
        notification.status = "READ"
        notification.save()

    return render(request, "notification_detail.html", {"notification": notification})

def unread_notifications(request):
    if request.user.is_authenticated:
        count = Notifications.objects.filter(user=request.user, status="RECEIVED").count()
        return {"unread_count": count}
    return {"unread_count": 0}



# Ver anuncios del curso
@login_required
def course_ads(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    ads = AdvertisementCourse.objects.filter(community=course, status="ACTIVE").order_by("-timestamp")
    return render(request, "course_ads.html", {"course": course, "ads": ads})

# Redactar anuncio del curso (solo docentes)
@login_required
def create_course_ad(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    profile = get_object_or_404(Profile, user=request.user)

    # Solo docentes del curso pueden crear anuncios
    if profile not in course.teachers.all():
        return HttpResponseForbidden("No tienes permisos para crear anuncios en este curso.")

    if request.method == "POST":
        form = AdvertisementCourseForm(request.POST)
        if form.is_valid():
            ad = form.save(commit=False)
            ad.community = course
            ad.save()
            return redirect("course_ads", course_id=course.id)
    else:
        form = AdvertisementCourseForm()

    return render(request, "create_course_ad.html", {"course": course, "form": form})
