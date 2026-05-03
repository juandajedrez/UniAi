from .logger import log, log_error, log_debug, log_warning, log_info, log_success, title
log_debug("Cargando scripts.py")

#Funciones python para automatizar tareas en el proyecto Django
from app_calendar.models import *
from app_users.models import *
from django.contrib.auth.models import User
from app_chat.models import *
from app_notifications.models import *
from app_class.models import *
from app_ai.models import *
from app_admin.models import *
from app_notifications.models import *


# Diccionario de params para crear un usuario:
profile_params = {
    "role": str,  # "TEACHER", "ADMIN", "STUDENT", "IA"
    "birthday": "YYYY-MM-DD",  # Fecha de nacimiento
    "department": Department,  # Instancia de Department
    "program": Program,  # Instancia de Program
}
user_params = {
    "username": str,
    "first_name": str,
    "last_name": str,
    "email": str,
}

def create_user(user_params:dict, profile_params:dict):
    #Creamos los parametros por defecto para el usuario
    password = user_params["username"] # Contraseña por defecto (puede ser cambiada por el usuario)

    # Creamos el usuario y las instancias relacionadas
    user = User.objects.create(**user_params, password=password)
    semester = 1 if profile_params["role"] == "STUDENT" else None
    profile = Profile.objects.create(user=user, **profile_params, semester=semester)
    calendar = Calendar.objects.create(user=profile, timeZone="UTC", firstDay="MONDAY")

    "Pendiente: Crear IA para el usuario"

    #Enviar notificacion para cambiar contraseña
    notification = Notifications.objects.create(
        content="Bienvenido a UniAI! Por favor, cambia tu contraseña para asegurar tu cuenta.",
        user=user)
    #Enviar notificacion para completar perfil
    notification = Notifications.objects.create(
        content="Por favor, completa tu perfil para disfrutar de todas las funciones de UniAI.",
        user=user)

    #Crear chat con sigo mismo para guardar mensajes importantes
    chat = Chat.objects.create(description=f"Chat de {user.first_name}", status="RECEIVED")
    chat.users.add(user)

    # Guardar todos los objetos creados
    user.save()
    chat.save()
    calendar.save()
    profile.save()
    notification.save()

    return user



import random
from django.core.mail import send_mail
from django.conf import settings

# Generar un código aleatorio de 6 dígitos
def generate_reset_code():
    return str(random.randint(100000, 999999))

# Enviar correo con el código
def send_reset_code(email, code):
    send_mail(
        subject="Código de recuperación de contraseña",
        message=f"Tu código de recuperación es: {code}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
    )

# Agrgar evento al calendario del usuario
def add_event_to_calendar(profile, event):
    calendar = profile.calendar
    calendar.events.add(event)

# agregar evento a la clase 
def add_event_to_class(class_instance, event):
    class_instance.events.add(event)

# Enviar notificación al usuario
def send_notification(user, content):
    Notifications.objects.create(content=content, user=user)

# Enviar notificación al usuario
def send_advertisement_course(content:str, community:Course):
    AdvertisementCourse.objects.create(content=content, community=community)

# Enviar notificación al usuario
def send_advertisement(content:str, community:str):
    Advertisement.objects.create(content=content, community=community)

