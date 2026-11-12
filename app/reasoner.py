"""Motor de las reglas R1 a R5 y verificación opcional con Pellet.

Cada consulta se resuelve en Python para poder devolver el árbol de
explicación. Pellet sabe aplicar las reglas SWRL, pero no dice cuál
disparó ni por qué. Por eso la API explica con este módulo y Pellet
queda como comprobación, no como camino de cada clic.
"""

from __future__ import annotations

import logging
import shutil
from dataclasses import dataclass

from app.config import ADVERTENCIA, PESO_NIVEL
from app.ontology_manager import OntologyManager, RelacionVista, obtener_gestor
from app.schemas import ConsultaEntrada, ConsultaSalida, Explicacion, OtraRelacion, PasoRegla
from data.semilla import PRACTICAS

logger = logging.getLogger(__name__)

CATALOGO_PRACTICAS = dict(PRACTICAS)
REGLAS = (
    ("R1", "Aplicabilidad"),
    ("R2", "Precaución"),
    ("R3", "Laguna de conocimiento"),
    ("R4", "Incompatibilidad"),
    ("R5", "Trazabilidad"),
)
NOTA_R2 = (
    "Nota de precaución: la evidencia no es alta. Trate la sugerencia como "
    "una hipótesis de manejo y contrástela en campo antes de usarla."
)
LECTURA_CONEXIONES = (
    "MAGNETIME agrupa fuentes sobre tratamiento magnético de semillas de tomate "
    "(F13, tesis, nivel medio; F15, trabajo de grado, nivel medio) y de soja "
    "(F14, nivel alto). Ninguna está hecha en cítricos ni mide control de plagas: "
    "el inventario las marca como la evidencia que falta para el caso integrador. "
    "ClayOMICS aparece como noticia institucional de 2022 (F16, nivel medio) y "
    "como puente conceptual con la revisión de xenometabolómica del grupo de "
    "Cromatografía (F17, nivel alto). F17 no es un resultado del spin-off."
)


@dataclass
class Evaluacion:
    """Resultado de aplicar la ventana, el nivel y las restricciones a una relación."""

    relacion: RelacionVista
    temperatura_ok: bool
    humedad_ok: bool
    restricciones: list[str]
    elegible: bool
    puntaje: float | None
    ancho: float


def consultar(entrada: ConsultaEntrada, gestor: OntologyManager | None = None) -> ConsultaSalida:
    """Evalúa R1–R5 para una plaga, un clima y las prácticas declaradas."""
    gestor = gestor or obtener_gestor()
    practicas = _practicas_validas(entrada.practicas)
    plaga = gestor.resolver_plaga(entrada.plaga)
    if plaga is None:
        logger.info("Consulta sobre una plaga no registrada: %s", entrada.plaga)
        return _plaga_no_registrada()

    relaciones = gestor.relaciones_de(plaga.id)
    if not relaciones:
        logger.info("Laguna de conocimiento para %s.", plaga.id)
        return _laguna(plaga.nombre_cientifico, plaga.cultivos, plaga.descripcion)

    evaluaciones = [_evaluar(relacion, entrada, practicas) for relacion in relaciones]
    if not any(item.relacion.temp_min is not None for item in evaluaciones):
        logger.info("Relaciones sin ventana de uso para %s.", plaga.id)
        return _solo_documentados(plaga.nombre_cientifico, evaluaciones)
    elegibles = [item for item in evaluaciones if item.elegible]
    if not elegibles:
        logger.info("Sin ventana compatible para %s.", plaga.id)
        return _fuera_de_ventana(plaga.nombre_cientifico, entrada, evaluaciones)

    elegibles.sort(key=lambda item: (-(item.puntaje or 0), item.ancho, item.relacion.agente_nombre))
    return _conclusion(elegibles[0], evaluaciones, entrada)


def responder_competencia(gestor: OntologyManager | None = None) -> dict[str, object]:
    """Reúne las cinco preguntas de competencia en una sola estructura."""
    gestor = gestor or obtener_gestor()
    ejemplo = consultar(
        ConsultaEntrada(plaga="plaga_no_registrada", temperatura=25, humedad=70),
        gestor,
    )
    return {
        "enemigos_de_diaphorina_citri": gestor.enemigos_de("Diaphorina_citri"),
        "niveles_de_evidencia": gestor.niveles_de_evidencia(),
        "restricciones": gestor.restricciones_documentadas(),
        "lagunas": gestor.lagunas(),
        "respuesta_sin_agente": ejemplo.model_dump(),
        "conexiones": gestor.conexiones_externas(),
        "lectura_conexiones": LECTURA_CONEXIONES,
    }


def probar_pellet() -> dict[str, object]:
    """Comprueba R1 y R3 con Pellet en un mundo desechable.

    No se llama en cada consulta: tarda, escribe inferencias y no produce
    el texto de explicación. Si Java o Pellet fallan, el prototipo sigue
    respondiendo con el motor Python.
    """
    if shutil.which("java") is None:
        return {"disponible": False, "aplicado": False, "motivo": "Java no está en el PATH."}

    from owlready2 import OwlReadyJavaError, World, sync_reasoner_pellet

    from ontology.construir_ontologia import iri_archivo_owlready
    from app.config import RUTA_ONTOLOGIA

    mundo = World()
    try:
        onto = mundo.get_ontology(iri_archivo_owlready(RUTA_ONTOLOGIA)).load()
        with onto:
            consulta = onto.Consulta("Consulta_ejemplo_pellet")
            consulta.consultaPlaga = onto.Diaphorina_citri
            consulta.temperaturaActual = 25.0
            consulta.humedadActual = 70.0
        sync_reasoner_pellet(
            onto,
            infer_property_values=True,
            infer_data_property_values=True,
            debug=0,
        )
        recomendados = [item.name for item in _varios(onto.Tamarixia_radiata.altamenteRecomendadoPara)]
        lagunas = [item.name for item in _varios(onto.Compsus_sp.tieneLagunaEn)]
        return {
            "disponible": True,
            "aplicado": True,
            "r1_tamarixia": "Diaphorina_citri" in recomendados,
            "r3_sin_laguna_en_la_semilla": len(lagunas) == 0,
        }
    except (OwlReadyJavaError, OSError, Exception) as exc:
        motivo = _motivo_pellet(exc)
        logger.warning("Pellet no aplicó las reglas: %s", motivo)
        return {"disponible": True, "aplicado": False, "motivo": motivo}
    finally:
        mundo.close()


def _practicas_validas(practicas: list[str]) -> list[str]:
    validas: list[str] = []
    for practica in practicas:
        codigo = practica.strip()
        if codigo in {"", "ninguna"}:
            continue
        if codigo not in CATALOGO_PRACTICAS:
            logger.warning("Práctica no catalogada, se ignora: %s", codigo)
            continue
        if codigo not in validas:
            validas.append(codigo)
    return validas


def _evaluar(relacion: RelacionVista, entrada: ConsultaEntrada, practicas: list[str]) -> Evaluacion:
    """Decide si la relación es aplicable y con qué prioridad.

    Sin ventana térmica la relación queda documentada, pero no compite.
    La humedad solo filtra cuando la fuente la marca como umbral.
    """
    sin_ventana = relacion.temp_min is None or relacion.temp_max is None
    temperatura_ok = (
        not sin_ventana and relacion.temp_min <= entrada.temperatura <= relacion.temp_max
    )
    if relacion.humedad_decide and relacion.hum_min is not None and relacion.hum_max is not None:
        humedad_ok = relacion.hum_min <= entrada.humedad <= relacion.hum_max
    else:
        humedad_ok = True
    restricciones = [
        restriccion.etiqueta
        for restriccion in relacion.restricciones
        if restriccion.codigo in practicas
    ]
    elegible = (not sin_ventana) and temperatura_ok and humedad_ok and relacion.nivel in {"Alta", "Media", "Baja"}
    puntaje = None
    if elegible:
        puntaje = float(PESO_NIVEL[relacion.nivel] - (1 if restricciones else 0))
    if sin_ventana:
        ancho = 10_000.0
    elif relacion.humedad_decide and relacion.hum_min is not None and relacion.hum_max is not None:
        ancho = (relacion.temp_max - relacion.temp_min) + (relacion.hum_max - relacion.hum_min)
    else:
        ancho = relacion.temp_max - relacion.temp_min
    return Evaluacion(
        relacion=relacion,
        temperatura_ok=temperatura_ok,
        humedad_ok=humedad_ok,
        restricciones=restricciones,
        elegible=elegible,
        puntaje=puntaje,
        ancho=ancho,
    )


def _conclusion(
    ganadora: Evaluacion,
    evaluaciones: list[Evaluacion],
    entrada: ConsultaEntrada,
) -> ConsultaSalida:
    """Arma la recomendación principal y marca qué reglas se activaron."""
    relacion = ganadora.relacion
    alta = relacion.nivel == "Alta"
    activas = ["R1" if alta else "R2"]
    if ganadora.restricciones:
        activas.append("R4")
    activas.append("R5")
    inactivas = [codigo for codigo, _nombre in REGLAS if codigo not in activas]

    temperatura = _numero(entrada.temperatura)
    humedad = _numero(entrada.humedad)
    if alta:
        nucleo = _frase_clima(relacion, temperatura, humedad)
        nucleo += (
            f" La evidencia es Alta, así que {relacion.agente_nombre} queda altamente "
            f"recomendado para la plaga consultada."
        )
        nota = None
        recomendacion = "AltamenteRecomendado"
    else:
        nucleo = _frase_clima(relacion, temperatura, humedad)
        nucleo += (
            f" La evidencia es {relacion.nivel}. "
            f"Se activa R2: la recomendación es potencial, no alta."
        )
        nota = f"{NOTA_R2} {relacion.criterio_nivel}"
        recomendacion = "PotencialmenteRecomendado"

    otras = [_otra(item, item is not ganadora) for item in evaluaciones if item is not ganadora]
    if otras:
        aplicables = [item.agente for item in otras if item.aplicable]
        if aplicables:
            nucleo += " También es aplicable " + ", ".join(aplicables) + ", con menor prioridad."
    nucleo += f" La conclusión arrastra {relacion.id} y la fuente {relacion.fuente_principal} (R5)."
    if ganadora.restricciones:
        nucleo += (
            " R4 está activa: "
            + "; ".join(ganadora.restricciones)
            + ". La evidencia no se anula, pero no conviene usar el agente mientras esa práctica siga vigente."
        )

    arbol = _arbol(
        activas=set(activas),
        r1=nucleo if alta else "La evidencia de la relación elegida no es Alta.",
        r2=nota or "La evidencia de la relación elegida no es Media ni Baja.",
        r3="La plaga tiene al menos un agente documentado en la base.",
        r4=(
            "Coincide una práctica declarada: " + "; ".join(ganadora.restricciones)
            if ganadora.restricciones
            else "Ninguna práctica declarada coincide con una restricción de la relación elegida."
        ),
        r5=f"La conclusión cita {relacion.id} y {relacion.fuente_principal}.",
    )
    logger.info(
        "Consulta %s a %s °C y %s %% HR -> %s (%s).",
        relacion.plaga_id,
        temperatura,
        humedad,
        recomendacion,
        relacion.agente_nombre,
    )
    return ConsultaSalida(
        recomendacion=recomendacion,
        agente=relacion.agente_nombre,
        nivel_evidencia=relacion.nivel,
        condiciones=_condiciones(relacion),
        fuente=relacion.fuente_principal,
        explicacion=Explicacion(
            reglas_activadas=activas,
            reglas_no_activadas=inactivas,
            justificacion=nucleo,
            arbol=arbol,
            otras_relaciones=otras,
        ),
        advertencia=ADVERTENCIA,
        reglas_activadas=activas,
        alternativas=[item for item in otras if item.aplicable],
        restricciones_activas=ganadora.restricciones,
        nota_precaucion=nota,
        motor="python",
        trazabilidad={"relacion": relacion.id, "fuente": relacion.fuente_principal},
    )


def _otra(evaluacion: Evaluacion, _distinta: bool) -> OtraRelacion:
    relacion = evaluacion.relacion
    if relacion.temp_min is None:
        return OtraRelacion(
            relacion=relacion.id,
            agente=relacion.agente_nombre,
            nivel_evidencia=relacion.nivel,
            aplicable=False,
            reglas=[],
            motivo="Documentado sin ventana de uso. " + relacion.criterio_nivel,
        )
    if not evaluacion.temperatura_ok or not evaluacion.humedad_ok:
        motivo = _motivo_ventana(evaluacion)
        reglas: list[str] = []
    elif relacion.nivel == "Alta":
        motivo = "Aplicable con evidencia Alta, pero otra relación tuvo mayor prioridad."
        reglas = ["R1", "R5"]
    else:
        motivo = f"Aplicable con evidencia {relacion.nivel}; corresponde la precaución R2."
        reglas = ["R2", "R5"]
    if evaluacion.restricciones:
        reglas.append("R4")
        motivo += " Tiene una restricción activa: " + "; ".join(evaluacion.restricciones) + "."
    return OtraRelacion(
        relacion=relacion.id,
        agente=relacion.agente_nombre,
        nivel_evidencia=relacion.nivel,
        aplicable=evaluacion.elegible,
        reglas=reglas,
        motivo=motivo,
    )


def _condiciones(relacion: RelacionVista) -> dict[str, list[float]]:
    """Publica la temperatura que decide y, aparte, la humedad de ensayo."""
    datos: dict[str, list[float]] = {
        "temperatura": [_numero(relacion.temp_min), _numero(relacion.temp_max)],
    }
    if relacion.hum_min is None or relacion.hum_max is None:
        return datos
    clave = "humedad" if relacion.humedad_decide else "humedad_ensayo"
    datos[clave] = [_numero(relacion.hum_min), _numero(relacion.hum_max)]
    return datos


def _frase_clima(relacion: RelacionVista, temperatura: float, humedad: float) -> str:
    frase = (
        f"La temperatura {temperatura} °C está en el rango "
        f"[{_numero(relacion.temp_min)}, {_numero(relacion.temp_max)}]"
    )
    if relacion.humedad_decide and relacion.hum_min is not None and relacion.hum_max is not None:
        frase += (
            f" y la humedad {humedad} % está en el rango "
            f"[{_numero(relacion.hum_min)}, {_numero(relacion.hum_max)}]"
        )
    elif relacion.hum_min is not None and relacion.hum_max is not None:
        frase += (
            f". La humedad consultada ({humedad} %) no decide: la fuente solo reporta "
            f"una condición de ensayo ({_numero(relacion.hum_min)}–{_numero(relacion.hum_max)} % HR)"
        )
    return frase + "."


def _solo_documentados(nombre_plaga: str, evaluaciones: list[Evaluacion]) -> ConsultaSalida:
    """Muestra el hecho documentado cuando ninguna fuente trae ventana de uso."""
    ordenadas = sorted(
        evaluaciones,
        key=lambda item: (-PESO_NIVEL[item.relacion.nivel], item.relacion.agente_nombre),
    )
    relacion = ordenadas[0].relacion
    otras = [_otra(item, True) for item in ordenadas if item.relacion is not relacion]
    justificacion = (
        f"{nombre_plaga} tiene enemigos documentados, pero ninguna fuente trae una ventana "
        f"de temperatura o humedad para decidir la aplicación. Se muestra {relacion.agente_nombre} "
        f"({relacion.fuente_principal}) sin activar R1 ni R2. {relacion.criterio_nivel}"
    )
    logger.info("Consulta %s sin ventana de uso -> %s.", relacion.plaga_id, relacion.agente_nombre)
    return ConsultaSalida(
        recomendacion="Documentado sin ventana de uso",
        agente=relacion.agente_nombre,
        nivel_evidencia=relacion.nivel,
        fuente=relacion.fuente_principal,
        explicacion=Explicacion(
            reglas_activadas=["R5"],
            reglas_no_activadas=["R1", "R2", "R3", "R4"],
            justificacion=justificacion,
            arbol=_arbol(
                activas={"R5"},
                r1="No hay una ventana de temperatura documentada, así que R1 no dispara.",
                r2="Sin ventana, una evidencia Media o Baja no se convierte en recomendación potencial.",
                r3="La plaga sí tiene agentes documentados.",
                r4="Sin recomendación climática, la incompatibilidad no cambia la conclusión.",
                r5=f"La ficha cita {relacion.id} y {relacion.fuente_principal}.",
            ),
            otras_relaciones=otras,
        ),
        advertencia=ADVERTENCIA,
        reglas_activadas=["R5"],
        motor="python",
        trazabilidad={"relacion": relacion.id, "fuente": relacion.fuente_principal},
    )


def _motivo_ventana(evaluacion: Evaluacion) -> str:
    relacion = evaluacion.relacion
    if relacion.temp_min is None or relacion.temp_max is None:
        return "Sin ventana de uso documentada."
    fallos = []
    if not evaluacion.temperatura_ok:
        fallos.append(
            f"temperatura fuera de [{_numero(relacion.temp_min)}, {_numero(relacion.temp_max)}] °C"
        )
    if not evaluacion.humedad_ok:
        fallos.append(
            f"humedad fuera de [{_numero(relacion.hum_min)}, {_numero(relacion.hum_max)}] %"
        )
    return "No aplica: " + " y ".join(fallos) + "."


def _fuera_de_ventana(
    nombre_plaga: str,
    entrada: ConsultaEntrada,
    evaluaciones: list[Evaluacion],
) -> ConsultaSalida:
    detalles = " ".join(
        f"{item.relacion.agente_nombre}: {_motivo_ventana(item)}" for item in evaluaciones
    )
    justificacion = (
        f"Ninguna relación documentada para {nombre_plaga} contiene la consulta "
        f"({_numero(entrada.temperatura)} °C, {_numero(entrada.humedad)} % HR). "
        "No se activa R3 porque sí hay agentes en la base; lo que falla es la ventana de uso. "
        + detalles
    )
    return ConsultaSalida(
        recomendacion="Condiciones no satisfechas",
        explicacion=Explicacion(
            reglas_activadas=[],
            reglas_no_activadas=[codigo for codigo, _nombre in REGLAS],
            justificacion=justificacion,
            arbol=_arbol(
                activas=set(),
                r1="Ninguna relación de evidencia Alta contiene el clima consultado.",
                r2="Ninguna relación de evidencia Media o Baja contiene el clima consultado.",
                r3="La plaga sí tiene agentes documentados.",
                r4="Sin relación aplicable, la incompatibilidad no cambia la conclusión.",
                r5="No hay conclusión recomendada a la cual arrastrar una fuente.",
            ),
            otras_relaciones=[_otra(item, True) for item in evaluaciones],
        ),
        advertencia=ADVERTENCIA,
        reglas_activadas=[],
        motor="python",
    )


def _laguna(nombre_plaga: str, cultivos: list[str], descripcion: str) -> ConsultaSalida:
    cultivos_texto = ", ".join(cultivos) if cultivos else "los cultivos declarados"
    justificacion = (
        f"{nombre_plaga} afecta a {cultivos_texto} y la base no registra ningún agente "
        f"de biocontrol para esta plaga. Se activa R3: laguna de conocimiento. "
        f"{descripcion}"
    )
    return _insuficiente(justificacion, r3=justificacion)


def _plaga_no_registrada() -> ConsultaSalida:
    justificacion = (
        "La plaga consultada no está registrada en la base actual. "
        "Se activa R3: laguna de conocimiento."
    )
    return _insuficiente(
        justificacion,
        r3="No hay un individuo de Plaga con el nombre consultado, así que tampoco hay un agente documentado.",
    )


def _insuficiente(justificacion: str, r3: str) -> ConsultaSalida:
    activas = ["R3"]
    return ConsultaSalida(
        recomendacion="Evidencia insuficiente",
        explicacion=Explicacion(
            reglas_activadas=activas,
            reglas_no_activadas=["R1", "R2", "R4", "R5"],
            justificacion=justificacion,
            arbol=_arbol(
                activas={"R3"},
                r1="No hay una relación con evidencia Alta que evaluar.",
                r2="No hay una relación con evidencia Media o Baja que evaluar.",
                r3=r3,
                r4="Sin relación documentada, no hay una restricción que pueda activarse.",
                r5="La laguna no tiene una relación R ni una fuente F que arrastrar.",
            ),
        ),
        advertencia=ADVERTENCIA,
        reglas_activadas=activas,
        motor="python",
    )


def _arbol(
    activas: set[str],
    r1: str,
    r2: str,
    r3: str,
    r4: str,
    r5: str,
) -> list[PasoRegla]:
    detalles = {"R1": r1, "R2": r2, "R3": r3, "R4": r4, "R5": r5}
    return [
        PasoRegla(codigo=codigo, nombre=nombre, activada=codigo in activas, detalle=detalles[codigo])
        for codigo, nombre in REGLAS
    ]


def _numero(valor: float) -> int | float:
    if float(valor).is_integer():
        return int(valor)
    return round(float(valor), 2)


def _motivo_pellet(exc: Exception) -> str:
    """Traduce el fallo de Java a una causa usable en el informe."""
    texto = str(exc)
    if "UnsupportedClassVersionError" in texto or "class file version" in texto:
        return (
            "El Pellet incluido en Owlready2 0.51 necesita Java 25 o superior. "
            "Con un Java más antiguo las reglas siguen cargadas en el OWL, "
            "pero cada consulta se explica con el motor Python."
        )
    primera = texto.strip().splitlines()[0] if texto.strip() else "Fallo de Pellet."
    return primera[:500]


def _varios(valor: object) -> list:
    if valor is None:
        return []
    if isinstance(valor, (list, tuple)):
        return list(valor)
    return [valor]
