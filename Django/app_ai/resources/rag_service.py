"""
rag_service.py — RAG desde PostgreSQL con tus modelos Django
Consulta directamente Profile, Course, Event, Advising, Chat, Message, Notifications y DocumentoRAG.
"""

import logging
from django.conf import settings

logger = logging.getLogger("agente")

def build_context(profile, query: str) -> str:
    """
    Construye el contexto completo del usuario desde la base de datos.
    Incluye: perfil, cursos, eventos, asesorías, chats, mensajes y notificaciones.
    """
    if not profile:
        logger.warning("RAG — Sin perfil vinculado. Solo información pública.")
        return _get_public_context(query) or "Contexto institucional no disponible."

    logger.info(f"RAG — Cargando datos completos de: {profile}")

    secciones: list[str] = []

    # ── 1. Perfil ──────────────────────────────
    perfil = _get_perfil_context(profile)
    if perfil:
        secciones.append(perfil)

    # ── 2. Cursos ──────────────────────────────
    cursos = _get_courses_context(profile)
    if cursos:
        secciones.append(cursos)

    # ── 3. Eventos ─────────────────────────────
    eventos = _get_events_context(profile)
    if eventos:
        secciones.append(eventos)

    # ── 4. Asesorías ───────────────────────────
    advisings = _get_advisings_context(profile)
    if advisings:
        secciones.append(advisings)

    # ── 5. Chats y mensajes ────────────────────
    chats = _get_chats_context(profile.user)
    if chats:
        secciones.append(chats)

    # ── 6. Notificaciones ──────────────────────
    notifs = _get_notifications_context(profile.user)
    if notifs:
        secciones.append(notifs)

    # ── 7. Información pública ─────────────────
    pub = _get_public_context(query)
    if pub:
        secciones.append(pub)

    if not secciones:
        return "No se encontró información en la base de datos para este perfil."

    logger.info(f"RAG — {len(secciones)} secciones de contexto cargadas.")
    return "\n\n---\n\n".join(secciones)


def _get_perfil_context(profile) -> str:
    """Perfil del usuario."""
    user = profile.user
    lineas = ["Perfil del usuario:"]
    lineas.append(f"Nombre: {user.get_full_name() or user.username}")
    lineas.append(f"Programa: {profile.program.name}")
    lineas.append(f"Facultad: {profile.department.name}")
    lineas.append(f"Rol: {profile.get_role_display()}")
    if profile.semester:
        lineas.append(f"Semestre: {profile.semester}")
    return "\n".join(lineas)


def _get_courses_context(profile) -> str:
    """Cursos del usuario."""
    from app_class.models import Course
    cursos = profile.courses_as_student.all() | profile.courses_as_teacher.all()
    if not cursos.exists():
        return "No se encontraron cursos asociados."
    lineas = ["Cursos:"]
    for c in cursos:
        lineas.append(f"{c.name} — {c.description[:80]}...")
    return "\n".join(lineas)


def _get_events_context(profile) -> str:
    """Eventos del usuario."""
    from app_calendar.models import Event
    events = Event.objects.filter(participants=profile)
    if not events.exists():
        return "No se encontraron eventos."
    lineas = ["Eventos:"]
    for e in events:
        lineas.append(f"{e.title} — {e.startDateTime.strftime('%d/%m %H:%M')} en {e.location}")
    return "\n".join(lineas)


def _get_advisings_context(profile) -> str:
    """Asesorías del usuario."""
    from app_calendar.models import Advising
    advisings = Advising.objects.filter(createdBy=profile)
    if not advisings.exists():
        return "No se encontraron asesorías."
    lineas = ["Asesorías:"]
    for a in advisings:
        lineas.append(f"{a.title} con {a.advisor.user.get_full_name()} — {a.startDateTime.strftime('%d/%m %H:%M')}")
    return "\n".join(lineas)


def _get_chats_context(user) -> str:
    """Chats y mensajes del usuario."""
    from app_chat.models import Chat, Message
    chats = Chat.objects.filter(users=user)
    if not chats.exists():
        return "No se encontraron chats."
    lineas = ["Chats:"]
    for c in chats:
        lineas.append(f"{c.name} — {c.description or 'Sin descripción'}")
        msgs = Message.objects.filter(chat=c).order_by("-timeStamp")[:3]
        for m in msgs:
            lineas.append(f"  {m.sender.username}: {m.content[:60]}...")
    return "\n".join(lineas)


def _get_notifications_context(user) -> str:
    """Notificaciones del usuario."""
    from app_notifications.models import Notifications
    notifs = Notifications.objects.filter(user=user).order_by("-timestamp")[:5]
    if not notifs.exists():
        return "No se encontraron notificaciones."
    lineas = ["Notificaciones recientes:"]
    for n in notifs:
        lineas.append(f"{n.timestamp.strftime('%d/%m %H:%M')} — {n.content}")
    return "\n".join(lineas)


def _get_public_context(query: str) -> str:
    """Información institucional pública."""
    from app_ai.models import DocumentoRAG
    from django.db.models import Q
    palabras = [p for p in query.lower().split() if len(p) > 3]
    if not palabras:
        return ""
    filtro = Q()
    for p in palabras[:4]:
        filtro |= Q(texto__icontains=p)
    docs = DocumentoRAG.objects.filter(filtro)[:5]
    if not docs.exists():
        return ""
    lineas = ["Información institucional relevante:"]
    for d in docs:
        lineas.append(d.texto[:400])
    return "\n\n".join(lineas)
