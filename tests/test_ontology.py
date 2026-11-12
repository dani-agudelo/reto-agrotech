"""Pruebas de carga, consistencia y formas SHACL."""

from __future__ import annotations

from data.semilla import validar_semilla
from app.ontology_manager import obtener_gestor


def test_la_semilla_cierra_referencias() -> None:
    validar_semilla()


def test_ontologia_carga_clases_e_individuos() -> None:
    gestor = obtener_gestor()
    nombres = {plaga.id for plaga in gestor.plagas}
    assert nombres == {"Diaphorina_citri", "Compsus_sp", "Phyllocoptruta_oleivora"}
    agentes = {agente["id"] for agente in gestor.listar_agentes()}
    assert agentes == {
        "Tamarixia_radiata",
        "Diaphorencyrtus_sp",
        "Hirsutella_citriformis",
        "Beauveria_bassiana",
        "Trigonospila_unicaldasi",
        "Chrysoperla_carnea",
    }
    assert len(gestor.relaciones) == 6
    assert len(gestor.listar_fuentes()) == 17


def test_reglas_swrl_quedaron_en_el_owl() -> None:
    """R2 y R5 se parten en dos implicaciones; el archivo cubre R1 a R5."""
    gestor = obtener_gestor()
    assert gestor.contar_reglas() >= 5
    texto = gestor.texto_reglas()
    for codigo in ("R1_Aplicabilidad", "R2_Precaucion", "R3_LagunaConocimiento", "R4_Incompatibilidad", "R5_Trazabilidad"):
        assert codigo in texto
    assert "swrlb:greaterThanOrEqual" in texto
    assert "swrlb:lessThanOrEqual" in texto


def test_sparql_y_objetos_cuentan_las_mismas_relaciones() -> None:
    gestor = obtener_gestor()
    assert len(gestor.niveles_de_evidencia()) == len(gestor.relaciones)


def test_shacl_acepta_el_inventario() -> None:
    reporte = obtener_gestor().validar_shacl()
    assert reporte["cumple"] is True, reporte["reporte"]
