from Django.utils.logger import log_debug
log_debug("Cargando modelos de app_notifications")

from django.db import models
from django.contrib.auth.models import User


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
    ], default="RECEIVED")
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Notif {self.id} - {self.user.username} - {self.status}"

class Advertisement(models.Model):
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    ROLE_CHOICES = [
        ("TEACHER", "Profesor"),
        ("ADMIN", "Administrativo"),
        ("STUDENT", "Estudiante"),
        ("GLOBAL", "Global")
    ]
    community = models.CharField(max_length=20, choices=ROLE_CHOICES, default="GLOBAL")
    status = models.CharField(max_length=20, choices=[
        ("ACTIVE", "Activo"),
        ("INACTIVE", "Inactivo"),
    ], default="ACTIVE")

    def __str__(self):
        return f"Ad {self.id} - {self.community} - {self.status}"
    

class AdvertisementCourse(models.Model):
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    community = models.ForeignKey("app_class.Course", on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ("ACTIVE", "Activo"),
        ("INACTIVE", "Inactivo"),
    ], default="ACTIVE")

    def __str__(self):
        return f"Ad {self.id} - {self.community} - {self.status}"
