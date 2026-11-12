"""Modelos de entrada y salida de la consulta.

Los nombres de los campos siguen el contrato del prototipo: la explicación
siempre viaja junto con la recomendación, y la advertencia académica no
se puede omitir.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.config import ADVERTENCIA


class ConsultaEntrada(BaseModel):
    """Hechos que declara quien consulta el sistema."""

    plaga: str = Field(..., min_length=1, description="Identificador o nombre de la plaga.")
    temperatura: float = Field(..., ge=-5, le=55, description="Temperatura del sitio, en °C.")
    humedad: float = Field(..., ge=0, le=100, description="Humedad relativa, en porcentaje.")
    practicas: list[str] = Field(
        default_factory=list,
        description="Códigos de prácticas agronómicas vigentes en el cultivo.",
    )


class PasoRegla(BaseModel):
    """Un nodo del árbol de explicación."""

    codigo: str
    nombre: str
    activada: bool
    detalle: str


class OtraRelacion(BaseModel):
    """Relación evaluada que no es la recomendación principal."""

    relacion: str
    agente: str
    nivel_evidencia: str
    aplicable: bool
    reglas: list[str] = Field(default_factory=list)
    motivo: str


class Explicacion(BaseModel):
    """Árbol de las reglas R1 a R5 para la conclusión elegida."""

    reglas_activadas: list[str]
    reglas_no_activadas: list[str]
    justificacion: str
    arbol: list[PasoRegla]
    otras_relaciones: list[OtraRelacion] = Field(default_factory=list)


class ConsultaSalida(BaseModel):
    """Respuesta de una consulta, con trazabilidad y advertencia."""

    recomendacion: str
    agente: str | None = None
    nivel_evidencia: str | None = None
    condiciones: dict[str, list[float | int]] | None = None
    fuente: str | None = None
    explicacion: Explicacion
    advertencia: str = ADVERTENCIA
    reglas_activadas: list[str]
    alternativas: list[OtraRelacion] = Field(default_factory=list)
    restricciones_activas: list[str] = Field(default_factory=list)
    nota_precaucion: str | None = None
    motor: str = "python"
    trazabilidad: dict[str, str] | None = None
