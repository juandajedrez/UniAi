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
    photo = models.TextField(default="https://img.freepik.com/vector-premium/icono-usuario-establece-perfil-social-simbolo-vectorial-avatar-persona-cuenta-signo-web_268104-14523.jpg?semt=ais_hybrid&w=740&q=80")
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        verbose_name="Usuario"
    )
    birthday = models.DateField(
        null=True, 
        blank=True, 
        verbose_name="Fecha de nacimiento"
    )
    department = models.ForeignKey(
        "app_class.Department", 
        on_delete=models.PROTECT,
        verbose_name="Facultad"
    )
    program = models.ForeignKey(
        "app_class.Program", 
        on_delete=models.PROTECT,
        verbose_name="Programa"
    )
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES,
        verbose_name="Rol"
    )
    semester = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(15)], 
        null=True, 
        blank=True,
        verbose_name="Semestre"
    )

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfiles"

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    
class SocialMedia(models.Model):
    name = models.CharField(
        max_length=25, 
        blank=True, 
        null=True,
        verbose_name="Nombre de la red social"
    )
    link = models.URLField(
        blank=True, 
        null=True,
        verbose_name="Enlace"
    )
    profile = models.ForeignKey(
        Profile, 
        on_delete=models.PROTECT,
        verbose_name="Perfil asociado"
    )

    class Meta:
        verbose_name = "Red social"
        verbose_name_plural = "Redes sociales"

    def __str__(self):
        return f"{self.name or 'Sin nombre'}"


        





