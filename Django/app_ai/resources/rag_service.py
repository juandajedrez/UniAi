"""
consulta directamente los modelos Django con el ORM.
"""

import logging
from django.conf import settings

logger = logging.getLogger("agente")

# ── Palabras clave por tipo de consulta ───────────────────────

KEYWORDS_HORARIO = [
    "horario", "salon", "salón", "aula", "clase", "clases",
    "donde tengo", "dónde tengo", "cuándo tengo", "cuando tengo",
    "qué días", "que dias", "dicta", "se dicta",
]

KEYWORDS_NOTAS = [
    "nota", "notas", "calificacion", "calificación", "definitiva",
    "promedio", "perdí", "perdi", "aprobé", "aprobe",
    "reprobé", "reprobe", "corte", "cuanto saque", "cuánto saqué",
]

KEYWORDS_DOCENTES = [
    "docente", "profesor", "profesora", "quien dicta", "quién dicta",
    "quien da", "quién da", "quien enseña", "quién enseña",
    "nombre del profe", "profe de", "maestro",
]

KEYWORDS_UBICACION = [
    "donde", "dónde", "ubicación", "ubicacion", "dirección", "direccion",
    "como llego", "cómo llego", "queda", "mapa", "lugar", "sitio",
]


def build_context(estudiante, query: str) -> str:
    """
    Construye el contexto para el sistema RAG consultando PostgreSQL.
    Detecta el tipo de consulta y devuelve el texto relevante.

    Args:
        estudiante: instancia de Estudiante (o None si no está autenticado)
        query: pregunta del usuario

    Returns:
        String con el contexto a inyectar en el system prompt
    """
    query_lower = query.lower()
    contextos: list[str] = []

    # ── Datos personales del estudiante ──────────────────────
    if estudiante:

        # Horario
        if any(k in query_lower for k in KEYWORDS_HORARIO):
            ctx = _get_horario_context(estudiante, query_lower)
            if ctx:
                contextos.append(ctx)

        # Notas
        if any(k in query_lower for k in KEYWORDS_NOTAS):
            ctx = _get_notas_context(estudiante)
            if ctx:
                contextos.append(ctx)

        # Docentes
        if any(k in query_lower for k in KEYWORDS_DOCENTES):
            ctx = _get_docentes_context(estudiante)
            if ctx:
                contextos.append(ctx)

    # ── Información pública institucional (búsqueda semántica) ─
    if not contextos or any(k in query_lower for k in ["matrícula", "matricula", "certificado", "reglamento", "faq"]):
        ctx = _get_public_context(query)
        if ctx:
            contextos.append(ctx)

    if not contextos:
        return "No se encontró información específica para esta consulta."

    return "\n\n---\n\n".join(contextos)


# ─────────────────────────────────────────────────────────────
#  CONSULTAS POR TIPO
# ─────────────────────────────────────────────────────────────

def _get_horario_context(estudiante, query_lower: str) -> str:
    """Retorna el horario del estudiante desde la DB."""
    from ..models import Horario

    # Si pregunta por una materia específica, filtrar
    horarios = Horario.objects.filter(estudiante=estudiante)

    # Detectar si pregunta por un día específico
    dias_map = {
        "lunes": "Lunes", "martes": "Martes", "miércoles": "Miércoles",
        "miercoles": "Miércoles", "jueves": "Jueves",
        "viernes": "Viernes", "sábado": "Sábado", "sabado": "Sábado",
    }
    for kw, dia in dias_map.items():
        if kw in query_lower:
            horarios = horarios.filter(dia=dia)
            break

    if not horarios.exists():
        return "No se encontraron clases registradas en el horario."

    lineas = ["Horario académico:"]
    for h in horarios:
        lineas.append(h.as_context_text())

    logger.info(f"RAG horario: {horarios.count()} registros")
    return "\n".join(lineas)


def _get_notas_context(estudiante) -> str:
    """Retorna todas las notas del estudiante desde la DB."""
    from ..models import Nota

    notas = Nota.objects.filter(estudiante=estudiante)

    if not notas.exists():
        return "No se encontraron notas registradas."

    lineas = ["Notas del período actual:"]
    for n in notas:
        lineas.append(n.as_context_text())

    logger.info(f"RAG notas: {notas.count()} materias")
    return "\n".join(lineas)


def _get_docentes_context(estudiante) -> str:
    """Retorna los docentes de las materias del estudiante."""
    from ..models import Docente, Horario

    # Obtener los códigos de las materias del estudiante
    codigos = Horario.objects.filter(
        estudiante=estudiante
    ).values_list("codigo", flat=True).distinct()

    docentes = Docente.objects.filter(codigo__in=codigos)

    if not docentes.exists():
        return "No se encontró información de docentes."

    lineas = ["Docentes de tus materias:"]
    for d in docentes:
        lineas.append(d.as_context_text())

    logger.info(f"RAG docentes: {docentes.count()} registros")
    return "\n".join(lineas)


def _get_public_context(query: str) -> str:
    """
    Búsqueda semántica en DocumentoRAG (información pública).
    Usa similitud de embeddings si están disponibles,
    o búsqueda por palabras clave como fallback.
    """
    from ..models import DocumentoRAG

    # ── Intento 1: búsqueda vectorial con embeddings ──────────
    try:
        resultado = _semantic_search(query)
        if resultado:
            return resultado
    except Exception as e:
        logger.warning(f"Búsqueda vectorial falló: {e}. Usando búsqueda por keywords.")

    # ── Intento 2: búsqueda por palabras clave (fallback) ─────
    palabras = [p for p in query.lower().split() if len(p) > 3]
    if not palabras:
        return ""

    from django.db.models import Q
    filtro = Q()
    for p in palabras[:4]:     # máximo 4 palabras para no saturar
        filtro |= Q(texto__icontains=p)

    docs = DocumentoRAG.objects.filter(filtro)[:5]

    if not docs.exists():
        return ""

    lineas = ["Información institucional relevante:"]
    for d in docs:
        lineas.append(d.texto[:400])     # máximo 400 chars por fragmento

    logger.info(f"RAG público (keywords): {docs.count()} fragmentos")
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