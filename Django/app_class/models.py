from django.db import models
from app_users.models import Teacher,Student
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
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.teacher} dicta {self.course}"

class StudentCourse(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.student} inscrito en {self.course}"

class ClassroomCourse(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.course} en {self.classroom}"
