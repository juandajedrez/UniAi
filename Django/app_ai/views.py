from django.shortcuts import render
from Django.utils.logger import log_debug
log_debug("Cargando views de app_ai")

# Create your views here.
"""
views.py — Vistas del agente Helper
Chat con streaming SSE (Server-Sent Events) + autenticación Django.
"""

import json
import uuid
import logging

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import StreamingHttpResponse, JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth import logout

from .resources.rag_service import build_context
from .resources.llm_service import get_response_stream
from .models import Estudiante, MensajeChat

logger = logging.getLogger("agente")


# ─────────────────────────────────────────────────────────────
#  PÁGINA PRINCIPAL
# ─────────────────────────────────────────────────────────────

# def index(request):
#     """Landing page — redirige al chat si está autenticado."""
#     if request.user.is_authenticated:
#         return redirect("chat")
#     return render(request, "agente/index.html")


# ─────────────────────────────────────────────────────────────
#  CHAT
# ─────────────────────────────────────────────────────────────

@login_required
def chat_view(request):
    """Renderiza la interfaz del chat."""
    estudiante = _get_estudiante(request.user)
    sesion_id  = request.session.get("chat_sesion_id") or str(uuid.uuid4())
    request.session["chat_sesion_id"] = sesion_id

    import json

    historial = MensajeChat.objects.filter(sesion_id=sesion_id).order_by("created_at")
    
    historial_json =[
        {"role": msg.rol, "content": msg.contenido}
        for msg in historial
    ]
    
    context = {
        "estudiante":    estudiante,
        "historial":     historial,
        "historial_json":historial_json,
        "sesion_id":     sesion_id,
        "maps_key":      _get_maps_key(),
        "ubicaciones":   _get_ubicaciones_dict(),   # dict, no string
    }
    return render(request, "Chat.html", context)


# ─────────────────────────────────────────────────────────────
#  ENDPOINT DE STREAMING SSE
# ─────────────────────────────────────────────────────────────

@login_required
@require_POST
def chat_stream(request):
    """
    Recibe el mensaje del usuario y devuelve la respuesta en streaming SSE.

    Request body (JSON):
        {
            "message":  "¿cuál es mi horario?",
            "history":  [{"role": "user", "content": "..."}, ...]
        }

    Response: text/event-stream con chunks de texto
    """
    try:
        body      = json.loads(request.body)
        message   = body.get("message", "").strip()
        history   = body.get("history", [])
        sesion_id = request.session.get("chat_sesion_id", str(uuid.uuid4()))
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({"error": "Solicitud inválida"}, status=400)

    if not message:
        return JsonResponse({"error": "Mensaje vacío"}, status=400)

    estudiante = _get_estudiante(request.user)

    # Guardar mensaje del usuario en DB
    MensajeChat.objects.create(
        estudiante = estudiante,
        rol        = "user",
        contenido  = message,
        sesion_id  = sesion_id,
    )

    # Construir contexto RAG desde PostgreSQL
    context = build_context(estudiante, message)

    def event_stream():
        """Generador SSE: cada chunk es un evento text/event-stream."""
        full_response = ""

        try:
            for chunk in get_response_stream(message, history, context):
                full_response += chunk
                # Formato SSE: "data: <texto>\n\n"
                payload = json.dumps({"chunk": chunk}, ensure_ascii=False)
                yield f"data: {payload}\n\n"

        except Exception as e:
            logger.error(f"Error en streaming: {e}")
            error_payload = json.dumps({"error": str(e)}, ensure_ascii=False)
            yield f"data: {error_payload}\n\n"
            return

        # Guardar respuesta completa del asistente en DB
        if full_response:
            MensajeChat.objects.create(
                estudiante = estudiante,
                rol        = "assistant",
                contenido  = full_response,
                sesion_id  = sesion_id,
            )

        # Señal de fin del stream
        yield "data: [DONE]\n\n"

    response = StreamingHttpResponse(
        event_stream(),
        content_type="text/event-stream",
    )
    response["Cache-Control"]  = "no-cache"
    response["X-Accel-Buffering"] = "no"   # importante para Nginx
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
        MensajeChat.objects.filter(sesion_id=sesion_id).delete()
    request.session["chat_sesion_id"] = str(uuid.uuid4())
    return JsonResponse({"ok": True})


# ─────────────────────────────────────────────────────────────
#  LOGOUT
# ─────────────────────────────────────────────────────────────

def logout_view(request):
    logout(request)
    return redirect("index")


# ─────────────────────────────────────────────────────────────
#  UTILIDADES PRIVADAS
# ─────────────────────────────────────────────────────────────

def _get_estudiante(user) -> "Estudiante | None":
    """
    Obtiene el perfil Estudiante del usuario autenticado.
    Fallback: en desarrollo, usa el primer Estudiante de la DB
    si el usuario no tiene uno vinculado todavía.
    """
    from django.conf import settings
 
    # Intento 1: relación directa OneToOneField
    try:
        return user.estudiante
    except Exception:
        pass
 
    # Intento 2: buscar por email
    try:
        return Estudiante.objects.get(user__email=user.email)
    except Exception:
        pass
 
    # Intento 3 (solo en DEBUG): usar el primer estudiante de la DB
    if getattr(settings, "DEBUG", False):
        est = Estudiante.objects.first()
        if est:
            import logging
            logging.getLogger("agente").warning(
                f"Usuario {user.username} sin Estudiante vinculado. "
                f"Usando {est} como fallback de desarrollo."
            )
            return est
 
    return None


def _get_maps_key() -> str:
    from django.conf import settings
    return getattr(settings, "GOOGLE_MAPS_KEY", "")


def _get_ubicaciones_dict() -> dict:
    """Retorna el diccionario de ubicaciones del campus para json_script."""
    return {
        "Dirección principal":
            {"lat": 4.55395252725635,  "lng": -75.66020315188669},
        "Facultad de Ciencias de la Salud":
            {"lat": 4.556355309239439, "lng": -75.65889335985999},
        "Facultad de Ciencias Agroindustriales":
            {"lat": 4.554573164589939, "lng": -75.66210285679566},
        "Biblioteca Central":
            {"lat": 4.556594508396184, "lng": -75.65907732533077},
        "Facultad de Ingeniería":
            {"lat": 4.5559207277588065,"lng": -75.65983370819697},
        "Edificio Administrativo":
            {"lat": 4.552868086801359, "lng": -75.65938488992852},
        "Vicerrectoría Académica":
            {"lat": 4.552856054947472, "lng": -75.65916025494606},
    }