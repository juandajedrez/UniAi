from Django.utils.logger import log_debug
log_debug("Cargando views de app_chat")

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Chat, Message


# ==========================
# Lista de chats
# ==========================
@login_required
def chat_list(request):
    chats = Chat.objects.filter(users=request.user)

    # Precalcular mensajes no leídos por chat
    chats_data = []
    for chat in chats:
        unread_count = chat.message_set.filter(read=False).exclude(sender=request.user).count()
        chats_data.append({
            "chat": chat,
            "unread_count": unread_count
        })

    return render(request, "chat_list.html", {"chats_data": chats_data})



# ==========================
# Vista de chat con mensajes
# ==========================
@login_required
def chat_view(request, chat_id):
    chat = get_object_or_404(Chat, pk=chat_id, users=request.user)
    messages = Message.objects.filter(chat=chat).order_by("timeStamp")

    # Enviar nuevo mensaje
    if request.method == "POST":
        content = request.POST.get("content")
        if content:
            Message.objects.create(
                content=content,
                sender=request.user,
                chat=chat,
                read=False
            )
        return redirect("chat_view", chat_id=chat.id)

    # ✅ Marcar mensajes como leídos (los que no son del usuario actual)
    messages.filter(read=False).exclude(sender=request.user).update(read=True)

    return render(request, "chat_view.html", {
        "chat": chat,
        "messages": messages,
        "user": request.user
    })



# ==========================
# Detalle del chat
# ==========================
@login_required
def chat_detail(request, chat_id):
    chat = get_object_or_404(Chat, pk=chat_id, users=request.user)
    return render(request, "chat_detail.html", {"chat": chat})

