from Django.utils.logger import log_debug
log_debug("Cargando apis de app_notifications")

from django.urls import path
from .models import *
from Django.utils.logger import log_debug
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect

@login_required
def has_new_notifications(request):
    """
    Devuelve un bool indicando si hay notificaciones nuevas (estado SENT).
    """
    print("Hola")
    new_exists = Notifications.objects.filter(user=request.user, status="SENT").exists()
    print(Notifications.objects.filter(user=request.user, status="SENT"))
    return JsonResponse({"new": new_exists})

@login_required
def get_notifications(request):
    """
    Devuelve todas las notificaciones del usuario en JSON.
    Además, las que estaban en estado SENT se marcan como RECEIVED.
    """

    

    # Obtener todas las notificaciones ordenadas
    notifications = Notifications.objects.filter(user=request.user).order_by("-timestamp")
    data = [
        {
            "id": n.id,
            "content": n.content,
            "timestamp": n.timestamp.strftime("%Y-%m-%d %H:%M"),
            "status": n.status,
        }
        for n in notifications
    ]
    return JsonResponse({"notifications": data})

@login_required
def read_all_notifications(request):
    """
    Marca todas las notificaciones del usuario como LEÍDAS.
    """
    Notifications.objects.filter(user=request.user).update(status="READ")
    return redirect("notifications_list")