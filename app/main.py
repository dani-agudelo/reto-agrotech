"""Servicio HTTP del sistema experto de biocontrol.

Arranque, desde la raíz del proyecto:

    uvicorn app.main:app --reload
"""

from __future__ import annotations

import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import ADVERTENCIA, API_HOST, API_PORT, LOG_LEVEL, NS, VERSION
from app.ontology_manager import obtener_gestor
from app.reasoner import consultar, responder_competencia
from app.schemas import ConsultaEntrada, ConsultaSalida
from data.semilla import PRACTICAS

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def ciclo_de_vida(_aplicacion: FastAPI):
    """Carga la ontología al arrancar para que el primer error sea visible."""
    obtener_gestor()
    logger.info("Servicio de biocontrol listo.")
    yield


app = FastAPI(
    title="Sistema experto de biocontrol",
    summary="Consulta enemigos naturales de plagas de cítricos con evidencia trazable.",
    version=VERSION,
    lifespan=ciclo_de_vida,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def salud() -> dict[str, object]:
    """Estado del servicio y de la ontología cargada."""
    gestor = obtener_gestor()
    return {
        "estado": "ok",
        "version": VERSION,
        "ontologia_cargada": True,
        "iri": NS,
        "plagas": len(gestor.plagas),
        "agentes": len(gestor.listar_agentes()),
        "relaciones": len(gestor.relaciones),
        "fuentes": len(gestor.listar_fuentes()),
        "reglas_swrl": gestor.contar_reglas(),
        "java_disponible": gestor.java_disponible(),
        "motor_consulta": "python",
        "pellet": (
            "Las reglas SWRL están en el OWL. Owlready2 0.51 las ejecuta con "
            "Pellet solo si hay Java 25 o superior; si no, la consulta usa el motor Python."
        ),
        "advertencia": ADVERTENCIA,
    }


@app.get("/plagas")
def plagas() -> list[dict[str, object]]:
    """Plagas registradas en la ontología."""
    return [
        {
            "id": plaga.id,
            "nombre_cientifico": plaga.nombre_cientifico,
            "nombre_comun": plaga.nombre_comun,
            "cultivos": plaga.cultivos,
            "sin_agente": plaga.sin_agente,
        }
        for plaga in obtener_gestor().plagas
    ]


@app.get("/agentes")
def agentes() -> list[dict[str, str]]:
    """Agentes de biocontrol registrados en la ontología."""
    return obtener_gestor().listar_agentes()


@app.get("/fuentes")
def fuentes() -> list[dict[str, str]]:
    """Inventario de fuentes F01 a F17."""
    return obtener_gestor().listar_fuentes()


@app.get("/practicas")
def practicas() -> list[dict[str, str]]:
    """Prácticas que el usuario puede declarar para evaluar R4."""
    return [{"codigo": codigo, "etiqueta": etiqueta} for codigo, etiqueta in PRACTICAS]


@app.get("/competencia")
def competencia() -> dict[str, object]:
    """Respuestas de las cinco preguntas de competencia."""
    return responder_competencia()


@app.post("/consultar", response_model=ConsultaSalida)
def consultar_plaga(entrada: ConsultaEntrada) -> ConsultaSalida:
    """Recomienda, o explica la laguna, a partir de la plaga y el clima."""
    try:
        return consultar(entrada)
    except Exception as exc:
        logger.exception("Fallo al consultar %s", entrada.plaga)
        raise HTTPException(status_code=500, detail="No se pudo completar la consulta.") from exc


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=API_HOST, port=API_PORT, reload=False)
