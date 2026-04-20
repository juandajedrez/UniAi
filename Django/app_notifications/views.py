from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Notifications

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