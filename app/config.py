"""Rutas, constantes visuales y advertencia del prototipo.

Las variables de entorno son opcionales. Si no existen, se usan las rutas
del repositorio para que `uvicorn` y `streamlit` arranquen desde la raíz.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parent.parent
load_dotenv(RAIZ / ".env")


def _ruta(variable: str, defecto: Path) -> Path:
    """Resuelve una ruta de entorno o devuelve el valor del repositorio."""
    valor = os.getenv(variable, "").strip()
    if not valor:
        return defecto
    camino = Path(valor)
    if not camino.is_absolute():
        camino = RAIZ / camino
    return camino


IRI = "http://agrotech.ucaldas.edu.co/ontologias/biocontrol"
NS = IRI + "#"

RUTA_ONTOLOGIA = _ruta("RUTA_ONTOLOGIA", RAIZ / "ontology" / "biocontrol.owl")
RUTA_REGLAS = _ruta("RUTA_REGLAS", RAIZ / "rules" / "rules.swrl")
RUTA_INSTANCIAS = _ruta("RUTA_INSTANCIAS", RAIZ / "data" / "instancias.ttl")
RUTA_FUENTES = _ruta("RUTA_FUENTES", RAIZ / "data" / "fuentes.csv")
RUTA_SHACL = _ruta("RUTA_SHACL", RAIZ / "ontology" / "shacl_shapes.ttl")

API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_BASE_URL = os.getenv("API_BASE_URL", f"http://{API_HOST}:{API_PORT}")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

VERSION = "1.0.0"
ADVERTENCIA = "Prototipo académico. No constituye prescripción agronómica."
PIE = "Este es un prototipo académico. No constituye prescripción agronómica."

# Colores institucionales y de estado de la evidencia.
AZUL = "#0D336E"
VERDE = "#2E8B57"
COLOR_ALTA = "#1B7F4E"
COLOR_MEDIA = "#8A6A00"
COLOR_BAJA = "#9B2335"
COLOR_FONDO = "#F4F7FB"

NIVELES = ("Alta", "Media", "Baja", "Insuficiente")
PESO_NIVEL = {"Alta": 3, "Media": 2, "Baja": 1, "Insuficiente": 0}
