from django.db import models
from django.contrib.auth.models import User
from app_class.models import Course
# Create your models here.

# ==========================
# CALENDARIO Y EVENTOS
# ==========================
class Calendar(models.Model):
    timeZone = models.CharField(max_length=50)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Calendario de {self.user.username}"

class Event(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    startDateTime = models.DateTimeField()
    endDateTime = models.DateTimeField()
    location = models.CharField(max_length=100)
    recurrenceRule = models.CharField(max_length=100, blank=True, null=True)
    createdBy = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_events")
    participants = models.ManyToManyField(User, related_name="events")
    status = models.CharField(max_length=20, choices=[
        ("SCHEDULED", "Programado"),
        ("CANCELLED", "Cancelado"),
        ("COMPLETED", "Completado"),
    ], default="SCHEDULED")

    def __str__(self):
        return f"{self.title} ({self.startDateTime})"

class CalendarEvent(models.Model):
    calendar = models.ForeignKey(Calendar, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.event} en {self.calendar}"

class CourseEvent(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.event} para {self.course}"
