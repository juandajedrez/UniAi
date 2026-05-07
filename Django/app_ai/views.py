
from Django.utils.logger import log_debug
log_debug("Cargando views de app_ai")

import json
import uuid
import logging
from django.shortcuts import get_object_or_404, render, redirect
from app_class.models import Department, Program
from django.contrib.auth.decorators import login_required
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth import logout
from django.contrib.auth.models import User
from app_ai.resources.rag_service import build_context
from app_ai.resources.llm_service import get_response_stream
from app_chat.models import Chat, Message
from app_users.models import Profile
from django.conf import settings
from sentence_transformers import SentenceTransformer

embedding_model = SentenceTransformer(settings.AI_EMBEDDING_MODEL)


logger = logging.getLogger("agente")


# ─────────────────────────────────────────────────────────────
#  CHAT
# ─────────────────────────────────────────────────────────────

@login_required
def chat_view(request):

    # Buscar o crear el chat
    helper_user, _ = User.objects.get_or_create(username="4511", defaults={"first_name": "Helper"})
    # Buscar si ya existe un chat entre el usuario actual y el otro
    chat = Chat.objects.filter(users=request.user).filter(users=helper_user).first()

    if not chat:
        # Crear nuevo chat 1 a 1
        chat = Chat.objects.create(
            description=f"Chat entre {request.user.first_name} y {helper_user.first_name}",
            state="active",  # ajusta según tu modelo
            icon="https://cdn-icons-png.flaticon.com/512/1384/1384055.png"  # ícono por defecto
        )
        chat.users.add(request.user, helper_user)

    chat.users.add(request.user)

    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        if content:
            Message.objects.create(
                content=content,
                sender=request.user,
                chat=chat,
                read=True,
            )
        return redirect("chat_view")  # redirige para limpiar el form y mostrar mensajes

    messages = Message.objects.filter(chat=chat).order_by("timeStamp")

    return render(request, "chat.html", {
        "messages": messages,
        "user": request.user,
        "maps_key":      _get_maps_key(),
        "ubicaciones":   _get_ubicaciones_dict(),
    })


def get_chat_messages(user):
    # Buscar el usuario Helper
    helper_user = User.objects.get(username="4511")

    # Buscar el chat donde están el user y Helper
    chat = Chat.objects.filter(users=user).filter(users=helper_user).first()

    if not chat:
        return []

    # Traer mensajes ordenados por timestamp
    return Message.objects.filter(chat=chat).order_by("timeStamp")

# ─────────────────────────────────────────────────────────────
#  ENDPOINT DE STREAMING SSE
# ─────────────────────────────────────────────────────────────

@login_required
@require_POST
def chat_stream(request):
    """
    Recibe el mensaje del usuario y devuelve la respuesta en streaming SSE.
    """
    try:
        body = json.loads(request.body)
        message = body.get("message", "").strip()
        history = body.get("history", [])
        sesion_id = request.session.get("chat_sesion_id", str(uuid.uuid4()))
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({"error": "Solicitud inválida"}, status=400)

    if not message:
        return JsonResponse({"error": "Mensaje vacío"}, status=400)

    profile = request.user.profile

    # Buscar o crear el chat
    helper_user, _ = User.objects.get_or_create(username="4511", defaults={"first_name": "Helper"})
    # Buscar si ya existe un chat entre el usuario actual y el otro
    chat = Chat.objects.filter(users=request.user).filter(users=helper_user).first()
    if not chat:
        # Crear nuevo chat 1 a 1
        chat = Chat.objects.create(
            description=f"Chat entre {request.user.first_name} y {helper_user.first_name}",
            state="active",  # ajusta según tu modelo
            icon="https://cdn-icons-png.flaticon.com/512/1384/1384055.png"  # ícono por defecto
        )
        chat.users.add(request.user, helper_user)

    # Guardar mensaje del usuario en DB
    Message.objects.create(
        content=message,
        sender=request.user,
        chat=chat,
        read=True,
    )

    # Construir contexto RAG
    context = build_context(profile, message)

    def event_stream():
        """Generador SSE: cada chunk es un evento text/event-stream."""
        full_response = ""

        try:
            for chunk in get_response_stream(message, history, context):
                full_response += chunk
                payload = json.dumps({"chunk": chunk}, ensure_ascii=False)
                yield f"data: {payload}\n\n"

        except Exception as e:
            logger.error(f"Error en streaming: {e}")
            error_payload = json.dumps({"error": str(e)}, ensure_ascii=False)
            yield f"data: {error_payload}\n\n"
            return

        # Guardar respuesta completa del asistente en DB con sender=Helper
        if full_response:
            Message.objects.create(
                content=full_response,
                sender=helper_user,   # ✅ ahora sí un usuario válido
                chat=chat,
                read=True,
            )

        yield "data: [DONE]\n\n"

    response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response



# ─────────────────────────────────────────────────────────────
#  LIMPIAR HISTORIAL
# ─────────────────────────────────────────────────────────────

@login_required
@require_POST
def limpiar_chat(request):
    """Elimina el historial de la sesión actual."""
    sesion_id = request.session.get("chat_sesion_id")
    if sesion_id:
        Chat.objects.filter(name=f"Chat-{sesion_id}").delete()
    request.session["chat_sesion_id"] = str(uuid.uuid4())
    return JsonResponse({"ok": True})


# ─────────────────────────────────────────────────────────────
#  UTILIDADES PRIVADAS
# ─────────────────────────────────────────────────────────────

def _get_maps_key() -> str:
    from django.conf import settings
    return getattr(settings, "GOOGLE_MAPS_KEY", "")


def _get_ubicaciones_dict() -> dict:
    """Diccionario de ubicaciones del campus para json_script."""
    return {
        "Dirección principal": {"lat": 4.55395252725635, "lng": -75.66020315188669},
        "Facultad de Ciencias de la Salud": {"lat": 4.556355309239439, "lng": -75.65889335985999},
        "Facultad de Ciencias Agroindustriales": {"lat": 4.554573164589939, "lng": -75.66210285679566},
        "Biblioteca Central": {"lat": 4.556594508396184, "lng": -75.65907732533077},
        "Facultad de Ingeniería": {"lat": 4.5559207277588065, "lng": -75.65983370819697},
        "Edificio Administrativo": {"lat": 4.552868086801359, "lng": -75.65938488992852},
        "Vicerrectoría Académica": {"lat": 4.552856054947472, "lng": -75.65916025494606},
    }
