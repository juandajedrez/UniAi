from django.db import models
from django.contrib.auth.models import User

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
    icon = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    state = models.CharField(max_length=20, choices=State.choices, default=State.ACTIVE)

    class Meta:
        abstract = True

    def __str__(self):
        return f"Chat {self.id} - {self.state}"

class ChatAI(Chat):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"ChatAI {self.name} ({self.state})"

class ChatUser(Chat):
    users = models.ManyToManyField(User, related_name="user_chats")

    def __str__(self):
        return f"ChatUser con {self.users.count()} usuarios ({self.state})"

class MessageUser(models.Model):
    content = models.TextField()
    timeStamp = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Msg {self.id} by {self.sender}"

class MessageAI(models.Model):
    content = models.TextField()
    timeStamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AI Msg {self.id}"
