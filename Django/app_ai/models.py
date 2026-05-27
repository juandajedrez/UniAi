from django.db import models
from Django.utils.logger import log_debug
log_debug("Cargando modelos de app_ai")

# Create your models here.

from django.db import models
from django.contrib.auth.models import User



class DocumentoRAG(models.Model):
    """
    Fragmentos de información pública institucional indexados para búsqueda semántica.
    Reemplaza el índice FAISS de informacion_publica.txt.
    """
    FUENTES = [
        ("web",         "Página web institucional"),
        ("reglamento",  "Reglamento estudiantil"),
        ("faq",         "Preguntas frecuentes"),
        ("otro",        "Otro"),
    ]

    texto      = models.TextField()
    fuente     = models.CharField(max_length=20, choices=FUENTES, default="web")
    url_origen = models.URLField(blank=True, default="")
    # Embedding vectorial guardado como JSON (lista de floats)
    # Si usas pgvector, reemplazar por VectorField(dimensions=384)
    embedding_json = models.JSONField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Documento RAG"
        verbose_name_plural = "Documentos RAG"

    def __str__(self):
        return f"[{self.fuente}] {self.texto[:80]}..."


class PublicInformation(models.Model):
    title = models.CharField(max_length=200)              # Título del documento o sección
    category = models.CharField(max_length=100, blank=True)  # Ej: "Reglamento", "Trámite", "FAQ"
    content = models.TextField()                          # Texto completo
    timestamp = models.DateTimeField(auto_now_add=True)   # Fecha de creación
    updated_at = models.DateTimeField(auto_now=True)      # Última actualización
    status = models.CharField(max_length=20, choices=[
        ("ACTIVE", "Activo"),
        ("INACTIVE", "Inactivo"),
    ], default="ACTIVE")

    def __str__(self):
        return f"{self.title} ({self.category})"
    
# ─────────────────────────────────────────────────────────────
#  HISTORIAL DE CHAT
#  Opcional: guarda las conversaciones para análisis.
# ─────────────────────────────────────────────────────────────

class MensajeChat(models.Model):

    contenido  = models.TextField()
    profile    = models.ForeignKey("app_users.Profile", on_delete=models.CASCADE, related_name="mensajes_chat")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Mensaje de chat"
        verbose_name_plural = "Mensajes de chat"
        ordering            = ["created_at"]

    def __str__(self):
        return f"[{self.profile.user.first_name}] {self.contenido[:60]}..."