from django.db import models
from django.contrib.auth.models import User

# ==========================
# USUARIOS
# ==========================


class SocialMedia(models.Model):
    name = models.CharField(max_length=25)
    link = models.CharField(max_length=100)
    def __str__(self):
        return f"Nombre: {self.name}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,null=True, blank=True)
    birthday = models.DateField(
        verbose_name="Fecha de nacimiento",
        help_text="Ingrese la fecha en formato AAAA-MM-DD",null=True, blank=True
    )
    department = models.ForeignKey("app_class.Department", on_delete=models.PROTECT,null=True, blank=True)
    program = models.ForeignKey("app_class.Program", on_delete=models.PROTECT,null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.department} - {self.program})"
    
class SocialMediaProfile(models.Model):
    socialMedia = models.ForeignKey(SocialMedia, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    def __str__(self):
        return f"Red social: {self.socialMedia.name} - usuario: {self.profile.user.username}"
    
class Teacher(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE,null=True, blank=True)

    def __str__(self):
        return f"Profesor: {self.profile.user.username}"

class Administrative(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE,null=True, blank=True)

    def __str__(self):
        return f"Administrativo: {self.profile.user.username}"

class Student(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE,null=True, blank=True)
    semester = models.PositiveIntegerField()

    def __str__(self):
        return f"Estudiante: {self.profile.user.username} - Semestre {self.semester}"



