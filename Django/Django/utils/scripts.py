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
import random
from django.core.mail import send_mail
from django.conf import settings

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
    user = User.objects.create(**user_params)
    user.set_password(password)
    user.save()
    semester = 1 if profile_params["role"] == "STUDENT" else None
    Profile.objects.create(user=user, **profile_params, semester=semester)
    return user

# Generar un código aleatorio de 6 dígitos
def generate_reset_code():
    return str(random.randint(100000, 999999))

# Enviar correo con el código
def send_reset_code(email:str, code:str):
    send_mail(
        subject="Código de recuperación de contraseña",
        message=f"Tu código de recuperación es: {code}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
    )

# Agrgar evento al calendario del usuario
def add_event_to_calendar(calendar:Calendar, event:Event):
    calendar.events.add(event)

# agregar evento a la clase 
def add_event_to_class(class_instance:Course, event:Event):
    class_instance.events.add(event)

# Enviar notificación al usuario
def send_notification(user:User, content:str):
    Notifications.objects.create(content=content, user=user)

# Enviar notificación al usuario
def send_advertisement_course(content:str, community:Course):
    AdvertisementCourse.objects.create(content=content, community=community)

# Enviar notificación al usuario
def send_advertisement(content:str, community:str):
    Advertisement.objects.create(content=content, community=community)

# Agregar participantes al evento
def add_participants_to_event(event:Event, profile:Profile):
    event.participants.add(profile)

# Eliminar participantes del avento
def remove_participants_from_event(event:Event, profile:Profile):
    event.participants.remove(profile)

