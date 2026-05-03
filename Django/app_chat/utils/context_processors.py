from Django.utils.logger import log_debug
log_debug("Cargando context processors de app_chat")

from ..models import Message


def unread_messages(request):
    if request.user.is_authenticated:
        count = Message.objects.filter(chat__users=request.user, read=False).exclude(sender=request.user).count()
        return {"unread_messages_count": count}
    return {}
