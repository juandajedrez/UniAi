from django.db import models
from django.contrib.auth.models import User
from Django.utils.logger import log_debug
log_debug("Cargando modelos de app_chat")

# Create your models here.

# ==========================
# CHAT
# ==========================
class State(models.TextChoices):
    ACTIVE = "ACTIVE", "Activo"
    INACTIVE = "INACTIVE", "Inactivo"
    FINISHED = "FINISHED", "Finalizado"
    REPORT = "REPORT", "Reportado"

class Chat(models.Model):
    icon = models.TextField()
    name = models.TextField(default="Chat")
    description = models.TextField(blank=True, null=True)
    state = models.CharField(max_length=20, choices=State.choices, default=State.ACTIVE)
    users = models.ManyToManyField(User, related_name="user_chats")

    def __str__(self):
        return f"Chat {self.id} - {self.state}"


class Message(models.Model):
    content = models.TextField()
    timeStamp = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(User, on_delete=models.PROTECT)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Msg {self.id} by {self.sender}"
