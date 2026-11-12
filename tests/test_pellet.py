"""Comprueba el puente con Pellet sin exigir Java 25 en cada máquina."""

from __future__ import annotations

from app.reasoner import probar_pellet


def test_pellet_devuelve_un_resultado_explicable() -> None:
    resultado = probar_pellet()
    assert "aplicado" in resultado
    if resultado["aplicado"]:
        assert resultado["r1_tamarixia"] is True
        assert resultado["r3_sin_laguna_en_la_semilla"] is True
    else:
        assert resultado["motivo"]
        assert "Python" in resultado["motivo"] or "Java" in resultado["motivo"]
