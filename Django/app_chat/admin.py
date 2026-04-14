from django.contrib import admin
from .models import Chat, Message

# --- Admin para Chat ---
@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ("id", "state", "get_users", "description")
    search_fields = ("description", "users__username", "users__email")
    list_filter = ("state",)

    def get_users(self, obj):
        return ", ".join([u.username for u in obj.users.all()])
    get_users.short_description = "Usuarios"

# --- Admin para Message ---
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "chat", "sender", "timeStamp", "short_content")
    search_fields = ("sender__username", "content", "chat__description")
    list_filter = ("timeStamp", "sender")

    def short_content(self, obj):
        return obj.content[:50] + ("..." if len(obj.content) > 50 else "")
    short_content.short_description = "Contenido"
