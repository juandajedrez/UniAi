from .utils.scripts import log_debug
log_debug("Cargando vistas de Django")
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect


@login_required
def home_view(request):
    return render(request, "home.html")

def custom_page_not_found(request, exception):
    return render(request, "404.html", status=404)

@login_required
def blank_view(request):
    return redirect("home")

# views.py
from django.http import JsonResponse
from app_notifications.models import Notifications
from app_chat.models import Message

def unread_notifications_count(request):
    count = Notifications.objects.filter(user=request.user, status="RECEIVED").count()
    return JsonResponse({"count": count})

def unread_messages_count(request):
    count = Message.objects.filter(chat__users=request.user, read=False).exclude(sender=request.user).count()
    return JsonResponse({"count": count})
    