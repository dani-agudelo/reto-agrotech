"""Interfaz del sistema experto de biocontrol.

Desde la raíz del proyecto:

    streamlit run app/ui.py

La pantalla comparte el motor con la API: no hace falta tener uvicorn
encendido para consultar. Las tres zonas de la consulta son la entrada,
el resultado y la explicación.
"""

from __future__ import annotations

import logging
import sys
from html import escape
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import streamlit as st

from app.config import ADVERTENCIA, AZUL, LOG_LEVEL, PIE, VERDE
from app.ontology_manager import obtener_gestor
from app.reasoner import LECTURA_CONEXIONES, consultar, responder_competencia
from app.schemas import ConsultaEntrada, ConsultaSalida
from data.semilla import PRACTICAS

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

st.set_page_config(
    page_title="Sistema Experto de Biocontrol",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inyectar_estilo() -> None:
    """Aplica la tipografía, el azul institucional y las tarjetas."""
    st.markdown(
        f"""
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;500;600;700&display=swap');
          html, body, [class*="css"] {{
            font-family: "Noto Sans", "Segoe UI", sans-serif;
          }}
          .stApp {{
            background:
              radial-gradient(1200px 400px at 10% -10%, rgba(13, 51, 110, 0.08), transparent 50%),
              { "#F4F7FB" };
          }}
          [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {AZUL} 0%, #071833 100%);
          }}
          [data-testid="stSidebar"] h1,
          [data-testid="stSidebar"] h2,
          [data-testid="stSidebar"] h3,
          [data-testid="stSidebar"] p,
          [data-testid="stSidebar"] label,
          [data-testid="stSidebar"] span {{
            color: #F7F9FC !important;
          }}
          [data-testid="stSidebar"] [data-baseweb="radio"] {{
            background: transparent;
          }}
          .bio-banner {{
            background: linear-gradient(135deg, {AZUL} 0%, #1A4A8A 70%, {VERDE} 140%);
            color: white;
            border-radius: 18px;
            padding: 28px 32px;
            margin-bottom: 18px;
            box-shadow: 0 12px 30px rgba(13, 51, 110, 0.18);
          }}
          .bio-banner h1 {{
            color: white;
            font-size: 1.9rem;
            margin: 4px 0 6px 0;
            letter-spacing: -0.03em;
          }}
          .bio-kicker {{
            text-transform: uppercase;
            letter-spacing: 0.14em;
            font-size: 0.72rem;
            opacity: 0.85;
            font-weight: 600;
          }}
          .bio-banner p {{ color: rgba(255,255,255,0.9); margin: 0; }}
          .bio-card {{
            background: white;
            border-radius: 16px;
            padding: 20px 22px;
            box-shadow: 0 8px 24px rgba(16, 36, 63, 0.08);
            border: 1px solid rgba(13, 51, 110, 0.06);
            min-height: 220px;
          }}
          .bio-alta {{ border-top: 6px solid #1B7F4E; }}
          .bio-media {{ border-top: 6px solid #C4920A; }}
          .bio-baja {{ border-top: 6px solid #9B2335; }}
          .bio-neutral {{ border-top: 6px solid {AZUL}; }}
          .bio-etiqueta {{
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #5C6B80;
          }}
          .bio-titulo {{
            font-size: 1.35rem;
            font-weight: 700;
            color: #142033;
            margin: 6px 0;
          }}
          .bio-agente {{
            font-size: 1.15rem;
            color: {AZUL};
            font-weight: 650;
          }}
          .bio-pill {{
            display: inline-block;
            background: #EEF3FA;
            color: {AZUL};
            border-radius: 999px;
            padding: 4px 10px;
            margin: 8px 6px 0 0;
            font-size: 0.85rem;
          }}
          .bio-nota {{ color: #3D4A5C; line-height: 1.45; }}
          .bio-alerta {{
            background: #FFF6D8;
            color: #6B5200;
            border-radius: 10px;
            padding: 10px 12px;
            margin-top: 12px;
          }}
          .bio-footer {{
            margin-top: 28px;
            padding: 12px 16px;
            text-align: center;
            color: #5C6B80;
            font-size: 0.9rem;
          }}
          .bio-seccion {{
            color: {AZUL};
            font-weight: 700;
            margin-bottom: 8px;
          }}
          div.stButton > button[kind="primary"] {{
            background: {AZUL};
            border: none;
            border-radius: 12px;
            padding: 0.6rem 1rem;
            font-weight: 650;
          }}
          div.stButton > button[kind="primary"]:hover {{
            background: #16488F;
          }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def logo_svg() -> str:
    """Marca geométrica del prototipo. No reproduce el escudo de la universidad."""
    return """
    <svg width="72" height="72" viewBox="0 0 72 72" fill="none" aria-hidden="true">
      <rect width="72" height="72" rx="18" fill="#F4F7FB"/>
      <circle cx="36" cy="34" r="16" fill="#F4D35E"/>
      <circle cx="36" cy="34" r="7" fill="#0D336E"/>
      <path d="M48 18c8 6 10 16 6 24" stroke="#2E8B57" stroke-width="4" stroke-linecap="round"/>
      <path d="M50 16c6 2 9 8 8 14" stroke="#1B7F4E" stroke-width="3" stroke-linecap="round"/>
    </svg>
    """


def clase_visual(resultado: ConsultaSalida) -> str:
    """Elige el color de la tarjeta según la recomendación y la evidencia."""
    if resultado.recomendacion == "AltamenteRecomendado":
        return "bio-alta"
    if resultado.recomendacion == "PotencialmenteRecomendado":
        return "bio-media"
    if resultado.recomendacion == "Evidencia insuficiente":
        return "bio-baja"
    return "bio-neutral"


def tarjeta_resultado(resultado: ConsultaSalida) -> str:
    """HTML de la tarjeta de recomendación."""
    titulo = {
        "AltamenteRecomendado": "Altamente recomendado",
        "PotencialmenteRecomendado": "Potencialmente recomendado",
        "Evidencia insuficiente": "Evidencia insuficiente",
        "Condiciones no satisfechas": "Condiciones no satisfechas",
    }.get(resultado.recomendacion, resultado.recomendacion)
    agente = f'<div class="bio-agente">{escape(resultado.agente)}</div>' if resultado.agente else ""
    nivel = (
        f'<span class="bio-pill">Evidencia {escape(resultado.nivel_evidencia or "")}</span>'
        if resultado.nivel_evidencia
        else ""
    )
    fuente = (
        f'<span class="bio-pill">{escape(resultado.fuente or "")}</span>' if resultado.fuente else ""
    )
    condiciones = ""
    if resultado.condiciones:
        temperatura = resultado.condiciones["temperatura"]
        humedad = resultado.condiciones["humedad"]
        condiciones = (
            f'<span class="bio-pill">Temperatura {temperatura[0]}–{temperatura[1]} °C</span>'
            f'<span class="bio-pill">Humedad {humedad[0]}–{humedad[1]} %</span>'
        )
    alerta = ""
    if resultado.restricciones_activas:
        texto = "; ".join(resultado.restricciones_activas)
        alerta = f'<div class="bio-alerta">Restricción activa: {escape(texto)}</div>'
    if resultado.nota_precaucion:
        alerta += f'<div class="bio-alerta">{escape(resultado.nota_precaucion)}</div>'
    return f"""
    <div class="bio-card {clase_visual(resultado)}">
      <div class="bio-etiqueta">Resultado</div>
      <div class="bio-titulo">{escape(titulo)}</div>
      {agente}
      <div>{nivel}{fuente}{condiciones}</div>
      {alerta}
      <p class="bio-nota">{escape(ADVERTENCIA)}</p>
    </div>
    """


def pagina_consulta(gestor) -> None:
    """Entrada, resultado y explicación en tres columnas."""
    st.session_state.setdefault("temperatura", 25)
    st.session_state.setdefault("humedad", 70)
    st.session_state.setdefault("plaga_id", "Diaphorina_citri")
    st.session_state.setdefault("practicas", [])

    columna_entrada, columna_resultado, columna_explicacion = st.columns([1.05, 1.15, 1.15], gap="large")

    with columna_entrada:
        st.markdown('<div class="bio-seccion">1. Entrada</div>', unsafe_allow_html=True)
        if st.button("Usar ejemplo: D. citri, 25 °C, 70 %"):
            st.session_state.temperatura = 25
            st.session_state.humedad = 70
            st.session_state.plaga_id = "Diaphorina_citri"
            st.session_state.practicas = []
            st.rerun()

        identificadores = [plaga.id for plaga in gestor.plagas]
        st.selectbox(
            "Plaga",
            identificadores,
            format_func=lambda identificador: _etiqueta_plaga(gestor, identificador),
            key="plaga_id",
        )
        st.slider("Temperatura (°C)", min_value=10, max_value=40, step=1, key="temperatura")
        st.slider("Humedad relativa (%)", min_value=20, max_value=100, step=1, key="humedad")
        st.multiselect(
            "Prácticas vigentes en el cultivo",
            options=[codigo for codigo, _etiqueta in PRACTICAS],
            format_func=lambda codigo: dict(PRACTICAS)[codigo],
            key="practicas",
        )
        st.caption(
            "Las ventanas de temperatura y humedad son parámetros operativos del prototipo, "
            "anclados en las fuentes del inventario."
        )
        consultar_ahora = st.button(
            "🔍 Consultar",
            type="primary",
            use_container_width=True,
            key="consultar",
        )

    if consultar_ahora:
        st.session_state.resultado = consultar(ConsultaEntrada(
            plaga=st.session_state.plaga_id,
            temperatura=float(st.session_state.temperatura),
            humedad=float(st.session_state.humedad),
            practicas=list(st.session_state.practicas),
        ))

    resultado: ConsultaSalida | None = st.session_state.get("resultado")

    with columna_resultado:
        st.markdown('<div class="bio-seccion">2. Resultado</div>', unsafe_allow_html=True)
        if resultado is None:
            st.markdown(
                '<div class="bio-card bio-neutral"><div class="bio-etiqueta">Resultado</div>'
                '<div class="bio-titulo">Aún no hay una consulta</div>'
                '<p class="bio-nota">Elija la plaga y el clima, y pulse Consultar.</p></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(tarjeta_resultado(resultado), unsafe_allow_html=True)
            if resultado.alternativas:
                st.markdown("**Otras relaciones aplicables**")
                for alternativa in resultado.alternativas:
                    st.caption(f"{alternativa.agente} · {alternativa.nivel_evidencia}. {alternativa.motivo}")

    with columna_explicacion:
        st.markdown('<div class="bio-seccion">3. Explicación</div>', unsafe_allow_html=True)
        if resultado is None:
            st.info("El árbol de reglas aparece aquí después de consultar.")
        else:
            with st.expander("Árbol de inferencia", expanded=True):
                for paso in resultado.explicacion.arbol:
                    marca = "✅" if paso.activada else "❌"
                    estado = "activada" if paso.activada else "no activada"
                    st.markdown(f"**{marca} {paso.codigo} {paso.nombre}** — {estado}")
                    st.caption(paso.detalle)
                st.markdown(resultado.explicacion.justificacion)
            if resultado.trazabilidad:
                st.caption(
                    f"Trazabilidad: {resultado.trazabilidad['relacion']} · "
                    f"{resultado.trazabilidad['fuente']}"
                )


def _etiqueta_plaga(gestor, identificador: str) -> str:
    plaga = gestor.plaga_por_id(identificador)
    if plaga is None:
        return identificador
    return f"{plaga.nombre_cientifico} — {plaga.nombre_comun}"


def pagina_competencia(gestor) -> None:
    """Muestra las cinco preguntas que el informe pide poder responder."""
    respuestas = responder_competencia(gestor)
    preguntas = [
        (
            "¿Qué enemigos naturales están documentados para D. citri?",
            _texto_enemigos(respuestas["enemigos_de_diaphorina_citri"]),
        ),
        (
            "¿Qué nivel de evidencia respalda cada relación?",
            _texto_niveles(respuestas["niveles_de_evidencia"]),
        ),
        (
            "¿Existen restricciones documentadas?",
            _texto_restricciones(respuestas["restricciones"]),
        ),
        (
            "¿Cómo responde el sistema ante una plaga sin agente documentado?",
            respuestas["respuesta_sin_agente"]["explicacion"]["justificacion"],
        ),
        (
            "¿Qué conexiones existen con ClayOMICS y MAGNETIME?",
            LECTURA_CONEXIONES + "\n\n" + _texto_conexiones(respuestas["conexiones"]),
        ),
    ]
    for titulo, cuerpo in preguntas:
        with st.expander(titulo, expanded=False):
            st.write(cuerpo)


def _texto_enemigos(filas: list[dict]) -> str:
    if not filas:
        return "La base no documenta enemigos para esa plaga."
    return "\n".join(
        f"• {fila['nombre']} ({fila['cientifico']}), evidencia {fila['nivel']}, fuente {fila['cita']}."
        for fila in filas
    )


def _texto_niveles(filas: list[dict]) -> str:
    return "\n".join(
        f"• {fila['relacion']}: {fila['agente']} sobre {fila['plaga']}, nivel {fila['nivel']}, {fila['cita']}."
        for fila in filas
    )


def _texto_restricciones(filas: list[dict]) -> str:
    if not filas:
        return "No hay restricciones codificadas."
    return "\n".join(
        f"• {fila['relacion']} / {fila['codigo']}: {fila['descripcion']} "
        f"(fuentes {', '.join(fila['fuentes'])})."
        for fila in filas
    )


def _texto_conexiones(filas: list[dict]) -> str:
    return "\n".join(
        f"• {fila['plataforma']} ({fila['estado']}) en {fila['relacion']}: {fila['resultado']}"
        for fila in filas
    )


def pagina_inventario(gestor) -> None:
    """Tabla de las fuentes F01 a F17."""
    st.dataframe(gestor.listar_fuentes(), use_container_width=True, hide_index=True)
    st.caption("El rol «interoperabilidad» no es evidencia de eficacia de un agente.")


def pagina_acerca(gestor) -> None:
    """Reglas, motor y límite del prototipo."""
    st.markdown(
        """
        El sistema reifica cada recomendación como una **relación de biocontrol**:
        plaga, agente, ventana de uso, nivel de evidencia, restricciones y fuente.
        R1 recomienda solo con evidencia alta y clima dentro de la ventana.
        R2 baja la conclusión a potencial si la evidencia es media o baja.
        R3 declara una laguna cuando la base no tiene agente, bajo mundo cerrado local.
        R4 advierte si una práctica del cultivo coincide con una restricción, sin borrar la evidencia.
        R5 obliga a que toda conclusión cite la relación y su fuente.
        """
    )
    st.caption(
        f"Reglas SWRL cargadas en el OWL: {gestor.contar_reglas()}. "
        f"Java para Pellet: {'sí' if gestor.java_disponible() else 'no'}. "
        "La explicación de cada consulta la redacta el motor Python, que es auditable."
    )
    with st.expander("Reglas SWRL en sintaxis estándar"):
        st.code(gestor.texto_reglas(), language="text")


def main() -> None:
    """Compone la barra lateral y la página elegida."""
    inyectar_estilo()
    gestor = obtener_gestor()
    with st.sidebar:
        st.markdown(logo_svg(), unsafe_allow_html=True)
        st.markdown("### AgroTech UCaldas")
        st.markdown("Sistema experto de biocontrol")
        st.caption("Ingeniería del Conocimiento · cítricos")
        pagina = st.radio(
            "Sección",
            ["Consultar", "Preguntas de competencia", "Inventario de fuentes", "Cómo razona"],
            label_visibility="collapsed",
        )
        st.markdown("---")
        st.caption(PIE)

    st.markdown(
        """
        <div class="bio-banner">
          <div class="bio-kicker">Universidad de Caldas · Ingeniería del Conocimiento</div>
          <h1>Sistema experto de biocontrol</h1>
          <p>Plagas de cítricos, enemigos naturales y la evidencia que sostiene cada conclusión.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if pagina == "Consultar":
        pagina_consulta(gestor)
    elif pagina == "Preguntas de competencia":
        pagina_competencia(gestor)
    elif pagina == "Inventario de fuentes":
        pagina_inventario(gestor)
    else:
        pagina_acerca(gestor)

    st.markdown(f'<div class="bio-footer">{PIE}</div>', unsafe_allow_html=True)


main()
