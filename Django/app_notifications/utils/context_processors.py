from ..models import Notifications
from Django.utils.logger import log_debug
log_debug("Cargando context processors de app_notifications")

def unread_notifications(request):
    if request.user.is_authenticated:
        count = Notifications.objects.filter(user=request.user, status="RECEIVED").count()
        return {"unread_count": count}
    return {"unread_count": 0}
