"""
import_data.py — Management command Django
Importa los archivos .txt generados por el scraper anterior
a la base de datos (SQLite en desarrollo, PostgreSQL en producción).

Uso:
    python manage.py import_data
    python manage.py import_data --dir ruta/a/documentos
    python manage.py import_data --solo horario
    python manage.py import_data --usuario correo@uniquindio.edu.co
    python manage.py import_data --limpiar   # borra datos previos antes de importar

Archivos que lee:
    data/documents/horario.txt
    data/documents/notas.txt
    data/documents/docentes.txt
"""

import re
import logging
from pathlib import Path
from datetime import datetime, time
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

logger = logging.getLogger("scraper")


class Command(BaseCommand):
    help = "Importa horario, notas y docentes desde archivos .txt a la base de datos."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dir", type=str, default="data/documents",
            help="Directorio con los archivos .txt (default: data/documents)"
        )
        parser.add_argument(
            "--usuario", type=str, default=None,
            help="Correo del estudiante al que asignar los datos"
        )
        parser.add_argument(
            "--solo", type=str, choices=["horario", "notas", "docentes"],
            help="Importar solo un tipo de datos"
        )
        parser.add_argument(
            "--limpiar", action="store_true",
            help="Eliminar datos previos del estudiante antes de importar"
        )

    def handle(self, *args, **options):
        docs_dir = Path(options["dir"])
        solo     = options.get("solo")
        limpiar  = options.get("limpiar", False)

        if not docs_dir.exists():
            raise CommandError(f"Directorio no encontrado: {docs_dir}")

        self.stdout.write(self.style.SUCCESS(f"\n=== Importando datos desde {docs_dir} ==="))

        # Obtener o crear el estudiante
        estudiante = self._get_o_crear_estudiante(options.get("usuario"))
        if not estudiante:
            return

        self.stdout.write(f"  Estudiante: {estudiante}")

        if limpiar:
            self._limpiar_datos(estudiante, solo)

        # ── Importar según selección ──────────────────────────
        if not solo or solo == "horario":
            path = docs_dir / "horario.txt"
            if path.exists():
                n = self._importar_horario(estudiante, path)
                self.stdout.write(self.style.SUCCESS(f"  ✅ Horario: {n} registros importados"))
            else:
                self.stdout.write(self.style.WARNING(f"  ⚠️  No se encontró horario.txt en {docs_dir}"))

        if not solo or solo == "notas":
            path = docs_dir / "notas.txt"
            if path.exists():
                n = self._importar_notas(estudiante, path)
                self.stdout.write(self.style.SUCCESS(f"  ✅ Notas: {n} registros importados"))
            else:
                self.stdout.write(self.style.WARNING(f"  ⚠️  No se encontró notas.txt en {docs_dir}"))

        if not solo or solo == "docentes":
            path = docs_dir / "docentes.txt"
            if path.exists():
                n = self._importar_docentes(path)
                self.stdout.write(self.style.SUCCESS(f"  ✅ Docentes: {n} registros importados"))
            else:
                self.stdout.write(self.style.WARNING(f"  ⚠️  No se encontró docentes.txt en {docs_dir}"))

        self.stdout.write(self.style.SUCCESS("\n=== Importación completada ===\n"))

    # ─────────────────────────────────────────────────────────
    #  ESTUDIANTE
    # ─────────────────────────────────────────────────────────

    def _get_o_crear_estudiante(self, correo: str | None):
        from ..models import Estudiante

        if correo:
            try:
                user = User.objects.get(email=correo)
                estudiante, _ = Estudiante.objects.get_or_create(user=user)
                return estudiante
            except User.DoesNotExist:
                # Crear usuario y estudiante de desarrollo
                self.stdout.write(
                    self.style.WARNING(f"  Usuario {correo} no existe. Creando usuario de desarrollo...")
                )
                nombre  = correo.split("@")[0]
                user    = User.objects.create_user(
                    username=nombre, email=correo,
                    first_name=nombre.capitalize()
                )
                estudiante, _ = Estudiante.objects.get_or_create(user=user)
                return estudiante
        else:
            # Usar el primer estudiante disponible o crear uno por defecto
            estudiante = Estudiante.objects.first()
            if estudiante:
                return estudiante

            self.stdout.write(
                self.style.WARNING(
                    "  No hay estudiantes en la DB. "
                    "Creando usuario de desarrollo 'estudiante@uniquindio.edu.co'..."
                )
            )
            user, _ = User.objects.get_or_create(
                username="estudiante_dev",
                defaults={
                    "email":      "estudiante@uniquindio.edu.co",
                    "first_name": "Estudiante",
                    "last_name":  "Desarrollo",
                }
            )
            estudiante, _ = Estudiante.objects.get_or_create(user=user)
            return estudiante

    def _limpiar_datos(self, estudiante, solo: str | None):
        from models import Horario, Nota

        if not solo or solo == "horario":
            n = Horario.objects.filter(estudiante=estudiante).delete()[0]
            self.stdout.write(f"  🗑️  Horarios eliminados: {n}")
        if not solo or solo == "notas":
            n = Nota.objects.filter(estudiante=estudiante).delete()[0]
            self.stdout.write(f"  🗑️  Notas eliminadas: {n}")

    # ─────────────────────────────────────────────────────────
    #  IMPORTAR HORARIO
    # ─────────────────────────────────────────────────────────

    DIAS_ES = {
        0: "Lunes", 1: "Martes", 2: "Miércoles",
        3: "Jueves", 4: "Viernes", 5: "Sábado", 6: "Domingo",
    }

    def _importar_horario(self, estudiante, path: Path) -> int:
        from ..models import Horario

        text  = path.read_text(encoding="utf-8")
        items = self._parse_horario(text)
        count = 0

        for item in items:
            if not item.get("codigo") or not item.get("materia"):
                continue
            Horario.objects.update_or_create(
                estudiante  = estudiante,
                codigo      = item["codigo"],
                dia         = item["dia"],
                hora_inicio = item["hora_inicio"],
                defaults={
                    "materia":     item["materia"],
                    "grupo":       item.get("grupo", "01D"),
                    "hora_fin":    item["hora_fin"],
                    "aula":        item["aula"],
                    "fecha_desde": item["fecha_desde"],
                    "fecha_hasta": item["fecha_hasta"],
                }
            )
            count += 1

        return count

    def _parse_horario(self, text: str) -> list[dict]:
        """
        Parsea el horario.txt del SAC UniQuindío.
        Deriva el día de la semana desde la primera fecha de cada bloque.
        """
        results    = []
        hora_slot  = ""
        lineas     = text.splitlines()
        bloques_raw: list[tuple[str, list[str]]] = []
        bloque_actual: list[str] = []
        hora_franja = ""

        for linea in lineas:
            s = linea.strip()
            if re.match(r'^\d{1,2}:\d{2}\s*[ap]m$', s, re.I):
                if bloque_actual:
                    bloques_raw.append((hora_franja, bloque_actual))
                    bloque_actual = []
                hora_franja = s
            else:
                bloque_actual.append(linea)
        if bloque_actual:
            bloques_raw.append((hora_franja, bloque_actual))

        for hora_slot, lineas_bloque in bloques_raw:
            texto_bloque = "\n".join(lineas_bloque)
            for sub in re.split(r'\n(?=Cod\.)', texto_bloque):
                sub = sub.strip()
                if "Cod." not in sub:
                    continue

                lines = [l.strip() for l in sub.splitlines() if l.strip()]
                codigo = nombre = hora_rango = dia = grupo = ""
                aulas: list[str] = []
                fecha_desde = fecha_hasta = None
                i = 0

                while i < len(lines):
                    line = lines[i]
                    if line.startswith("Cod."):
                        codigo = line.replace("Cod.", "").strip()
                    elif line.startswith("Prog.") and i + 1 < len(lines):
                        nombre = lines[i + 1].strip()
                        i += 1
                    elif line.startswith("Grupo."):
                        grupo = line.replace("Grupo.", "").strip()
                    elif re.match(r'^\d{2}/\d{2}/\d{2,4}', line):
                        partes = line.split("-")
                        if not dia:
                            raw_fecha = partes[0].strip()
                            for fmt in ("%d/%m/%y", "%d/%m/%Y"):
                                try:
                                    dt = datetime.strptime(raw_fecha, fmt)
                                    dia = self.DIAS_ES[dt.weekday()]
                                    fecha_desde = dt.date()
                                    break
                                except ValueError:
                                    pass
                        if len(partes) >= 2 and not fecha_hasta:
                            for fmt in ("%d/%m/%y", "%d/%m/%Y"):
                                try:
                                    fecha_hasta = datetime.strptime(partes[1].strip(), fmt).date()
                                    break
                                except ValueError:
                                    pass
                    elif line.startswith("Aula."):
                        aula_raw = re.sub(r'[¿¡]', '', line.replace("Aula.", "")).strip()
                        aula_raw = re.sub(r'\bSAL\s*N\b', 'SALÓN', aula_raw)
                        aulas.append(aula_raw)
                    elif re.match(
                        r'^\d{1,2}:\d{2}\s*[ap]m\s*[-–]\s*\d{1,2}:\d{2}\s*[ap]m$',
                        line, re.I
                    ):
                        hora_rango = line
                    i += 1

                if not nombre or not codigo:
                    continue

                aula      = aulas[-1] if aulas else "por confirmar"
                hora_str  = hora_rango if hora_rango else hora_slot
                horas     = re.findall(r'\d{1,2}:\d{2}\s*[ap]m', hora_str, re.I)
                hora_ini  = self._parse_hora(horas[0]) if horas else time(7, 0)
                hora_fin  = self._parse_hora(horas[-1]) if len(horas) > 1 else time(9, 0)

                results.append({
                    "codigo":      codigo,
                    "materia":     nombre.title(),
                    "grupo":       grupo or "01D",
                    "dia":         dia,
                    "hora_inicio": hora_ini,
                    "hora_fin":    hora_fin,
                    "aula":        aula,
                    "fecha_desde": fecha_desde or datetime.today().date(),
                    "fecha_hasta": fecha_hasta or datetime.today().date(),
                })

        return results

    # ─────────────────────────────────────────────────────────
    #  IMPORTAR NOTAS
    # ─────────────────────────────────────────────────────────

    def _importar_notas(self, estudiante, path: Path) -> int:
        from ..models import Nota

        text    = path.read_text(encoding="utf-8")
        items   = self._parse_notas(text)
        count   = 0
        vistos  = set()

        for item in items:
            codigo = item.get("codigo", "")
            if not codigo or codigo in vistos:
                continue
            vistos.add(codigo)

            Nota.objects.update_or_create(
                estudiante = estudiante,
                codigo     = codigo,
                defaults={
                    "materia":     item["materia"],
                    "seccion":     item.get("seccion", "01D"),
                    "corte1":      item.get("corte1"),
                    "corte2":      item.get("corte2"),
                    "corte3":      item.get("corte3"),
                    "seguimiento": item.get("seguimiento"),
                    "definitiva":  item.get("definitiva"),
                }
            )
            count += 1

        return count

    def _parse_notas(self, text: str) -> list[dict]:
        results = []
        materias = re.split(r'(?=CODIGO:)', text)

        for materia in materias:
            materia = materia.strip()
            if "CODIGO:" not in materia:
                continue

            m_cod = re.search(r'CODIGO:\s*(\d+)',       materia)
            m_cur = re.search(r'CURSO:\s*(.+)',          materia)
            m_sec = re.search(r'SECCION:\s*(.+)',         materia)

            if not m_cod or not m_cur:
                continue

            etiquetas = [
                ("NOTA1",       "corte1"),
                ("NOTA2",       "corte2"),
                ("NOTA3",       "corte3"),
                ("SEGUIMIENTO", "seguimiento"),
                ("DEFINITIVA",  "definitiva"),
            ]
            notas = {}
            for clave, campo in etiquetas:
                m = re.search(rf'NOTAS:\s*{clave}:\s*([\d.]+)', materia)
                if m:
                    notas[campo] = self._limpiar_nota(m.group(1))

            results.append({
                "codigo":  m_cod.group(1).strip(),
                "materia": m_cur.group(1).strip().title(),
                "seccion": m_sec.group(1).strip() if m_sec else "01D",
                **notas,
            })

        return results

    # ─────────────────────────────────────────────────────────
    #  IMPORTAR DOCENTES
    # ─────────────────────────────────────────────────────────

    def _importar_docentes(self, path: Path) -> int:
        from ..models import Docente

        text  = path.read_text(encoding="utf-8")
        items = self._parse_docentes(text)
        count = 0

        for item in items:
            if not item.get("codigo"):
                continue
            Docente.objects.update_or_create(
                codigo   = item["codigo"],
                defaults={
                    "materia": item["materia"],
                    "nombre":  item["nombre"],
                }
            )
            count += 1

        return count

    def _parse_docentes(self, text: str) -> list[dict]:
        results  = []
        registros = re.split(r'(?=\b\d{5}\b)', text)

        for reg in registros:
            reg = reg.strip()
            if not reg:
                continue

            m_cod = re.match(r'^(\d{5})\s+', reg)
            if not m_cod:
                continue
            codigo = m_cod.group(1)
            resto  = reg[m_cod.end():]

            m_mat = re.match(r'([A-ZÁÉÍÓÚÑ\s]+?)\s+\d{2}[A-Z]\s+', resto)
            if not m_mat:
                continue
            materia = m_mat.group(1).strip()
            resto2  = resto[m_mat.end():]

            m_doc = re.search(
                r'\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+'
                r'([A-ZÁÉÍÓÚÑ]+(?:\s+[A-ZÁÉÍÓÚÑ]+){1,4})\s+SEDE',
                resto2
            )
            if not m_doc:
                m_doc = re.search(r'([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]{5,40})\s+SEDE', resto2)
            if not m_doc:
                continue

            palabras = m_doc.group(1).strip().split()
            if len(palabras) >= 3:
                apellidos, nombres = palabras[:2], palabras[2:]
            elif len(palabras) == 2:
                apellidos, nombres = palabras[:1], palabras[1:]
            else:
                apellidos, nombres = [], palabras

            nombre_fmt = " ".join(p.title() for p in nombres + apellidos)

            results.append({
                "codigo":  codigo,
                "materia": materia.title(),
                "nombre":  nombre_fmt,
            })

        return results

    # ─────────────────────────────────────────────────────────
    #  UTILIDADES
    # ─────────────────────────────────────────────────────────

    @staticmethod
    def _parse_hora(hora_str: str) -> time:
        hora_str = hora_str.strip().lower().replace(" ", "")
        for fmt in ("%I:%M%p", "%H:%M"):
            try:
                return datetime.strptime(hora_str, fmt).time()
            except ValueError:
                pass
        return time(7, 0)

    @staticmethod
    def _limpiar_nota(valor: str) -> float | None:
        """Corrige artefacto de scraping: '4.34.3' → 4.3, '55' → 5.0"""
        s = str(valor).strip()
        n = len(s)
        if n >= 2 and s[:n // 2] == s[n // 2:]:
            s = s[:n // 2]
        try:
            return round(float(s), 2)
        except (ValueError, TypeError):
            return None