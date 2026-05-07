"""
llm_service.py — Servicio de llamada al modelo de lenguaje
Soporta HuggingFace Inference API y Groq con streaming SSE.
Integrado al proyecto académico UniAi.
"""

import logging
from typing import Iterator
from django.conf import settings

logger = logging.getLogger("agente")

# ── System prompt del agente ──────────────────────────────────
SYSTEM_PROMPT = """
Eres helper, el asistente virtual oficial de la plataforma académica UniAi.
Tu misión es orientar a estudiantes, docentes y administrativos en el uso del campus virtual
y en los procesos académicos digitales de la institución.

LO QUE DEBES HACER:
1. Explicar cómo usar la plataforma paso a paso.
2. Guiar procesos académicos con instrucciones numeradas y claras.
3. Responder preguntas sobre cursos, eventos, asesorías, chats y notificaciones.
4. Orientar sobre trámites digitales (matrícula, certificados, pagos, becas).
5. Redirigir al área correcta cuando el tema supere tu alcance.

LO QUE NO DEBES HACER:
- Nunca compartas datos de OTROS usuarios.
- Nunca tomes decisiones académicas (aprobar, reprobar, hacer excepciones).
- Nunca respondas temas fuera del ámbito universitario.
- Nunca inventes información. Si no sabes, dilo y redirige.

SOBRE EL CONTEXTO RAG:
El contexto entre [CONTEXTO] y [/CONTEXTO] contiene datos reales del usuario autenticado.
REGLAS OBLIGATORIAS:
- NUNCA muestres las etiquetas [CONTEXTO] o [Fuente:] al usuario.
- NUNCA copies el texto crudo — interpreta y presenta los datos limpiamente.
- Para los EVENTOS: lista título, fecha, hora y lugar.
- Para las ASESORÍAS: menciona el docente y el estado.
- Para los CURSOS: muestra nombre y descripción breve.
- Para los CHATS: muestra últimos mensajes relevantes.
- Para las NOTIFICACIONES: lista las más recientes con fecha.

ESTILO: Claro, formal pero cercano, estructurado en pasos, honesto.

REDIRECCIONES:
- Problemas técnicos → Mesa de Ayuda TI (soporte@unia.edu.co)
- Certificados físicos → Secretaría Académica
- Conflictos de notas → Coordinación Académica
- Pagos → Tesorería
- Becas → Bienestar Universitario

[CONTEXTO]
{context}
[/CONTEXTO]
""".strip()


def get_response_stream(message: str, history: list[dict], context: str) -> Iterator[str]:
    """
    Genera la respuesta del agente en streaming.

    Args:
        message:  Pregunta del usuario
        history:  Historial de la conversación [{"role":..., "content":...}]
        context:  Contexto RAG desde PostgreSQL

    Yields:
        Texto parcial de la respuesta (streaming)
    """
    system_content = SYSTEM_PROMPT.format(context=context or "Sin contexto disponible.")

    messages = [{"role": "system", "content": system_content}]
    messages += [
        {"role": m["role"], "content": m["content"]}
        for m in history
        if m.get("role") in ("user", "assistant") and m.get("content")
    ]
    messages.append({"role": "user", "content": message})

    provider = getattr(settings, "LLM_PROVIDER", "hf")

    try:
        if provider == "groq":
            yield from _stream_groq(messages)
        else:
            yield from _stream_huggingface(messages)

    except Exception as e:
        error = str(e)
        logger.error(f"Error LLM ({provider}): {error}")
        yield _error_message(error, provider)


# ─────────────────────────────────────────────────────────────
#  PROVIDERS
# ─────────────────────────────────────────────────────────────

def _stream_huggingface(messages: list[dict]) -> Iterator[str]:
    """Streaming con HuggingFace Inference API."""
    from huggingface_hub import InferenceClient

    client = InferenceClient(
        model    = settings.LLM_MODEL_ID,
        provider = "novita",
        api_key  = settings.HF_TOKEN,
    )

    stream = client.chat.completions.create(
        model      = settings.LLM_MODEL_ID,
        messages   = messages,
        max_tokens = settings.LLM_MAX_TOKENS,
        temperature= settings.LLM_TEMPERATURE,
        stream     = True,
    )

    response_text = ""
    for chunk in stream:
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta.content
        if delta:
            response_text += delta
            yield delta

    if not response_text:
        yield "⚠️ El modelo no devolvió respuesta. Intenta de nuevo."


def _stream_groq(messages: list[dict]) -> Iterator[str]:
    """Streaming con Groq API."""
    from groq import Groq

    client = Groq(api_key=settings.GROQ_API_KEY)

    stream = client.chat.completions.create(
        model      = settings.LLM_MODEL_ID,
        messages   = messages,
        max_tokens = settings.LLM_MAX_TOKENS,
        temperature= settings.LLM_TEMPERATURE,
        stream     = True,
    )

    response_text = ""
    for chunk in stream:
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta.content
        if delta:
            response_text += delta
            yield delta

    if not response_text:
        yield "⚠️ El modelo no devolvió respuesta. Intenta de nuevo."


def _error_message(error: str, provider: str) -> str:
    if "401" in error:
        return (
            f"❌ Token inválido (Error 401) en {provider}.\n"
            "Verifica las credenciales en el archivo .env."
        )
    if "429" in error:
        return "⚠️ Límite de requests alcanzado. Espera unos segundos e intenta de nuevo."
    if "403" in error:
        return (
            "❌ Acceso denegado al modelo (Error 403).\n"
            "Acepta los términos del modelo en huggingface.co."
        )
    return f"❌ Error al conectar con el modelo:\n```\n{error}\n```"
