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
        "Diaphorencyrtus sp.",
        "Hirsutella citriformis",
        "Beauveria bassiana",
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
        "Relacion_DC_Hirsutella": "Alta",
        "Relacion_DC_Beauveria": "Alta",
        "Relacion_Compsus_Trigonospila": "Alta",
        "Relacion_PO_Chrysoperla": "Alta",
    }


def test_restricciones_documentadas() -> None:
    """¿Existen restricciones documentadas?"""
    filas = obtener_gestor().restricciones_documentadas()
    codigos = {fila["codigo"] for fila in filas}
    assert "aplicacion_insecticida_botanico" in codigos
    assert "aplicacion_extractos_vegetales" in codigos
    assert any(
        fila["relacion"] == "Relacion_DC_Tamarixia" and fila["codigo"] == "aplicacion_insecticida_botanico"
        for fila in filas
    )


def test_el_inventario_no_deja_lagunas_en_las_plagas_semilla() -> None:
    """Las tres plagas del inventario tienen agente; R3 queda para un nombre ausente."""
    assert obtener_gestor().lagunas() == []

    compsus = _consultar("Compsus_sp", 25, 70)
    assert compsus.recomendacion == "Documentado sin ventana de uso"
    assert compsus.agente == "Trigonospila unicaldasi"
    assert compsus.reglas_activadas == ["R5"]
    assert "R3" in compsus.explicacion.reglas_no_activadas

    acaro = _consultar("Phyllocoptruta_oleivora", 25, 70)
    assert acaro.recomendacion == "Documentado sin ventana de uso"
    assert acaro.agente == "Chrysoperla carnea"
    assert "R1" in acaro.explicacion.reglas_no_activadas


def test_conexiones_clayomics_y_magnetime() -> None:
    """¿Qué conexiones existen con ClayOMICS y MAGNETIME?"""
    competencia = responder_competencia()
    plataformas = {fila["plataforma"] for fila in competencia["conexiones"]}
    assert plataformas == {"ClayOMICS", "MAGNETIME"}
    estados = {fila["estado"] for fila in competencia["conexiones"]}
    assert estados <= {"documentado", "contexto"}
    assert "tomate" in competencia["lectura_conexiones"]
    assert "no es un resultado del spin-off" in competencia["lectura_conexiones"]


def test_r1_en_la_ventana_de_tamarixia() -> None:
    respuesta = _consultar("Diaphorina citri", 25, 70)
    assert respuesta.recomendacion == "AltamenteRecomendado"
    assert respuesta.agente == "Tamarixia radiata"
    assert respuesta.nivel_evidencia == "Alta"
    assert respuesta.condiciones["temperatura"] == [15, 35]
    assert "humedad" not in respuesta.condiciones
    assert respuesta.condiciones["humedad_ensayo"] == [60, 80]
    assert "no decide" in respuesta.explicacion.justificacion
    assert respuesta.fuente == "F02 - Restrepo-García et al. (2016)"
    assert respuesta.explicacion.reglas_activadas == ["R1", "R5"]
    assert "R2" in respuesta.explicacion.reglas_no_activadas
    assert "R4" in respuesta.explicacion.reglas_no_activadas
    assert "25 °C" in respuesta.explicacion.justificacion


def test_r1_incluye_los_bordes_de_la_ventana() -> None:
    for temperatura, humedad in ((15, 20), (35, 95)):
        respuesta = _consultar("D. citri", temperatura, humedad)
        assert respuesta.recomendacion == "AltamenteRecomendado"


def test_diaphorencyrtus_queda_como_hipotesis_sin_ventana() -> None:
    """A 26 °C y 90 % HR sigue Tamarixia: la humedad de ensayo no cierra R1."""
    respuesta = _consultar("Diaphorina_citri", 26, 90)
    assert respuesta.recomendacion == "AltamenteRecomendado"
    assert respuesta.agente == "Tamarixia radiata"
    assert "R2" in respuesta.explicacion.reglas_no_activadas
    alternativa = next(
        item for item in respuesta.explicacion.otras_relaciones if item.agente == "Diaphorencyrtus sp."
    )
    assert alternativa.aplicable is False
    assert alternativa.nivel_evidencia == "Media"
    assert "hipótesis" in alternativa.motivo.lower()


def test_r4_no_borra_la_recomendacion_alta() -> None:
    respuesta = _consultar("Diaphorina_citri", 25, 70, ["aplicacion_insecticida_botanico"])
    assert respuesta.recomendacion == "AltamenteRecomendado"
    assert respuesta.agente == "Tamarixia radiata"
    assert respuesta.explicacion.reglas_activadas == ["R1", "R4", "R5"]
    assert respuesta.restricciones_activas


def test_r4_no_cambia_de_agente_si_los_demas_no_tienen_ventana() -> None:
    respuesta = _consultar("Diaphorina_citri", 25, 70, ["aplicacion_extractos_vegetales"])
    assert respuesta.agente == "Tamarixia radiata"
    assert respuesta.explicacion.reglas_activadas == ["R1", "R4", "R5"]


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
