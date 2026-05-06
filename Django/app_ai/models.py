from django.db import models
from Django.utils.logger import log_debug
log_debug("Cargando modelos de app_ai")

# Create your models here.

from django.db import models
from django.contrib.auth.models import User


# ─────────────────────────────────────────────────────────────
#  ESTUDIANTE
#  Se crea automáticamente cuando el usuario hace login con Google.
# ─────────────────────────────────────────────────────────────

class Estudiante(models.Model):
    """Perfil académico del estudiante vinculado al usuario Django."""
    user        = models.OneToOneField(User, on_delete=models.CASCADE, related_name="estudiante")
    documento   = models.CharField(max_length=20, unique=True, blank=True, default="")
    programa    = models.CharField(max_length=200, blank=True, default="")
    semestre    = models.PositiveSmallIntegerField(null=True, blank=True)
    sede        = models.CharField(max_length=100, blank=True, default="")
    correo_inst = models.EmailField(blank=True, default="")
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Estudiante"
        verbose_name_plural = "Estudiantes"

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.documento})"

    @property
    def nombre_completo(self):
        return self.user.get_full_name() or self.user.username


# ─────────────────────────────────────────────────────────────
#  HORARIO
#  Una fila por cada bloque de clase del estudiante.
#  Reemplaza horario.txt
# ─────────────────────────────────────────────────────────────

class Horario(models.Model):
    """Horario académico del semestre actual del estudiante."""

    DIAS = [
        ("Lunes",     "Lunes"),
        ("Martes",    "Martes"),
        ("Miércoles", "Miércoles"),
        ("Jueves",    "Jueves"),
        ("Viernes",   "Viernes"),
        ("Sábado",    "Sábado"),
    ]

    estudiante  = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name="horarios")
    codigo      = models.CharField(max_length=20)
    materia     = models.CharField(max_length=200)
    grupo       = models.CharField(max_length=10, default="01D")
    dia         = models.CharField(max_length=15, choices=DIAS)
    hora_inicio = models.TimeField()
    hora_fin    = models.TimeField()
    aula        = models.CharField(max_length=100)
    fecha_desde = models.DateField()
    fecha_hasta = models.DateField()
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Horario"
        verbose_name_plural = "Horarios"
        ordering            = ["dia", "hora_inicio"]
        # Un estudiante no puede tener la misma materia dos veces el mismo día a la misma hora
        unique_together = ["estudiante", "codigo", "dia", "hora_inicio"]

    def __str__(self):
        return (
            f"{self.materia} — {self.dia} "
            f"{self.hora_inicio.strftime('%H:%M')}-{self.hora_fin.strftime('%H:%M')} "
            f"| {self.aula}"
        )

    def as_context_text(self) -> str:
        """Genera el texto semántico para el RAG."""
        return (
            f"La materia {self.materia} (código {self.codigo}) "
            f"se dicta los {self.dia}s "
            f"de {self.hora_inicio.strftime('%I:%M %p')} a {self.hora_fin.strftime('%I:%M %p')} "
            f"en el aula {self.aula}."
        )


# ─────────────────────────────────────────────────────────────
#  NOTA
#  Una fila por cada materia del estudiante con todos sus cortes.
#  Reemplaza notas.txt
# ─────────────────────────────────────────────────────────────

class Nota(models.Model):
    """Calificaciones del estudiante por materia y período."""

    estudiante  = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name="notas")
    codigo      = models.CharField(max_length=20)
    materia     = models.CharField(max_length=200)
    seccion     = models.CharField(max_length=10, default="01D")
    corte1      = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    corte2      = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    corte3      = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    seguimiento = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    definitiva  = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Nota"
        verbose_name_plural = "Notas"
        ordering            = ["materia"]
        unique_together     = ["estudiante", "codigo"]

    def __str__(self):
        return f"{self.materia} — Def: {self.definitiva}"

    @property
    def aprobada(self) -> bool | None:
        """Retorna True si la nota definitiva >= 3.0"""
        if self.definitiva is None:
            return None
        return float(self.definitiva) >= 3.0

    def as_context_text(self) -> str:
        """Genera el texto semántico para el RAG."""
        partes = [f"Notas de {self.materia} (código {self.codigo}):"]
        if self.corte1      is not None: partes.append(f"Corte 1 (25%): {self.corte1}")
        if self.corte2      is not None: partes.append(f"Corte 2 (25%): {self.corte2}")
        if self.corte3      is not None: partes.append(f"Corte 3 (25%): {self.corte3}")
        if self.seguimiento is not None: partes.append(f"Seguimiento (25%): {self.seguimiento}")
        if self.definitiva  is not None: partes.append(f"Nota definitiva: {self.definitiva}")
        return " | ".join(partes)


# ─────────────────────────────────────────────────────────────
#  DOCENTE
#  Una fila por materia con el nombre del docente.
#  Reemplaza docentes.txt
# ─────────────────────────────────────────────────────────────

class Docente(models.Model):
    """Relación materia → docente (global, no depende del estudiante)."""
    codigo  = models.CharField(max_length=20, unique=True)
    materia = models.CharField(max_length=200)
    nombre  = models.CharField(max_length=200)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Docente"
        verbose_name_plural = "Docentes"
        ordering            = ["materia"]

    def __str__(self):
        return f"{self.nombre} — {self.materia}"

    def as_context_text(self) -> str:
        return f"El docente de {self.materia} (código {self.codigo}) es {self.nombre}."


# ─────────────────────────────────────────────────────────────
#  DOCUMENTO RAG (información pública institucional)
#  Reemplaza informacion_publica.txt + índice FAISS
# ─────────────────────────────────────────────────────────────

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


# ─────────────────────────────────────────────────────────────
#  HISTORIAL DE CHAT
#  Opcional: guarda las conversaciones para análisis.
# ─────────────────────────────────────────────────────────────

class MensajeChat(models.Model):
    """Historial de conversaciones del agente por estudiante."""
    ROL = [("user", "Usuario"), ("assistant", "Asistente")]

    estudiante = models.ForeignKey(
        Estudiante, on_delete=models.CASCADE,
        related_name="mensajes", null=True, blank=True
    )
    rol        = models.CharField(max_length=10, choices=ROL)
    contenido  = models.TextField()
    sesion_id  = models.CharField(max_length=64, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Mensaje de chat"
        verbose_name_plural = "Mensajes de chat"
        ordering            = ["created_at"]

    def __str__(self):
        return f"[{self.rol}] {self.contenido[:60]}..."