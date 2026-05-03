from django.db import models
from django.contrib.auth.models import User
from Django.utils.logger import log_debug
log_debug("Cargando modelos de app_class")

# Create your models here.

# ==========================
# CURSOS Y AULAS
# ==========================

class Classroom(models.Model):
    roomNumber = models.CharField(max_length=20)
    capacity = models.PositiveIntegerField()
    location = models.CharField(max_length=100)

    def __str__(self):
        return f"Aula {self.roomNumber} ({self.location})"

class Course(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    classrooms = models.ManyToManyField(Classroom, blank=True)
    teachers = models.ManyToManyField("app_users.Profile", related_name="courses_as_teacher", blank=True)
    students = models.ManyToManyField("app_users.Profile", related_name="courses_as_student", blank=True)
    events = models.ManyToManyField("app_calendar.Event", blank=True)
    
    def __str__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    director = models.OneToOneField(User, on_delete=models.PROTECT)
    def __str__(self):
        return f"{self.name}"


class Program(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    director = models.OneToOneField(User, on_delete=models.PROTECT)    
    def __str__(self):
        return f"{self.name}"