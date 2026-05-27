"""
rag_service.py — RAG desde PostgreSQL con tus modelos Django
Consulta directamente Profile, Course, Event, Advising, Chat, Message, Notifications y DocumentoRAG.
"""

import logging
from django.conf import settings

from ..models import PublicInformation
from app_class.models import Course
from django.db.models import Q

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

    social_media = _get_social_media_context(profile)
    if social_media:
        secciones.append(social_media)

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
    avisos = _get_advertisement_context(profile)
    if avisos:
        secciones.append(avisos)
    
    avisos_courses = _get_courses_advertisement_context(profile)
    if avisos_courses:
        secciones.append(avisos_courses)

    # ── 7. Información pública ─────────────────
    pub = _get_public_context(query)
    if pub:
        secciones.append(pub)

    


    if not secciones:
        return "No se encontró información en la base de datos para este perfil."

    logger.info(f"RAG — {len(secciones)} secciones de contexto cargadas.")
    return "\n\n---\n\n".join(secciones)

def _get_advertisement_context(profile) -> str:
    """Ejemplo de sección adicional: avisos o anuncios institucionales."""
    from app_notifications.models import Advertisement
    ads = Advertisement.objects.filter(status="ACTIVE",community=profile.role)
    if not ads.exists():
        return "No se encontraron avisos relevantes."
    lineas = ["Avisos institucionales:"]
    for a in ads:
        lineas.append(f"anuncio: {a.content} — {a.community} ({a.timestamp.strftime('%d/%m %H:%M')})")
    return "\n".join(lineas)

def _get_courses_advertisement_context(profile) -> str:
    """Ejemplo de sección adicional: avisos o anuncios institucionales."""
    from app_notifications.models import AdvertisementCourse
    from django.db.models import Q
    # Cursos en los que el perfil participa (como estudiante o profesor)
    courses = Course.objects.filter(Q(students=profile) | Q(teachers=profile)).distinct()

    # Avisos de esos cursos, solo activos
    ads = AdvertisementCourse.objects.filter(community__in=courses, status="ACTIVE")
    if not ads.exists():
        return "No se encontraron avisos de cursos relevantes."
    lineas = ["Avisos de cursos:"]
    for a in ads:
        lineas.append(f"anuncio: {a.content} — {a.community} ({a.timestamp.strftime('%d/%m %H:%M')})")
    return "\n".join(lineas)

def _get_social_media_context(profile) -> str:
    """Redes sociales del usuario."""
    social_media = profile.socialmedia_set.all()
    if not social_media.exists():
        return "No se encontraron redes sociales asociadas."
    lineas = ["Redes sociales:"]
    for s in social_media:
        lineas.append(f"{s.get_platform_display()}: {s.url}")
    return "\n".join(lineas)

def _get_perfil_context(profile) -> str:
    """Perfil del usuario."""
    user = profile.user
    lineas = ["Perfil del usuario:"]
    lineas.append(f"Nombre: {user.get_full_name() or user.username}")
    lineas.append(f"Email: {user.email}")
    lineas.append(f"Username: {user.username}")
    lineas.append(f"Programa: {profile.program.name}")
    lineas.append(f"Facultad: {profile.department.name}")
    lineas.append(f"Rol: {profile.get_role_display()}")
    lineas.append(f"cumpleaños: {profile.birthday.strftime('%d/%m/%Y') if profile.birthday else 'No especificado'}")

    if profile.semester:
        lineas.append(f"Semestre: {profile.semester}")
    return "\n".join(lineas)


def _get_courses_context(profile) -> str:
    """Cursos asociados al perfil (como estudiante o profesor)."""
    from app_class.models import Course
    from django.db.models import Q

    cursos = Course.objects.filter(
        Q(teachers=profile) | Q(students=profile)
    ).distinct()

    if not cursos.exists():
        return "No se encontraron cursos asociados."

    lineas = ["Cursos:"]
    for c in cursos:
        # Información básica del curso
        lineas.append(f"{c.name} — {c.description[:80]}")

        # Profesores
        for t in c.teachers.all():
            lineas.append(f"  Profesor: {t.user.get_full_name()}")

        # Estudiantes (opcional: podrías omitir si no quieres listar todos)
        for s in c.students.all():
            lineas.append(f"  Estudiante: {s.user.get_full_name()}")

        # Eventos
        for e in c.events.all():
            lineas.append(f"  Evento: {e.title} el {e.startDateTime.strftime('%d/%m %H:%M')}")

        # Aulas
        for a in c.classrooms.all():
            lineas.append(f"  Aula: {a.roomNumber} en {a.location}")

    return "\n".join(lineas)


def _get_public_context(query: str) -> str:
    palabras = [p for p in query.lower().split() if len(p) > 3]
    if not palabras:
        return ""

    filtro = Q()
    for p in palabras[:4]:
        filtro |= Q(content__icontains=p)

    docs = PublicInformation.objects.filter(filtro, status="ACTIVE")[:5]

    if not docs.exists():
        return ""

    lineas = ["Información institucional relevante:"]
    for d in docs:
        lineas.append(f"{d.title}: {d.content[:400]}")

    return "\n\n".join(lineas)


def _get_events_context(profile) -> str:
    """Eventos del usuario."""
    from app_calendar.models import Event
    events_owned = Event.objects.filter(createdBy=profile)
    events_participated = Event.objects.filter(participants__in=[profile])
    if not events_participated.exists() or not events_owned.exists():
        return "No se encontraron eventos."
    lineas = ["Eventos "]
    for e in events_owned:
        lineas.append(f"{e.title} — tipo: {e.type} — Hora de inicio: {e.startDateTime.strftime('%d/%m %H:%M')} en {e.location} (organizador), creado por {e.createdBy.user.get_full_name()}")
    for e in events_participated:
        lineas.append(f"{e.title} — tipo: {e.type} — Hora de inicio: {e.startDateTime.strftime('%d/%m %H:%M')} en {e.location} (participante) creado por {e.createdBy.user.get_full_name()}")
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
        lineas.append(f"{n.timestamp.strftime('%d/%m %H:%M')} — {n.content} estado: {'Leída' if n.status == 'READ' else 'No leída'}")
    return "\n".join(lineas)




def _get_public_context(query: str) -> str:
    """Información institucional pública."""
    from app_ai.models import DocumentoRAG

        # ── Intento 1: búsqueda vectorial con embeddings ──────────
    try:
        resultado = _semantic_search(query)
        if resultado:
            return resultado
    except Exception as e:
        logger.warning(f"Búsqueda vectorial falló: {e}. Usando búsqueda por keywords.")

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


def _semantic_search(query: str, top_k: int = 4) -> str:
    """
    Búsqueda semántica en DocumentoRAG usando embeddings guardados en DB.
    Requiere que los documentos tengan embedding_json poblado.
    """
    import json
    import numpy as np
    from ..models import DocumentoRAG
    from sentence_transformers import SentenceTransformer

    # Cargar modelo (se cachea en memoria tras la primera carga)
    modelo = _get_embedding_model()
    if modelo is None:
        return ""

    query_embedding = modelo.encode([query], normalize_embeddings=True)[0]

    # Cargar todos los embeddings de la DB
    docs = DocumentoRAG.objects.exclude(embedding_json=None).only(
        "id", "texto", "embedding_json"
    )
    if not docs.exists():
        return ""

    scores = []
    for doc in docs:
        vec = np.array(doc.embedding_json, dtype="float32")
        score = float(np.dot(query_embedding, vec))
        scores.append((score, doc))

    # Ordenar por similitud descendente
    scores.sort(key=lambda x: x[0], reverse=True)
    top = [(s, d) for s, d in scores[:top_k] if s >= 0.15]

    if not top:
        return ""

    lineas = ["Información institucional:"]
    for _, doc in top:
        lineas.append(doc.texto[:400])

    logger.info(f"RAG semántico: {len(top)} fragmentos (score >= 0.15)")
    return "\n\n".join(lineas)


# Cache simple del modelo de embeddings en memoria
_embedding_model = None

def _get_embedding_model():
    """Carga el modelo de embeddings una sola vez y lo cachea."""
    global _embedding_model
    if _embedding_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _embedding_model = SentenceTransformer(
                "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
            )
            logger.info("Modelo de embeddings cargado correctamente.")
        except Exception as e:
            logger.error(f"No se pudo cargar el modelo de embeddings: {e}")
            return None
    return _embedding_model