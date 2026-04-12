from django.db import models
from django.contrib.auth.models import User
from app_calendar.models import Event
# Create your models here.

# ==========================
# NOTIFICACIONES
# ==========================
class Notifications(models.Model):
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ("SENT", "Enviado"),
        ("RECEIVED", "Recibido"),
        ("READ", "Leído"),
    ], default="SENT")

    def __str__(self):
        return f"Notif {self.id} - {self.status}"

class UserNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True)
    notification = models.ForeignKey(Notifications, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user} -> {self.notification}"
