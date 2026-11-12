"""Contrato HTTP de la API de consulta."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_salud_ontologia_y_reglas() -> None:
    with TestClient(app) as cliente:
        respuesta = cliente.get("/health")
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["estado"] == "ok"
    assert cuerpo["ontologia_cargada"] is True
    assert cuerpo["plagas"] == 3
    assert cuerpo["relaciones"] == 6
    assert cuerpo["fuentes"] == 17
    assert cuerpo["reglas_swrl"] >= 5


def test_listados() -> None:
    with TestClient(app) as cliente:
        plagas = cliente.get("/plagas")
        agentes = cliente.get("/agentes")
    assert plagas.status_code == 200
    assert any(item["id"] == "Diaphorina_citri" for item in plagas.json())
    assert agentes.status_code == 200
    assert any(item["nombre_comun"] == "Tamarixia radiata" for item in agentes.json())


def test_consultar_devuelve_la_recomendacion_alta() -> None:
    with TestClient(app) as cliente:
        respuesta = cliente.post("/consultar", json={
            "plaga": "Diaphorina_citri",
            "temperatura": 25,
            "humedad": 70,
        })
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["recomendacion"] == "AltamenteRecomendado"
    assert cuerpo["agente"] == "Tamarixia radiata"
    assert cuerpo["fuente"] == "F02 - Restrepo-García et al. (2016)"
    assert cuerpo["explicacion"]["reglas_activadas"] == ["R1", "R5"]
    assert "prescripción" in cuerpo["advertencia"]


def test_consultar_sin_agente() -> None:
    with TestClient(app) as cliente:
        respuesta = cliente.post("/consultar", json={
            "plaga": "Compsus_sp",
            "temperatura": 25,
            "humedad": 70,
        })
    cuerpo = respuesta.json()
    assert cuerpo["recomendacion"] == "Documentado sin ventana de uso"
    assert cuerpo["agente"] == "Trigonospila unicaldasi"
    assert cuerpo["reglas_activadas"] == ["R5"]


def test_competencia_en_un_endpoint() -> None:
    with TestClient(app) as cliente:
        respuesta = cliente.get("/competencia")
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert len(cuerpo["enemigos_de_diaphorina_citri"]) == 4
    assert cuerpo["conexiones"]


def test_entrada_invalida() -> None:
    with TestClient(app) as cliente:
        respuesta = cliente.post("/consultar", json={"plaga": "", "temperatura": 25, "humedad": 70})
    assert respuesta.status_code == 422
