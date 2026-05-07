# scripts/load_public_info.py
import os
from ..models import PublicInformation

def load_public_info_from_txt(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        data = f.read()

    # Separar por bloques de "TÍTULO:"
    bloques = data.split("TÍTULO:")
    for bloque in bloques[1:]:  # el primero es cabecera
        lineas = bloque.strip().splitlines()
        titulo = lineas[0].strip()
        url = ""
        contenido = "\n".join(lineas[2:])  # saltar título y URL

        # Buscar URL explícita
        if lineas[1].startswith("URL:"):
            url = lineas[1].replace("URL:", "").strip()

        PublicInformation.objects.create(
            title=titulo,
            
            content=contenido,
            status="ACTIVE"
        )
        print(f"✔ Cargado: {titulo}")


