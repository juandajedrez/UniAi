from django.db import models
from django.contrib.auth.models import User
# Create your models here.

# ==========================
# CALENDARIO Y EVENTOS
# ==========================
class Event(models.Model):
    title = models.CharField("Título", max_length=100)
    description = models.TextField("Descripción")
    startDateTime = models.DateTimeField("Fecha y hora de inicio")
    endDateTime = models.DateTimeField("Fecha y hora de fin")
    location = models.CharField("Ubicación", max_length=100)
    isRecurrent = models.BooleanField("¿Es recurrente?", default=False)

    createdBy = models.ForeignKey(
        "app_users.Profile",
        on_delete=models.CASCADE,
        related_name="created_events",
        verbose_name="Creado por"
    )

    status = models.CharField(
        "Estado",
        max_length=20,
        choices=[
            ("SCHEDULED", "Programado"),
            ("CANCELLED", "Cancelado"),
            ("ONGOING", "En curso"),
            ("COMPLETED", "Completado"),
            ("PENDING", "Pendiente"),
        ],
        default="SCHEDULED"
    )

    type = models.CharField(
        "Tipo de evento",
        max_length=20,
        choices=[
            ("CLASS", "Clase"),
            ("EXAM", "Examen"),
            ("MEETING", "Reunión"),
            ("ADVISING", "Asesoría"),
            ("OTHER", "Otro")
        ],
        default="OTHER"
    )

    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"

    def __str__(self):
        return f"{self.title} ({self.startDateTime})"


class Advising(Event):
    advisor = models.ForeignKey(
        "app_users.Profile",
        on_delete=models.CASCADE,
        related_name="advisor_events",
        verbose_name="Asesor"
    )

    class Meta:
        verbose_name = "Asesoría"
        verbose_name_plural = "Asesorías"

    def __str__(self):
        return f"Asesoría: {self.title} - Asesor: {self.advisor}"


class Event_recurrence(Event):
    recurrenceRule = models.CharField(
        "Regla de recurrencia",
        max_length=100,
        choices=[
            ("DAILY", "Diaria"),
            ("WEEKLY", "Semanal"),
            ("MONTHLY", "Mensual"),
            ("YEARLY", "Anual"),
        ],
        default="DAILY"
    )

    class Meta:
        verbose_name = "Evento recurrente"
        verbose_name_plural = "Eventos recurrentes"

    def __str__(self):
        return f"Repetición de {self.title}"


class Calendar(models.Model):
    timeZone = models.CharField("Zona horaria", max_length=50)
    user = models.OneToOneField("app_users.Profile", on_delete=models.CASCADE, verbose_name="Usuario")

    DAY = [
        ("SUNDAY", "Domingo"),
        ("MONDAY", "Lunes"),
        ("SATURDAY", "Sábado"),
    ]
    firstDay = models.CharField("Primer día de la semana", max_length=20, choices=DAY)

    events = models.ManyToManyField(Event, blank=True, related_name="calendar_events", verbose_name="Eventos")
    event_recurrence = models.ManyToManyField(Event_recurrence, blank=True, related_name="calendar_recurrences", verbose_name="Eventos recurrentes")
    advisings = models.ManyToManyField(Advising, blank=True, related_name="calendar_advisings", verbose_name="Asesorías")

    class Meta:
        verbose_name = "Calendario"
        verbose_name_plural = "Calendarios"

    def __str__(self):
        return f"Calendario de {self.user.username}"




