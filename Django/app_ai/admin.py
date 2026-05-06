from django.contrib import admin
from Django.utils.logger import log_debug
log_debug("Cargando admin de app_ai")

# Register your models here.
"""
admin.py — Panel de administración de Helper
Permite ver y gestionar estudiantes, horarios, notas y docentes.
"""

from django.contrib import admin
from .models import Estudiante, Horario, Nota, Docente, DocumentoRAG, MensajeChat


@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    list_display  = ["nombre_completo", "documento", "programa", "semestre", "updated_at"]
    search_fields = ["user__first_name", "user__last_name", "documento", "programa"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
    list_display  = ["materia", "estudiante", "dia", "hora_inicio", "hora_fin", "aula"]
    list_filter   = ["dia", "estudiante"]
    search_fields = ["materia", "codigo", "aula"]
    readonly_fields = ["updated_at"]


@admin.register(Nota)
class NotaAdmin(admin.ModelAdmin):
    list_display  = ["materia", "estudiante", "corte1", "corte2", "corte3", "definitiva", "aprobada"]
    list_filter   = ["estudiante"]
    search_fields = ["materia", "codigo"]
    readonly_fields = ["updated_at"]

    @admin.display(boolean=True, description="¿Aprobada?")
    def aprobada(self, obj):
        return obj.aprobada


@admin.register(Docente)
class DocenteAdmin(admin.ModelAdmin):
    list_display  = ["nombre", "materia", "codigo", "updated_at"]
    search_fields = ["nombre", "materia", "codigo"]


@admin.register(DocumentoRAG)
class DocumentoRAGAdmin(admin.ModelAdmin):
    list_display  = ["fuente", "texto_preview", "updated_at"]
    list_filter   = ["fuente"]
    search_fields = ["texto"]

    @admin.display(description="Texto")
    def texto_preview(self, obj):
        return obj.texto[:80] + "..." if len(obj.texto) > 80 else obj.texto


@admin.register(MensajeChat)
class MensajeChatAdmin(admin.ModelAdmin):
    list_display  = ["rol", "estudiante", "contenido_preview", "sesion_id", "created_at"]
    list_filter   = ["rol", "estudiante"]
    readonly_fields = ["created_at"]

    @admin.display(description="Mensaje")
    def contenido_preview(self, obj):
        return obj.contenido[:80] + "..." if len(obj.contenido) > 80 else obj.contenido
