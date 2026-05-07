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

