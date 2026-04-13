from django.contrib import admin
from .models import ChatAI, ChatUser, MessageUser, MessageAI

@admin.register(ChatAI)
class ChatAIAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "user", "state")
    search_fields = ("name", "user__username")
    list_filter = ("state",)

@admin.register(ChatUser)
class ChatUserAdmin(admin.ModelAdmin):
    list_display = ("id", "state", "get_users_count")
    search_fields = ("users__username",)
    list_filter = ("state",)

    def get_users_count(self, obj):
        return obj.users.count()
    get_users_count.short_description = "Número de usuarios"

@admin.register(MessageUser)
class MessageUserAdmin(admin.ModelAdmin):
    list_display = ("id", "sender", "content", "timeStamp")
    search_fields = ("sender__username", "content")
    list_filter = ("timeStamp",)

@admin.register(MessageAI)
class MessageAIAdmin(admin.ModelAdmin):
    list_display = ("id", "content", "timeStamp")
    search_fields = ("content",)
    list_filter = ("timeStamp",)
