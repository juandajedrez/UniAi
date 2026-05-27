"""
run_scraper.py — Management command Django
Ejecuta el scraper del SAC UniQuindío y guarda los resultados
directamente en PostgreSQL (modelos Horario, Nota, Docente).

Uso:
    python manage.py run_scraper
    python manage.py run_scraper --usuario <correo>
    python manage.py run_scraper --solo horario
    python manage.py run_scraper --solo notas
    python manage.py run_scraper --visible
"""

import re
import logging
from datetime import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

logger = logging.getLogger("scraper")


class Command(BaseCommand):
    help = "Extrae horario, notas y docentes del SAC UniQuindío y los guarda en PostgreSQL."

    def add_arguments(self, parser):
        parser.add_argument("--usuario", type=str, help="Correo del estudiante a scrapear")
        parser.add_argument("--solo",    type=str, choices=["horario", "notas", "docentes"],
                            help="Ejecutar solo un módulo")
        parser.add_argument("--visible", action="store_true", help="Navegador visible (sin headless)")

    def handle(self, *args, **options):
        from django.conf import settings

        usuario   = options.get("usuario")
        solo      = options.get("solo")
        headless  = not options.get("visible")

        self.stdout.write(self.style.SUCCESS("\n=== Scraper SAC UniQuindío ==="))

        # Buscar el usuario en la DB
        estudiante = self._get_estudiante(usuario)
        if not estudiante:
            return

        # Credenciales del .env
        creds = {
            "google_email":    settings.SAC_DOCUMENTO + "@uniquindio.edu.co"
                               if "@" not in settings.SAC_DOCUMENTO
                               else settings.SAC_DOCUMENTO,
            "google_password": "",              # se usa el scraper del SAC directo
            "sac_documento":   settings.SAC_DOCUMENTO,
            "sac_palabra":     settings.SAC_PALABRA_SECRETA,
            "sac_icono_index": settings.SAC_ICONO_INDEX,
        }

        with SACScraperDjango(headless=headless, creds=creds) as scraper:
            if not scraper.login_sac():
                self.stderr.write(self.style.ERROR("Login SAC fallido. Verifica las credenciales en .env"))
                return

            if not solo or solo == "horario":
                datos = scraper.extraer_horario()
                count = self._guardar_horario(estudiante, datos)
                self.stdout.write(self.style.SUCCESS(f"  ✅ Horario: {count} registros guardados"))

            if not solo or solo == "notas":
                datos = scraper.extraer_notas()
                count = self._guardar_notas(estudiante, datos)
                self.stdout.write(self.style.SUCCESS(f"  ✅ Notas: {count} registros guardados"))

            if not solo or solo == "docentes":
                datos = scraper.extraer_docentes()
                count = self._guardar_docentes(datos)
                self.stdout.write(self.style.SUCCESS(f"  ✅ Docentes: {count} registros guardados"))

        self.stdout.write(self.style.SUCCESS("\n=== Scraping completado ===\n"))

    # ─── Persistencia en DB ───────────────────────────────────

    def _get_estudiante(self, correo: str | None):
        from models import Estudiante
        from django.conf import settings

        if correo:
            try:
                user = User.objects.get(email=correo)
                return user.estudiante
            except (User.DoesNotExist, Estudiante.DoesNotExist):
                self.stderr.write(f"No se encontró estudiante con correo: {correo}")
                return None
        else:
            # Si no se especifica usuario, tomar el primero (modo desarrollo)
            try:
                return Estudiante.objects.first()
            except Exception:
                self.stderr.write("No hay estudiantes en la DB. Inicia sesión primero.")
                return None

    def _guardar_horario(self, estudiante, datos: list[dict]) -> int:
        from models import Horario

        count = 0
        for item in datos:
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

    def _guardar_notas(self, estudiante, datos: list[dict]) -> int:
        from models import Nota

        count = 0
        for item in datos:
            Nota.objects.update_or_create(
                estudiante = estudiante,
                codigo     = item["codigo"],
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

    def _guardar_docentes(self, datos: list[dict]) -> int:
        from models import Docente

        count = 0
        for item in datos:
            Docente.objects.update_or_create(
                codigo  = item["codigo"],
                defaults={
                    "materia": item["materia"],
                    "nombre":  item["nombre"],
                }
            )
            count += 1
        return count


# ─────────────────────────────────────────────────────────────
#  SCRAPER ADAPTADO PARA DJANGO (retorna dicts listos para la DB)
# ─────────────────────────────────────────────────────────────

class SACScraperDjango:
    """
    Versión del scraper de UniQuindío adaptada para Django.
    En lugar de guardar .txt, retorna listas de diccionarios
    listos para guardarse en PostgreSQL con el ORM.
    """

    URLS = {
        "sac_login":   "https://sac.uniquindio.edu.co/sgacampus/services/seguridad/login.jsp",
        "sac_horario": "https://sac.uniquindio.edu.co/sgacampus/services/estudiantiles/horarioEstudiante.jsp",
        "sac_notas":   "https://sac.uniquindio.edu.co/sgacampus/services/estudiantiles/notasRegistradas.jsp",
        "sac_docentes":"https://sac.uniquindio.edu.co/sgacampus/services/estudiantiles/docentesCurso.jsp",
    }

    DIAS_ES = {
        0: "Lunes", 1: "Martes", 2: "Miércoles",
        3: "Jueves", 4: "Viernes", 5: "Sábado", 6: "Domingo",
    }

    def __init__(self, headless: bool = True, creds: dict = None):
        self.headless = headless
        self.creds    = creds or {}
        self._pw      = None
        self.browser  = None
        self.page     = None

    def __enter__(self):
        from playwright.sync_api import sync_playwright
        self._pw     = sync_playwright().start()
        self.browser = self._pw.chromium.launch(headless=self.headless)
        context      = self.browser.new_context(locale="es-CO", timezone_id="America/Bogota")
        self.page    = context.new_page()
        self.page.set_default_timeout(20_000)
        return self

    def __exit__(self, *args):
        try:
            self.browser.close()
            self._pw.stop()
        except Exception:
            pass

    def login_sac(self) -> bool:
        """Login en el SAC con número de documento + palabra secreta + ícono."""
        import time
        try:
            self.page.goto(self.URLS["sac_login"], wait_until="networkidle")
            time.sleep(1.5)

            # Campo de documento
            doc_selectors = [
                "input[name='seleccion']", "input[name='documento']",
                "input[name='usuario']",   "input[id*='seleccion']",
            ]
            for sel in doc_selectors:
                el = self.page.query_selector(sel)
                if el:
                    el.fill(self.creds.get("sac_documento", ""))
                    break

            # Contraseña / palabra secreta
            pass_selectors = [
                "input[name='palabraSecreta']", "input[name='password']",
                "input[type='password']",
            ]
            for sel in pass_selectors:
                el = self.page.query_selector(sel)
                if el:
                    el.fill(self.creds.get("sac_palabra", ""))
                    break

            # Ícono secreto
            iconos = self.page.query_selector_all(
                "table img, .icono-secreto img, form img:not([src*='logo'])"
            )
            if iconos:
                idx = max(0, min(self.creds.get("sac_icono_index", 1) - 1, len(iconos) - 1))
                iconos[idx].click()

            # Submit
            for sel in ["input[type='submit']", "button[type='submit']", "button:has-text('Ingresar')"]:
                btn = self.page.query_selector(sel)
                if btn:
                    btn.click()
                    break

            time.sleep(3)
            self.page.wait_for_load_state("networkidle")
            return "login" not in self.page.url.lower()

        except Exception as e:
            logger.error(f"Error login SAC: {e}")
            return False

    def extraer_horario(self) -> list[dict]:
        """Extrae el horario y lo retorna como lista de dicts para el modelo Horario."""
        import time
        from bs4 import BeautifulSoup

        try:
            self.page.goto(self.URLS["sac_horario"], wait_until="networkidle")
            time.sleep(2)
            html = self.page.content()
        except Exception as e:
            logger.error(f"Error extrayendo horario HTML: {e}")
            return []

        return self._parse_horario_html(html)

    def extraer_notas(self) -> list[dict]:
        """Extrae notas y las retorna como lista de dicts para el modelo Nota."""
        import time

        try:
            self.page.goto(self.URLS["sac_notas"], wait_until="networkidle")
            time.sleep(2)
            html = self.page.content()
        except Exception as e:
            logger.error(f"Error extrayendo notas HTML: {e}")
            return []

        return self._parse_notas_html(html)

    def extraer_docentes(self) -> list[dict]:
        """Extrae docentes y los retorna como lista de dicts para el modelo Docente."""
        import time

        try:
            self.page.goto(self.URLS["sac_docentes"], wait_until="networkidle")
            time.sleep(2)
            html = self.page.content()
        except Exception as e:
            logger.error(f"Error extrayendo docentes HTML: {e}")
            return []

        return self._parse_docentes_html(html)

    # ─── Parsers HTML → dicts ─────────────────────────────────

    def _parse_horario_html(self, html: str) -> list[dict]:
        from bs4 import BeautifulSoup
        soup    = BeautifulSoup(html, "lxml")
        results = []

        tables = soup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            if len(rows) < 2:
                continue

            # Primera fila = encabezados de días
            header = rows[0]
            dias   = [th.get_text(strip=True) for th in header.find_all(["th", "td"])]

            for row in rows[1:]:
                cells = row.find_all(["td", "th"])
                if not cells:
                    continue

                hora_col = cells[0].get_text(strip=True)

                for col_idx, cell in enumerate(cells[1:], start=1):
                    texto = cell.get_text(separator="\n", strip=True)
                    if "Cod." not in texto:
                        continue

                    dia_nombre = dias[col_idx] if col_idx < len(dias) else ""
                    parsed     = self._parse_celda_horario(texto, hora_col, dia_nombre)
                    if parsed:
                        results.append(parsed)

        return results

    def _parse_celda_horario(self, texto: str, hora_col: str, dia_nombre: str) -> dict | None:
        """Parsea una celda individual del horario."""
        lines       = [l.strip() for l in texto.splitlines() if l.strip()]
        codigo      = nombre = aula = ""
        hora_inicio = hora_fin = None
        fecha_desde = fecha_hasta = None

        i = 0
        while i < len(lines):
            line = lines[i]
            if line.startswith("Cod."):
                codigo = line.replace("Cod.", "").strip()
            elif line.startswith("Prog.") and i + 1 < len(lines):
                nombre = lines[i + 1].strip()
                i += 1
            elif line.startswith("Aula."):
                aula = re.sub(r'[¿¡]', '', line.replace("Aula.", "")).strip()
                aula = re.sub(r'\bSAL\s*N\b', 'SALÓN', aula)
            elif re.match(r'^\d{2}/\d{2}/\d{2,4}', line):
                partes = line.split("-")
                if len(partes) >= 2 and not fecha_desde:
                    fecha_desde  = self._parse_fecha(partes[0].strip())
                    fecha_hasta  = self._parse_fecha(partes[1].strip())
            elif re.match(r'^\d{1,2}:\d{2}\s*[ap]m', line, re.I):
                horas = re.findall(r'\d{1,2}:\d{2}\s*[ap]m', line, re.I)
                if len(horas) >= 2:
                    hora_inicio = self._parse_hora(horas[0])
                    hora_fin    = self._parse_hora(horas[1])
            i += 1

        if not codigo or not nombre:
            return None

        # Si no se extrajo la hora del rango, usar la columna
        if hora_inicio is None:
            horas = re.findall(r'\d{1,2}:\d{2}\s*[ap]m', hora_col, re.I)
            if horas:
                hora_inicio = self._parse_hora(horas[0])
                hora_fin    = self._parse_hora(horas[-1]) if len(horas) > 1 else hora_inicio

        return {
            "codigo":      codigo,
            "materia":     nombre.title(),
            "dia":         dia_nombre,
            "hora_inicio": hora_inicio,
            "hora_fin":    hora_fin,
            "aula":        aula,
            "fecha_desde": fecha_desde or datetime.today().date(),
            "fecha_hasta": fecha_hasta or datetime.today().date(),
        }

    def _parse_notas_html(self, html: str) -> list[dict]:
        """Parsea el HTML de notas del SAC."""
        from bs4 import BeautifulSoup
        soup    = BeautifulSoup(html, "lxml")
        results = []
        vistos  = set()

        tables = soup.find_all("table")
        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]
                if len(cells) < 6:
                    continue

                # Buscar fila que tenga un código de materia
                codigo = cells[0].strip() if cells[0].strip().isdigit() else None
                if not codigo or codigo in vistos:
                    continue
                vistos.add(codigo)

                try:
                    results.append({
                        "codigo":      codigo,
                        "materia":     cells[1].strip().title(),
                        "seccion":     cells[2].strip() if len(cells) > 2 else "01D",
                        "corte1":      self._clean_nota(cells[3]) if len(cells) > 3 else None,
                        "corte2":      self._clean_nota(cells[4]) if len(cells) > 4 else None,
                        "corte3":      self._clean_nota(cells[5]) if len(cells) > 5 else None,
                        "seguimiento": self._clean_nota(cells[6]) if len(cells) > 6 else None,
                        "definitiva":  self._clean_nota(cells[7]) if len(cells) > 7 else None,
                    })
                except Exception:
                    continue

        return results

    def _parse_docentes_html(self, html: str) -> list[dict]:
        """Parsea el HTML de docentes del SAC."""
        from bs4 import BeautifulSoup
        soup    = BeautifulSoup(html, "lxml")
        results = []

        for table in soup.find_all("table"):
            for row in table.find_all("tr"):
                cells = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]
                if len(cells) < 3 or not cells[0].strip().isdigit():
                    continue
                codigo  = cells[0].strip()
                materia = cells[1].strip().title() if len(cells) > 1 else ""
                docente = self._format_nombre_docente(cells[-2]) if len(cells) > 2 else ""
                if codigo and materia and docente:
                    results.append({"codigo": codigo, "materia": materia, "nombre": docente})

        return results

    # ─── Utilidades ───────────────────────────────────────────

    @staticmethod
    def _parse_fecha(fecha_str: str):
        for fmt in ("%d/%m/%y", "%d/%m/%Y"):
            try:
                return datetime.strptime(fecha_str.strip(), fmt).date()
            except ValueError:
                pass
        return None

    @staticmethod
    def _parse_hora(hora_str: str):
        hora_str = hora_str.strip().lower().replace(" ", "")
        for fmt in ("%I:%M%p", "%H:%M"):
            try:
                return datetime.strptime(hora_str, fmt).time()
            except ValueError:
                pass
        return None

    @staticmethod
    def _clean_nota(valor: str) -> float | None:
        """Limpia valores duplicados por artefacto del scraping: '4.34.3' → 4.3"""
        s = str(valor).strip()
        n = len(s)
        if n >= 2 and s[:n//2] == s[n//2:]:
            s = s[:n//2]
        try:
            return round(float(s), 2)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _format_nombre_docente(raw: str) -> str:
        """Convierte 'URREA OSPINA ALEJANDRO' a 'Alejandro Urrea Ospina'."""
        palabras = raw.strip().split()
        if len(palabras) >= 3:
            apellidos = palabras[:2]
            nombres   = palabras[2:]
        elif len(palabras) == 2:
            apellidos, nombres = palabras[:1], palabras[1:]
        else:
            return raw.title()
        return " ".join(p.title() for p in nombres + apellidos)