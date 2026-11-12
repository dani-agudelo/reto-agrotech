"""Genera la ontología, el Turtle y el inventario CSV desde la semilla.

La caja de conocimiento se escribe con RDFLib para que el Turtle quede
legible. Después Owlready2 carga ese OWL, inserta las reglas SWRL y lo
vuelve a guardar. Si Pellet o el cargador de reglas fallan, el archivo
OWL de clases e individuos permanece usable y el motor Python responde
las consultas.
"""

from __future__ import annotations

import argparse
import csv
import logging
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import OWL, RDF, RDFS, XSD

from app.config import IRI, NS, RUTA_FUENTES, RUTA_INSTANCIAS, RUTA_ONTOLOGIA, RUTA_REGLAS
from data.semilla import (
    AGENTES,
    ANALISIS,
    CONDICIONES,
    CULTIVOS,
    EXPERIMENTOS,
    FUENTES,
    PLAGAS,
    PLATAFORMAS,
    RELACIONES,
    RESTRICCIONES,
    validar_semilla,
)

logger = logging.getLogger(__name__)

BIO = Namespace(NS)
ONTOLOGIA = URIRef(IRI)

CLASES = {
    "Cultivo": "Cultivo de cítricos hospedero de la plaga.",
    "Plaga": "Organismo que afecta al menos un cultivo del inventario.",
    "AgenteBiocontrol": "Enemigo natural o microorganismo de control documentado.",
    "CondicionUso": "Ventana de temperatura documentada. La humedad solo decide si la fuente la marca como umbral.",
    "FuenteEvidencia": "Publicación, tesis o nota que respalda o contextualiza un hecho.",
    "RelacionBiocontrol": "Relación reificada entre plaga, agente, condición, evidencia y restricciones.",
    "AnalisisQuimico": "Análisis químico, medido o propuesto, articulado con una plataforma.",
    "Experimento": "Experimento, medido o propuesto, articulado con una plataforma.",
    "Restriccion": "Práctica agronómica que compromete el uso de un agente.",
    "PlataformaExterna": "Plataforma de la Universidad de Caldas enlazada por interoperabilidad.",
    "Consulta": "Hechos temporales de una pregunta: plaga, clima y prácticas.",
    "PlagaSinAgenteDocumentado": "Cierre de mundo local: la plaga no tiene agente en esta base.",
    "RestriccionActiva": "Estado inferido cuando una práctica de la consulta coincide con una restricción.",
}

PROPIEDADES_OBJETO = {
    "afectaA": ("Plaga", "Cultivo", False),
    "esControladaPor": ("Plaga", "AgenteBiocontrol", False),
    "tieneCondicion": ("RelacionBiocontrol", "CondicionUso", True),
    "respaldadoPor": ("RelacionBiocontrol", "FuenteEvidencia", False),
    "tieneRestriccion": ("RelacionBiocontrol", "Restriccion", False),
    "verificadoPor": ("RelacionBiocontrol", "AnalisisQuimico", False),
    "tieneExperimento": ("RelacionBiocontrol", "Experimento", False),
    "involucraPlaga": ("RelacionBiocontrol", "Plaga", True),
    "involucraAgente": ("RelacionBiocontrol", "AgenteBiocontrol", True),
    "fuentePrincipal": ("RelacionBiocontrol", "FuenteEvidencia", True),
    "justificadoPor": ("Restriccion", "FuenteEvidencia", False),
    "contextualizadoPor": ("Plaga", "FuenteEvidencia", False),
    "articuladoCon": (None, "PlataformaExterna", True),
    "documentadoEn": (None, "FuenteEvidencia", True),
    "consultaPlaga": ("Consulta", "Plaga", True),
    "altamenteRecomendadoPara": ("AgenteBiocontrol", "Plaga", False),
    "potencialmenteRecomendadoPara": ("AgenteBiocontrol", "Plaga", False),
    "tieneLagunaEn": ("Plaga", "Cultivo", False),
    "trazadoPor": (None, "FuenteEvidencia", False),
}

DATOS_FUNCIONALES = (
    "nombreComun",
    "nombreCientifico",
    "descripcion",
    "tipoAgente",
    "autores",
    "anio",
    "titulo",
    "tipoFuente",
    "iniciativa",
    "nivelConfiabilidad",
    "naturaleza",
    "acceso",
    "fechaConsulta",
    "informacionExtraida",
    "alcance",
    "doi",
    "url",
    "citaCorta",
    "notas",
    "tieneNivelEvidencia",
    "temperaturaMin",
    "temperaturaMax",
    "humedadMin",
    "humedadMax",
    "estadoVentanaHumedad",
    "rangoMin",
    "rangoMax",
    "rangoValido",
    "descripcionCondicion",
    "variableRespuesta",
    "condicionExperimental",
    "resultado",
    "criterioNivel",
    "codigoPractica",
    "etiqueta",
    "estadoEnlace",
    "tipoPlataforma",
    "temperaturaActual",
    "humedadActual",
)

ENTEROS = {"anio"}
DECIMALES = {
    "temperaturaMin",
    "temperaturaMax",
    "humedadMin",
    "humedadMax",
    "rangoMin",
    "rangoMax",
    "temperaturaActual",
    "humedadActual",
}
CONTROLADOS = {"tieneNivelEvidencia", "estadoEnlace", "estadoVentanaHumedad", "nivelConfiabilidad"}


def _configurar_registro() -> None:
    """Evita un logging básico repetido si la aplicación ya lo configuró."""
    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        )


def _texto(valor: str, idioma: str = "es") -> Literal:
    return Literal(valor, lang=idioma)


def _controlado(valor: str) -> Literal:
    return Literal(valor, datatype=XSD.string)


def _decimal(valor: float) -> Literal:
    return Literal(f"{valor:g}", datatype=XSD.decimal)


def _entero(valor: int) -> Literal:
    return Literal(valor, datatype=XSD.integer)


def construir_grafo() -> Graph:
    """Arma el grafo RDF de clases, propiedades e individuos semilla."""
    validar_semilla()
    grafo = Graph()
    grafo.bind("bio", BIO)
    grafo.bind("owl", OWL)
    grafo.add((ONTOLOGIA, RDF.type, OWL.Ontology))
    grafo.add((
        ONTOLOGIA,
        RDFS.comment,
        _texto(
            "Ontología de biocontrol de plagas de cítricos. Prototipo académico "
            "AgroTech, Universidad de Caldas. No es una prescripción agronómica."
        ),
    ))

    for nombre, comentario in CLASES.items():
        clase = BIO[nombre]
        grafo.add((clase, RDF.type, OWL.Class))
        grafo.add((clase, RDFS.label, _texto(nombre)))
        grafo.add((clase, RDFS.comment, _texto(comentario)))
    grafo.add((BIO.PlagaSinAgenteDocumentado, RDFS.subClassOf, BIO.Plaga))

    for nombre, (dominio, rango, funcional) in PROPIEDADES_OBJETO.items():
        prop = BIO[nombre]
        grafo.add((prop, RDF.type, OWL.ObjectProperty))
        grafo.add((prop, RDFS.label, _texto(nombre)))
        if dominio:
            grafo.add((prop, RDFS.domain, BIO[dominio]))
        if rango:
            grafo.add((prop, RDFS.range, BIO[rango]))
        if funcional:
            grafo.add((prop, RDF.type, OWL.FunctionalProperty))

    for nombre in DATOS_FUNCIONALES:
        prop = BIO[nombre]
        grafo.add((prop, RDF.type, OWL.DatatypeProperty))
        grafo.add((prop, RDF.type, OWL.FunctionalProperty))
        grafo.add((prop, RDFS.label, _texto(nombre)))
        if nombre in ENTEROS:
            grafo.add((prop, RDFS.range, XSD.integer))
        elif nombre in DECIMALES:
            grafo.add((prop, RDFS.range, XSD.decimal))
        elif nombre in CONTROLADOS:
            grafo.add((prop, RDFS.range, XSD.string))
    grafo.add((BIO.declaraPractica, RDF.type, OWL.DatatypeProperty))
    grafo.add((BIO.declaraPractica, RDFS.label, _texto("declaraPractica")))

    _agregar_individuos(grafo)
    return grafo


def _agregar(grafo: Graph, sujeto: str, predicado: str, objeto: Literal | URIRef) -> None:
    grafo.add((BIO[sujeto], BIO[predicado], objeto))


def _agregar_individuos(grafo: Graph) -> None:
    """Carga cultivos, plagas, agentes, condiciones, fuentes y relaciones."""
    for cultivo in CULTIVOS:
        grafo.add((BIO[cultivo.id], RDF.type, BIO.Cultivo))
        grafo.add((BIO[cultivo.id], RDFS.label, _texto(cultivo.nombre_comun)))
        _agregar(grafo, cultivo.id, "nombreComun", _texto(cultivo.nombre_comun))
        _agregar(grafo, cultivo.id, "nombreCientifico", Literal(cultivo.nombre_cientifico))
        _agregar(grafo, cultivo.id, "descripcion", _texto(cultivo.descripcion))

    for fuente in FUENTES:
        grafo.add((BIO[fuente.id], RDF.type, BIO.FuenteEvidencia))
        grafo.add((BIO[fuente.id], RDFS.label, Literal(fuente.cita_corta)))
        _agregar(grafo, fuente.id, "citaCorta", Literal(fuente.cita_corta))
        _agregar(grafo, fuente.id, "autores", Literal(fuente.autores))
        _agregar(grafo, fuente.id, "titulo", Literal(fuente.titulo))
        _agregar(grafo, fuente.id, "tipoFuente", Literal(fuente.tipo))
        _agregar(grafo, fuente.id, "iniciativa", Literal(fuente.iniciativa))
        _agregar(grafo, fuente.id, "nivelConfiabilidad", _controlado(fuente.nivel))
        _agregar(grafo, fuente.id, "naturaleza", Literal(fuente.naturaleza))
        _agregar(grafo, fuente.id, "acceso", Literal(fuente.acceso))
        _agregar(grafo, fuente.id, "fechaConsulta", Literal(fuente.fecha_consulta))
        _agregar(grafo, fuente.id, "informacionExtraida", _texto(fuente.informacion_extraida))
        _agregar(grafo, fuente.id, "alcance", _texto(fuente.alcance))
        _agregar(grafo, fuente.id, "notas", _texto(fuente.alcance))
        if fuente.anio is not None:
            _agregar(grafo, fuente.id, "anio", _entero(fuente.anio))
        if fuente.doi:
            _agregar(grafo, fuente.id, "doi", Literal(fuente.doi))
        if fuente.url:
            _agregar(grafo, fuente.id, "url", Literal(fuente.url))

    plagas_con_agente = {relacion.plaga_id for relacion in RELACIONES}
    for plaga in PLAGAS:
        grafo.add((BIO[plaga.id], RDF.type, BIO.Plaga))
        if plaga.id not in plagas_con_agente:
            grafo.add((BIO[plaga.id], RDF.type, BIO.PlagaSinAgenteDocumentado))
        grafo.add((BIO[plaga.id], RDFS.label, _texto(plaga.nombre_comun)))
        _agregar(grafo, plaga.id, "nombreComun", _texto(plaga.nombre_comun))
        _agregar(grafo, plaga.id, "nombreCientifico", Literal(plaga.nombre_cientifico))
        _agregar(grafo, plaga.id, "descripcion", _texto(plaga.descripcion))
        for cultivo_id in plaga.cultivos:
            _agregar(grafo, plaga.id, "afectaA", BIO[cultivo_id])
        for fuente_id in plaga.contexto:
            _agregar(grafo, plaga.id, "contextualizadoPor", BIO[fuente_id])

    for agente in AGENTES:
        grafo.add((BIO[agente.id], RDF.type, BIO.AgenteBiocontrol))
        grafo.add((BIO[agente.id], RDFS.label, Literal(agente.nombre_comun)))
        _agregar(grafo, agente.id, "nombreComun", Literal(agente.nombre_comun))
        _agregar(grafo, agente.id, "nombreCientifico", Literal(agente.nombre_cientifico))
        _agregar(grafo, agente.id, "tipoAgente", Literal(agente.tipo))
        _agregar(grafo, agente.id, "descripcion", _texto(agente.descripcion))

    for condicion in CONDICIONES:
        grafo.add((BIO[condicion.id], RDF.type, BIO.CondicionUso))
        if condicion.hum_min is not None and condicion.hum_max is not None and condicion.humedad_decide:
            ventana = (
                f"{condicion.temp_min:g}–{condicion.temp_max:g} °C; "
                f"{condicion.hum_min:g}–{condicion.hum_max:g} % HR"
            )
        elif condicion.hum_min is not None and condicion.hum_max is not None:
            ventana = (
                f"{condicion.temp_min:g}–{condicion.temp_max:g} °C; "
                f"HR de ensayo {condicion.hum_min:g}–{condicion.hum_max:g} % (no decide)"
            )
        else:
            ventana = f"{condicion.temp_min:g}–{condicion.temp_max:g} °C"
        grafo.add((BIO[condicion.id], RDFS.label, Literal(ventana)))
        _agregar(grafo, condicion.id, "temperaturaMin", _decimal(condicion.temp_min))
        _agregar(grafo, condicion.id, "temperaturaMax", _decimal(condicion.temp_max))
        if condicion.hum_min is not None and condicion.hum_max is not None:
            _agregar(grafo, condicion.id, "humedadMin", _decimal(condicion.hum_min))
            _agregar(grafo, condicion.id, "humedadMax", _decimal(condicion.hum_max))
            estado_humedad = "documentada" if condicion.humedad_decide else "ensayo"
            _agregar(grafo, condicion.id, "estadoVentanaHumedad", _controlado(estado_humedad))
        _agregar(grafo, condicion.id, "rangoMin", _decimal(condicion.temp_min))
        _agregar(grafo, condicion.id, "rangoMax", _decimal(condicion.temp_max))
        _agregar(grafo, condicion.id, "rangoValido", Literal(ventana))
        _agregar(grafo, condicion.id, "descripcionCondicion", _texto(condicion.descripcion))

    for restriccion in RESTRICCIONES:
        grafo.add((BIO[restriccion.id], RDF.type, BIO.Restriccion))
        grafo.add((BIO[restriccion.id], RDFS.label, _texto(restriccion.etiqueta)))
        _agregar(grafo, restriccion.id, "etiqueta", _texto(restriccion.etiqueta))
        _agregar(grafo, restriccion.id, "codigoPractica", Literal(restriccion.codigo_practica))
        _agregar(grafo, restriccion.id, "descripcion", _texto(restriccion.descripcion))
        for fuente_id in restriccion.fuentes:
            _agregar(grafo, restriccion.id, "justificadoPor", BIO[fuente_id])

    for plataforma in PLATAFORMAS:
        grafo.add((BIO[plataforma.id], RDF.type, BIO.PlataformaExterna))
        grafo.add((BIO[plataforma.id], RDFS.label, Literal(plataforma.etiqueta)))
        _agregar(grafo, plataforma.id, "etiqueta", Literal(plataforma.etiqueta))
        _agregar(grafo, plataforma.id, "tipoPlataforma", Literal(plataforma.tipo))
        _agregar(grafo, plataforma.id, "descripcion", _texto(plataforma.descripcion))
        _agregar(grafo, plataforma.id, "url", Literal(plataforma.url))

    for analisis in ANALISIS:
        grafo.add((BIO[analisis.id], RDF.type, BIO.AnalisisQuimico))
        grafo.add((BIO[analisis.id], RDFS.label, _texto(analisis.etiqueta)))
        _agregar(grafo, analisis.id, "etiqueta", _texto(analisis.etiqueta))
        _agregar(grafo, analisis.id, "estadoEnlace", _controlado(analisis.estado))
        _agregar(grafo, analisis.id, "variableRespuesta", _texto(analisis.variable_respuesta))
        _agregar(grafo, analisis.id, "condicionExperimental", _texto(analisis.condicion_experimental))
        _agregar(grafo, analisis.id, "resultado", _texto(analisis.resultado))
        _agregar(grafo, analisis.id, "articuladoCon", BIO[analisis.plataforma_id])
        _agregar(grafo, analisis.id, "documentadoEn", BIO[analisis.fuente_id])

    for experimento in EXPERIMENTOS:
        grafo.add((BIO[experimento.id], RDF.type, BIO.Experimento))
        grafo.add((BIO[experimento.id], RDFS.label, _texto(experimento.etiqueta)))
        _agregar(grafo, experimento.id, "etiqueta", _texto(experimento.etiqueta))
        _agregar(grafo, experimento.id, "estadoEnlace", _controlado(experimento.estado))
        _agregar(grafo, experimento.id, "variableRespuesta", _texto(experimento.variable_respuesta))
        _agregar(grafo, experimento.id, "condicionExperimental", _texto(experimento.condicion_experimental))
        _agregar(grafo, experimento.id, "resultado", _texto(experimento.resultado))
        _agregar(grafo, experimento.id, "articuladoCon", BIO[experimento.plataforma_id])
        _agregar(grafo, experimento.id, "documentadoEn", BIO[experimento.fuente_id])

    for relacion in RELACIONES:
        grafo.add((BIO[relacion.id], RDF.type, BIO.RelacionBiocontrol))
        grafo.add((BIO[relacion.id], RDFS.label, Literal(relacion.id)))
        _agregar(grafo, relacion.id, "involucraPlaga", BIO[relacion.plaga_id])
        _agregar(grafo, relacion.id, "involucraAgente", BIO[relacion.agente_id])
        _agregar(grafo, relacion.plaga_id, "esControladaPor", BIO[relacion.agente_id])
        if relacion.condicion_id is not None:
            _agregar(grafo, relacion.id, "tieneCondicion", BIO[relacion.condicion_id])
        _agregar(grafo, relacion.id, "fuentePrincipal", BIO[relacion.fuente_principal_id])
        _agregar(grafo, relacion.id, "tieneNivelEvidencia", _controlado(relacion.nivel))
        _agregar(grafo, relacion.id, "variableRespuesta", _texto(relacion.variable_respuesta))
        _agregar(grafo, relacion.id, "resultado", _texto(relacion.resultado))
        _agregar(grafo, relacion.id, "condicionExperimental", _texto(relacion.condicion_experimental))
        _agregar(grafo, relacion.id, "criterioNivel", _texto(relacion.criterio_nivel))
        for fuente_id in relacion.fuentes_ids:
            _agregar(grafo, relacion.id, "respaldadoPor", BIO[fuente_id])
        for restriccion_id in relacion.restricciones_ids:
            _agregar(grafo, relacion.id, "tieneRestriccion", BIO[restriccion_id])
        for analisis_id in relacion.analisis_ids:
            _agregar(grafo, relacion.id, "verificadoPor", BIO[analisis_id])
        for experimento_id in relacion.experimento_ids:
            _agregar(grafo, relacion.id, "tieneExperimento", BIO[experimento_id])


def escribir_csv() -> None:
    """Exporta F01–F17 a CSV para el inventario que lee la interfaz."""
    RUTA_FUENTES.parent.mkdir(parents=True, exist_ok=True)
    with RUTA_FUENTES.open("w", encoding="utf-8-sig", newline="") as archivo:
        escritor = csv.DictWriter(
            archivo,
            fieldnames=[
                "codigo",
                "autores",
                "anio",
                "titulo",
                "tipo",
                "iniciativa",
                "nivel",
                "naturaleza",
                "cita_corta",
                "doi",
                "url",
                "acceso",
                "informacion_extraida",
                "alcance",
            ],
        )
        escritor.writeheader()
        for fuente in FUENTES:
            escritor.writerow({
                "codigo": fuente.id,
                "autores": fuente.autores,
                "anio": "" if fuente.anio is None else fuente.anio,
                "titulo": fuente.titulo,
                "tipo": fuente.tipo,
                "iniciativa": fuente.iniciativa,
                "nivel": fuente.nivel,
                "naturaleza": fuente.naturaleza,
                "cita_corta": fuente.cita_corta,
                "doi": fuente.doi,
                "url": fuente.url,
                "acceso": fuente.acceso,
                "informacion_extraida": fuente.informacion_extraida,
                "alcance": fuente.alcance,
            })


def escribir_turtle(grafo: Graph) -> None:
    """Guarda el grafo en Turtle con un encabezado legible para el informe."""
    RUTA_INSTANCIAS.parent.mkdir(parents=True, exist_ok=True)
    cuerpo = grafo.serialize(format="turtle")
    encabezado = (
        "# Instancias y esquema del prototipo AgroTech Biocontrol.\n"
        "# Generado desde data/semilla.py. Regenerar con:\n"
        "#   python -m ontology.construir_ontologia\n"
        "# Inventario F01–F17 tomado de data/inventario_fuentes.tex.\n"
        "# La humedad de un ensayo no se usa como umbral si la ficha no la documenta.\n\n"
    )
    RUTA_INSTANCIAS.write_text(encabezado + cuerpo, encoding="utf-8")


def _reglas_desde_archivo(ruta: Path) -> list[tuple[str, str]]:
    """Lee rules.swrl y devuelve (nombre, regla en sintaxis Owlready2)."""
    nombre = None
    lineas: list[str] = []
    bloques: list[tuple[str, str]] = []
    for cruda in ruta.read_text(encoding="utf-8").splitlines():
        linea = cruda.strip()
        if not linea or linea.startswith("#"):
            continue
        coincidencia = re.match(r"^(R\d[\w]*)\s*:\s*$", linea)
        if coincidencia:
            if nombre and lineas:
                bloques.append((nombre, " ".join(lineas)))
            nombre = coincidencia.group(1)
            lineas = []
            continue
        lineas.append(linea)
    if nombre and lineas:
        bloques.append((nombre, " ".join(lineas)))

    traducidas = []
    for nombre_regla, cuerpo in bloques:
        if "->" not in cuerpo:
            logger.error("La regla %s no tiene consecuente.", nombre_regla)
            continue
        antecedente, consecuente = cuerpo.split("->", 1)
        regla = (
            " ".join(antecedente.replace("^", ",").replace("swrlb:", "").split())
            + " -> "
            + " ".join(consecuente.replace("^", ",").replace("swrlb:", "").split())
        )
        traducidas.append((nombre_regla, regla))
    return traducidas


def iri_archivo_owlready(ruta: Path) -> str:
    """Arma un IRI de archivo que Owlready2 abre bien en Windows.

    Owlready2 recorta el prefijo ``file://`` (siete caracteres). ``Path.as_uri()``
    produce ``file:///C:/...`` y, al recortarlo, queda ``/C:/...``, que Windows
    rechaza. Con dos barras el recorte deja ``C:/...``.
    """
    texto = ruta.resolve().as_posix()
    return "file://" + texto


def anexar_reglas_swrl(ruta_owl: Path) -> int:
    """Carga el OWL en un mundo aislado, inserta las reglas y lo guarda."""
    from owlready2 import Imp, World

    mundo = World()
    ontologia = mundo.get_ontology(iri_archivo_owlready(ruta_owl)).load()
    cargadas = 0
    with ontologia:
        for nombre, regla in _reglas_desde_archivo(RUTA_REGLAS):
            try:
                imp = Imp()
                imp.set_as_rule(regla)
                cargadas += 1
                logger.info("Regla SWRL cargada en el OWL: %s", nombre)
            except Exception as exc:
                logger.error("No se pudo cargar la regla %s: %s", nombre, exc)
    ontologia.save(file=str(ruta_owl), format="rdfxml")
    mundo.close()
    return cargadas


def construir(forzar: bool = True) -> dict[str, str]:
    """Escribe OWL, Turtle y CSV. Con forzar=False no pisa archivos existentes."""
    _configurar_registro()
    if (
        not forzar
        and RUTA_ONTOLOGIA.exists()
        and RUTA_INSTANCIAS.exists()
        and RUTA_FUENTES.exists()
    ):
        logger.info("Los artefactos ya existen; no se regeneran.")
        return {
            "owl": str(RUTA_ONTOLOGIA),
            "ttl": str(RUTA_INSTANCIAS),
            "csv": str(RUTA_FUENTES),
        }

    grafo = construir_grafo()
    RUTA_ONTOLOGIA.parent.mkdir(parents=True, exist_ok=True)
    grafo.serialize(destination=str(RUTA_ONTOLOGIA), format="pretty-xml")
    escribir_turtle(grafo)
    escribir_csv()
    try:
        total = anexar_reglas_swrl(RUTA_ONTOLOGIA)
        logger.info("Reglas SWRL insertadas: %s", total)
    except Exception as exc:
        logger.error(
            "El OWL de individuos quedó escrito, pero las reglas SWRL no se insertaron: %s",
            exc,
        )
    logger.info("Ontología escrita en %s", RUTA_ONTOLOGIA)
    return {
        "owl": str(RUTA_ONTOLOGIA),
        "ttl": str(RUTA_INSTANCIAS),
        "csv": str(RUTA_FUENTES),
    }


def main() -> None:
    """Punto de entrada: regenera los artefactos desde la semilla."""
    parser = argparse.ArgumentParser(description="Construye la ontología de biocontrol.")
    parser.add_argument(
        "--si-falta",
        action="store_true",
        help="No regenera si OWL, Turtle y CSV ya existen.",
    )
    args = parser.parse_args()
    construir(forzar=not args.si_falta)


if __name__ == "__main__":
    main()
