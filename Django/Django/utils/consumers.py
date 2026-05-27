from Django.utils.logger import log_debug
log_debug("Cargando consumers.py")

from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils.timezone import now
from asgiref.sync import sync_to_async
from app_users.models import Profile


class PresenceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if user.is_authenticated:
            profile = await sync_to_async(Profile.objects.get)(user=user)
            profile.last_activity = now()
            profile.is_online = True
            await sync_to_async(profile.save)(update_fields=["last_activity", "is_online"])
        await self.accept()

    async def disconnect(self, close_code):
        user = self.scope["user"]
        if user.is_authenticated:
            profile = await sync_to_async(Profile.objects.get)(user=user)
            profile.last_activity = now()
            profile.is_online = False
            await sync_to_async(profile.save)(update_fields=["last_activity", "is_online"])
