"""La interfaz abre, consulta y muestra a Tamarixia sin lanzar una excepción."""

from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

UI = Path(__file__).resolve().parent.parent / "app" / "ui.py"


def test_consultar_muestra_tamarixia_y_la_regla_r1() -> None:
    aplicacion = AppTest.from_file(str(UI), default_timeout=60)
    aplicacion.run()
    assert not aplicacion.exception

    aplicacion.button(key="consultar").click().run()
    assert not aplicacion.exception

    textos = " ".join(elemento.value for elemento in aplicacion.markdown)
    assert "Tamarixia radiata" in textos
    assert "R1" in textos
    assert "prescripción agronómica" in textos.lower() or "prescripcion agronomica" in textos.lower()
