from django.db import models
from django.contrib.auth.models import User
# Create your models here.

# ==========================
# CURSOS Y AULAS
# ==========================
class Course(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name

class Classroom(models.Model):
    roomNumber = models.CharField(max_length=20)
    capacity = models.PositiveIntegerField()
    location = models.CharField(max_length=100)

    def __str__(self):
        return f"Aula {self.roomNumber} ({self.location})"

class TeacherCourse(models.Model):
    teacher = models.ForeignKey("app_users.Teacher", on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.teacher} dicta {self.course}"

class StudentCourse(models.Model):
    student = models.ForeignKey("app_users.Student", on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.student} inscrito en {self.course}"

class ClassroomCourse(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.course} en {self.classroom}"


class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    director = models.ForeignKey(User, on_delete=models.PROTECT)
    def __str__(self):
        return f"{self.name}"
    

class Program(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    director = models.ForeignKey(User, on_delete=models.PROTECT)    
    def __str__(self):
        return f"{self.name}"