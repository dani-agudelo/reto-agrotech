"""Las cinco preguntas de competencia y los casos de cada regla."""

from __future__ import annotations

from app.ontology_manager import obtener_gestor
from app.reasoner import consultar, responder_competencia
from app.schemas import ConsultaEntrada


def _consultar(plaga: str, temperatura: float, humedad: float, practicas: list[str] | None = None):
    return consultar(ConsultaEntrada(
        plaga=plaga,
        temperatura=temperatura,
        humedad=humedad,
        practicas=practicas or [],
    ))


def test_enemigos_naturales_de_diaphorina() -> None:
    """¿Qué enemigos naturales están documentados para D. citri?"""
    filas = obtener_gestor().enemigos_de("Diaphorina_citri")
    nombres = {fila["cientifico"] for fila in filas}
    assert nombres == {
        "Tamarixia radiata",
        "Diaphorencyrtus aligarhensis",
        "Hirsutella citriformis",
    }
    tamarixia = next(fila for fila in filas if fila["cientifico"] == "Tamarixia radiata")
    assert tamarixia["nivel"] == "Alta"
    assert tamarixia["cita"] == "F02 - Restrepo-García et al. (2016)"


def test_nivel_de_evidencia_de_cada_relacion() -> None:
    """¿Qué nivel de evidencia respalda cada relación?"""
    niveles = {fila["relacion"]: fila["nivel"] for fila in obtener_gestor().niveles_de_evidencia()}
    assert niveles == {
        "Relacion_DC_Tamarixia": "Alta",
        "Relacion_DC_Diaphorencyrtus": "Media",
        "Relacion_DC_Hirsutella": "Media",
    }


def test_restricciones_documentadas() -> None:
    """¿Existen restricciones documentadas?"""
    filas = obtener_gestor().restricciones_documentadas()
    codigos = {fila["codigo"] for fila in filas}
    assert "aplicacion_piretroide" in codigos
    assert "aplicacion_fungicida_cuprico" in codigos
    assert any(fila["relacion"] == "Relacion_DC_Tamarixia" and fila["codigo"] == "aplicacion_piretroide" for fila in filas)


def test_plaga_sin_agente_dispara_r3() -> None:
    """¿Cómo responde el sistema ante una plaga sin agente documentado?"""
    lagunas = obtener_gestor().lagunas()
    plagas = {fila["plaga"] for fila in lagunas}
    assert "Compsus_sp" in plagas
    assert "Phyllocoptruta_oleivora" in plagas
    assert "Diaphorina_citri" not in plagas

    respuesta = _consultar("Compsus_sp", 25, 70)
    assert respuesta.recomendacion == "Evidencia insuficiente"
    assert respuesta.reglas_activadas == ["R3"]
    assert "laguna de conocimiento" in respuesta.explicacion.justificacion.lower()
    assert "R5" in respuesta.explicacion.reglas_no_activadas


def test_conexiones_clayomics_y_magnetime() -> None:
    """¿Qué conexiones existen con ClayOMICS y MAGNETIME?"""
    competencia = responder_competencia()
    plataformas = {fila["plataforma"] for fila in competencia["conexiones"]}
    assert plataformas == {"ClayOMICS", "MAGNETIME"}
    assert all(fila["estado"] == "propuesto" for fila in competencia["conexiones"])
    assert "medición ya hecha" in competencia["lectura_conexiones"]


def test_r1_en_la_ventana_de_tamarixia() -> None:
    respuesta = _consultar("Diaphorina citri", 25, 70)
    assert respuesta.recomendacion == "AltamenteRecomendado"
    assert respuesta.agente == "Tamarixia radiata"
    assert respuesta.nivel_evidencia == "Alta"
    assert respuesta.condiciones == {"temperatura": [20, 30], "humedad": [60, 85]}
    assert respuesta.fuente == "F02 - Restrepo-García et al. (2016)"
    assert respuesta.explicacion.reglas_activadas == ["R1", "R5"]
    assert "R2" in respuesta.explicacion.reglas_no_activadas
    assert "R4" in respuesta.explicacion.reglas_no_activadas
    assert "25 °C" in respuesta.explicacion.justificacion


def test_r1_incluye_los_bordes_de_la_ventana() -> None:
    for temperatura, humedad in ((20, 60), (30, 85)):
        respuesta = _consultar("D. citri", temperatura, humedad)
        assert respuesta.recomendacion == "AltamenteRecomendado"


def test_r2_cuando_solo_aplica_evidencia_media() -> None:
    respuesta = _consultar("Diaphorina_citri", 26, 90)
    assert respuesta.recomendacion == "PotencialmenteRecomendado"
    assert respuesta.agente == "Hirsutella citriformis"
    assert respuesta.nivel_evidencia == "Media"
    assert respuesta.explicacion.reglas_activadas == ["R2", "R5"]
    assert respuesta.nota_precaucion


def test_r4_no_borra_la_recomendacion_alta() -> None:
    respuesta = _consultar("Diaphorina_citri", 25, 70, ["aplicacion_piretroide"])
    assert respuesta.recomendacion == "AltamenteRecomendado"
    assert respuesta.agente == "Tamarixia radiata"
    assert respuesta.explicacion.reglas_activadas == ["R1", "R4", "R5"]
    assert respuesta.restricciones_activas


def test_r4_puede_cambiar_el_agente_preferido() -> None:
    respuesta = _consultar("Diaphorina_citri", 26, 90, ["aplicacion_fungicida_cuprico"])
    assert respuesta.agente == "Diaphorencyrtus aligarhensis"
    assert "R4" not in respuesta.explicacion.reglas_activadas
    assert any(item.agente == "Hirsutella citriformis" and "R4" in item.reglas for item in respuesta.explicacion.otras_relaciones)


def test_plaga_desconocida_tiene_mensaje_de_laguna() -> None:
    respuesta = _consultar("Toxoptera_sp", 25, 70)
    assert respuesta.recomendacion == "Evidencia insuficiente"
    assert respuesta.reglas_activadas == ["R3"]
    assert respuesta.explicacion.justificacion == (
        "La plaga consultada no está registrada en la base actual. "
        "Se activa R3: laguna de conocimiento."
    )


def test_clima_fuera_de_toda_ventana_no_es_laguna() -> None:
    respuesta = _consultar("Diaphorina_citri", 12, 70)
    assert respuesta.recomendacion == "Condiciones no satisfechas"
    assert respuesta.reglas_activadas == []
    assert "R3" in respuesta.explicacion.reglas_no_activadas
