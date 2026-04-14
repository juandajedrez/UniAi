from django.db import models
from django.contrib.auth.models import User
from app_class.models import Course
# Create your models here.

# ==========================
# CALENDARIO Y EVENTOS
# ==========================
class Event(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    startDateTime = models.DateTimeField()
    endDateTime = models.DateTimeField()
    location = models.CharField(max_length=100)
    recurrenceRule = models.CharField(max_length=100, blank=True, null=True)
    createdBy = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_events")
    status = models.CharField(max_length=20, choices=[
        ("SCHEDULED", "Programado"),
        ("CANCELLED", "Cancelado"),
        ("COMPLETED", "Completado"),
    ], default="SCHEDULED")

    def __str__(self):
        return f"{self.title} ({self.startDateTime})"


class Calendar(models.Model):
    timeZone = models.CharField(max_length=50)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    DAY = [
        ("SUNDAY", "Domingo"),
        ("MONDAY", "Lunes"),
        ("SATURDAY", "Sabado"),
    ]
    firstDay =  models.CharField(max_length=20, choices=DAY)
    events = models.ManyToManyField(Event, blank=True)

    def __str__(self):
        return f"Calendario de {self.user.username}"



