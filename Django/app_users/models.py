from django.db import models
from django.contrib.auth.models import User

# ==========================
# USUARIOS
# ==========================


class Profile(models.Model):
    ROLE_CHOICES = [
        ("STUDENT", "Estudiante"),
        ("TEACHER", "Profesor"),
        ("ADMINISTRATIVE", "Administrativo"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="STUDENT")
    semester = models.PositiveIntegerField(blank=True, null=True)  # solo para estudiantes
    department = models.CharField(max_length=100, blank=True, null=True)  # para profesores/administrativos
    officeHours = models.CharField(max_length=100, blank=True, null=True)  # para profesores

    def __str__(self):
        return f"Perfil de {self.user.username} ({self.role})"


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    officeHours = models.CharField(max_length=100, blank=True, null=True)
    department = models.CharField(max_length=100)

    def __str__(self):
        return f"Profesor: {self.user.username}"

class Administrative(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)

    def __str__(self):
        return f"Administrativo: {self.user.username}"

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    semester = models.PositiveIntegerField()

    def __str__(self):
        return f"Estudiante: {self.user.username} - Semestre {self.semester}"



