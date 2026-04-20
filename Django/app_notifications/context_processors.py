from .models import Notifications

def unread_notifications(request):
    if request.user.is_authenticated:
        count = Notifications.objects.filter(user=request.user, status="RECEIVED").count()
        return {"unread_count": count}
    return {"unread_count": 0}
