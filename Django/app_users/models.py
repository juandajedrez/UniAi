from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
# ==========================
# USERS
# ==========================

class Profile(models.Model):
    ROLE_CHOICES = [
        ("TEACHER", "Profesor"),
        ("ADMIN", "Administrativo"),
        ("STUDENT", "Estudiante"),
        ("IA","IA"),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birthday = models.DateField(null=True, blank=True)
    department = models.ForeignKey("app_class.Department", on_delete=models.PROTECT)
    program = models.ForeignKey("app_class.Program", on_delete=models.PROTECT)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    semester = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(15)], null=True, blank=True)  # solo usado si es estudiante

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    
class SocialMedia(models.Model):
    name = models.CharField(max_length=25)
    link = models.URLField()
    profile = models.ForeignKey(Profile, on_delete=models.PROTECT)
    def __str__(self):
        return f"Nombre: {self.name}"
        




