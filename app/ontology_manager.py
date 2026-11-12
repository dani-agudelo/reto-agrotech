"""Carga la ontología y responde consultas SPARQL y de objetos.

Owlready2 conserva las reglas SWRL y los individuos. RDFLib ejecuta las
preguntas de competencia sobre el Turtle, que sale de la misma semilla.
"""

from __future__ import annotations

import logging
import shutil
import threading
import unicodedata
from dataclasses import dataclass, field

from rdflib import Graph

from app.config import NS, RUTA_INSTANCIAS, RUTA_ONTOLOGIA, RUTA_REGLAS, RUTA_SHACL
from data.semilla import ALIAS_PLAGA

logger = logging.getLogger(__name__)

PREFIJO = f"PREFIX bio: <{NS}>\n"

CONSULTA_ENEMIGOS = PREFIJO + """
SELECT ?relacion ?agente ?nombre ?cientifico ?nivel ?fuente ?cita
WHERE {
  ?relacion a bio:RelacionBiocontrol ;
            bio:involucraPlaga bio:%(plaga)s ;
            bio:involucraAgente ?agente ;
            bio:tieneNivelEvidencia ?nivel ;
            bio:fuentePrincipal ?fuente .
  ?agente bio:nombreComun ?nombre ;
          bio:nombreCientifico ?cientifico .
  ?fuente bio:citaCorta ?cita .
}
"""

CONSULTA_NIVELES = PREFIJO + """
SELECT ?relacion ?plaga ?agente ?nivel ?fuente ?cita
WHERE {
  ?relacion a bio:RelacionBiocontrol ;
            bio:involucraPlaga ?plaga ;
            bio:involucraAgente ?agente ;
            bio:tieneNivelEvidencia ?nivel ;
            bio:fuentePrincipal ?fuente .
  ?fuente bio:citaCorta ?cita .
}
"""

CONSULTA_RESTRICCIONES = PREFIJO + """
SELECT ?relacion ?restriccion ?codigo ?descripcion ?fuente
WHERE {
  ?relacion a bio:RelacionBiocontrol ;
            bio:tieneRestriccion ?restriccion .
  ?restriccion bio:codigoPractica ?codigo ;
               bio:descripcion ?descripcion .
  OPTIONAL { ?restriccion bio:justificadoPor ?fuente }
}
"""

CONSULTA_LAGUNAS = PREFIJO + """
SELECT ?plaga ?cultivo
WHERE {
  ?plaga a bio:Plaga ;
         bio:afectaA ?cultivo .
  FILTER NOT EXISTS {
    ?relacion a bio:RelacionBiocontrol ;
              bio:involucraPlaga ?plaga .
  }
}
"""

CONSULTA_CONEXIONES = PREFIJO + """
SELECT ?plataforma ?etiqueta ?tipo ?pieza ?estado ?resultado ?relacion
WHERE {
  {
    ?relacion bio:verificadoPor ?pieza .
  }
  UNION
  {
    ?relacion bio:tieneExperimento ?pieza .
  }
  ?pieza bio:articuladoCon ?plataforma ;
         bio:estadoEnlace ?estado ;
         bio:resultado ?resultado .
  ?plataforma bio:etiqueta ?etiqueta ;
              bio:tipoPlataforma ?tipo .
}
"""

_CANDADO = threading.Lock()
_GESTOR: OntologyManager | None = None


def normalizar(texto: str) -> str:
    """Minúsculas, sin tildes ni puntuación, para comparar nombres de plagas."""
    descompuesto = unicodedata.normalize("NFD", texto.strip().lower())
    sin_tildes = "".join(caracter for caracter in descompuesto if unicodedata.category(caracter) != "Mn")
    limpio = sin_tildes.replace("_", " ").replace(".", " ")
    return " ".join(limpio.split())


def _como_texto(valor: object) -> str:
    """Convierte literales y entidades de Owlready2 en texto plano."""
    if valor is None:
        return ""
    if isinstance(valor, (list, tuple)):
        return _como_texto(valor[0]) if valor else ""
    return str(valor)


def _como_lista(valor: object) -> list:
    if valor is None:
        return []
    if isinstance(valor, (list, tuple)):
        return list(valor)
    return [valor]


def _numero(valor: object) -> float:
    return float(_como_texto(valor))


@dataclass
class RestriccionVista:
    """Restricción de uso leída de la ontología."""

    id: str
    codigo: str
    etiqueta: str
    descripcion: str
    fuentes: list[str] = field(default_factory=list)


@dataclass
class RelacionVista:
    """Relación plaga-agente lista para que el motor la evalúe."""

    id: str
    plaga_id: str
    agente_id: str
    agente_nombre: str
    agente_cientifico: str
    nivel: str
    temp_min: float
    temp_max: float
    hum_min: float
    hum_max: float
    descripcion_condicion: str
    fuente_principal: str
    fuentes: list[str]
    restricciones: list[RestriccionVista]
    variable_respuesta: str
    resultado: str
    condicion_experimental: str
    criterio_nivel: str


@dataclass
class PlagaVista:
    """Plaga del inventario, con los cultivos que afecta."""

    id: str
    nombre_cientifico: str
    nombre_comun: str
    descripcion: str
    cultivos: list[str]
    sin_agente: bool


class OntologyManager:
    """Fachada de la ontología: objetos OWL para inferir y SPARQL para listar."""

    def __init__(self) -> None:
        from owlready2 import World

        from ontology.construir_ontologia import iri_archivo_owlready

        if not RUTA_ONTOLOGIA.exists() or not RUTA_INSTANCIAS.exists():
            from ontology.construir_ontologia import construir

            construir(forzar=True)

        self.mundo = World()
        self.onto = self.mundo.get_ontology(iri_archivo_owlready(RUTA_ONTOLOGIA)).load()
        self.grafo = Graph()
        self.grafo.parse(RUTA_INSTANCIAS, format="turtle")
        self.relaciones = self._leer_relaciones()
        self.plagas = self._leer_plagas()
        logger.info(
            "Ontología cargada: %s plagas, %s relaciones, %s reglas SWRL.",
            len(self.plagas),
            len(self.relaciones),
            self.contar_reglas(),
        )

    def contar_reglas(self) -> int:
        """Cuenta las implicaciones SWRL guardadas en el OWL."""
        return len(list(self.onto.rules()))

    def java_disponible(self) -> bool:
        """Indica si hay un ejecutable de Java para intentar Pellet."""
        return shutil.which("java") is not None

    def sparql(self, consulta: str) -> list[dict[str, str]]:
        """Ejecuta una consulta SPARQL y devuelve filas de texto."""
        respuesta = self.grafo.query(consulta)
        filas: list[dict[str, str]] = []
        for fila in respuesta:
            crudo = fila.asdict() if hasattr(fila, "asdict") else {}
            if not crudo and respuesta.vars is not None:
                crudo = dict(zip(respuesta.vars, fila, strict=False))
            filas.append({str(clave): "" if valor is None else str(valor) for clave, valor in crudo.items()})
        return filas

    def _id_seguro(self, identificador: str) -> str:
        if not identificador.replace("_", "").isalnum():
            raise ValueError(f"Identificador no permitido en SPARQL: {identificador}")
        return identificador

    def enemigos_de(self, plaga_id: str) -> list[dict[str, str]]:
        """Pregunta 1: enemigos naturales documentados para una plaga."""
        consulta = CONSULTA_ENEMIGOS % {"plaga": self._id_seguro(plaga_id)}
        filas = self.sparql(consulta)
        for fila in filas:
            fila["agente"] = _local(fila.get("agente", ""))
            fila["fuente"] = _local(fila.get("fuente", ""))
            fila["cita"] = fila.get("cita", "")
            fila["relacion"] = _local(fila.get("relacion", ""))
        return sorted(filas, key=lambda fila: fila.get("nombre", ""))

    def niveles_de_evidencia(self) -> list[dict[str, str]]:
        """Pregunta 2: nivel de evidencia de cada relación."""
        filas = []
        for fila in self.sparql(CONSULTA_NIVELES):
            filas.append({
                "relacion": _local(fila["relacion"]),
                "plaga": _local(fila["plaga"]),
                "agente": _local(fila["agente"]),
                "nivel": fila["nivel"],
                "fuente": _local(fila["fuente"]),
                "cita": fila.get("cita", ""),
            })
        return sorted(filas, key=lambda fila: fila["relacion"])

    def restricciones_documentadas(self) -> list[dict[str, object]]:
        """Pregunta 3: restricciones y la fuente que las justifica."""
        agrupadas: dict[tuple[str, str], dict[str, object]] = {}
        for fila in self.sparql(CONSULTA_RESTRICCIONES):
            clave = (_local(fila["relacion"]), _local(fila["restriccion"]))
            actual = agrupadas.setdefault(clave, {
                "relacion": clave[0],
                "restriccion": clave[1],
                "codigo": fila["codigo"],
                "descripcion": fila["descripcion"],
                "fuentes": [],
            })
            fuente = _local(fila.get("fuente", ""))
            fuentes = actual["fuentes"]
            if fuente and isinstance(fuentes, list) and fuente not in fuentes:
                fuentes.append(fuente)
        return sorted(agrupadas.values(), key=lambda item: (str(item["relacion"]), str(item["codigo"])))

    def lagunas(self) -> list[dict[str, str]]:
        """Pregunta 4, en SPARQL: plagas sin ninguna relación, bajo mundo cerrado."""
        filas = []
        for fila in self.sparql(CONSULTA_LAGUNAS):
            filas.append({"plaga": _local(fila["plaga"]), "cultivo": _local(fila["cultivo"])})
        return sorted(filas, key=lambda fila: (fila["plaga"], fila["cultivo"]))

    def conexiones_externas(self) -> list[dict[str, str]]:
        """Pregunta 5: enlaces con ClayOMICS y MAGNETIME."""
        filas = []
        for fila in self.sparql(CONSULTA_CONEXIONES):
            filas.append({
                "plataforma": fila.get("etiqueta", ""),
                "tipo": fila.get("tipo", ""),
                "pieza": _local(fila.get("pieza", "")),
                "estado": fila.get("estado", ""),
                "resultado": fila.get("resultado", ""),
                "relacion": _local(fila.get("relacion", "")),
            })
        return filas

    def validar_shacl(self) -> dict[str, object]:
        """Valida el Turtle con las formas SHACL del repositorio."""
        from pyshacl import validate

        formas = Graph()
        formas.parse(RUTA_SHACL, format="turtle")
        cumple, _, reporte = validate(self.grafo, shacl_graph=formas, inference="none")
        if not cumple:
            logger.warning("SHACL reportó inconformidades.")
        return {"cumple": bool(cumple), "reporte": str(reporte)}

    def resolver_plaga(self, texto: str) -> PlagaVista | None:
        """Acepta el identificador, el nombre científico, el común o un alias."""
        clave = normalizar(texto)
        for plaga in self.plagas:
            candidatos = {
                normalizar(plaga.id),
                normalizar(plaga.nombre_cientifico),
                normalizar(plaga.nombre_comun),
            }
            if clave in candidatos:
                return plaga
        alias = ALIAS_PLAGA.get(clave)
        if alias:
            return self.plaga_por_id(alias)
        return None

    def plaga_por_id(self, identificador: str) -> PlagaVista | None:
        for plaga in self.plagas:
            if plaga.id == identificador:
                return plaga
        return None

    def relaciones_de(self, plaga_id: str) -> list[RelacionVista]:
        return [relacion for relacion in self.relaciones if relacion.plaga_id == plaga_id]

    def listar_agentes(self) -> list[dict[str, str]]:
        """Agentes de biocontrol presentes en la ontología."""
        agentes = []
        for agente in self.onto.AgenteBiocontrol.instances():
            agentes.append({
                "id": agente.name,
                "nombre_comun": _como_texto(agente.nombreComun),
                "nombre_cientifico": _como_texto(agente.nombreCientifico),
                "tipo": _como_texto(agente.tipoAgente),
                "descripcion": _como_texto(agente.descripcion),
            })
        return sorted(agentes, key=lambda item: item["nombre_comun"])

    def listar_fuentes(self) -> list[dict[str, str]]:
        """Inventario F01–F17 para la interfaz y el endpoint."""
        fuentes = []
        for fuente in self.onto.FuenteEvidencia.instances():
            fuentes.append({
                "codigo": fuente.name,
                "cita_corta": _como_texto(fuente.citaCorta),
                "autores": _como_texto(fuente.autores),
                "anio": _como_texto(fuente.anio),
                "titulo": _como_texto(fuente.titulo),
                "tipo": _como_texto(fuente.tipoFuente),
                "rol": _como_texto(fuente.rolFuente),
                "doi": _como_texto(fuente.doi),
                "url": _como_texto(fuente.url),
                "notas": _como_texto(fuente.notas),
            })
        return sorted(fuentes, key=lambda item: item["codigo"])

    def texto_reglas(self) -> str:
        """Devuelve el archivo SWRL para mostrarlo o revisarlo."""
        return RUTA_REGLAS.read_text(encoding="utf-8")

    def _leer_relaciones(self) -> list[RelacionVista]:
        vistas = []
        for relacion in self.onto.RelacionBiocontrol.instances():
            condicion = relacion.tieneCondicion
            agente = relacion.involucraAgente
            fuente = relacion.fuentePrincipal
            restricciones = []
            for restriccion in _como_lista(relacion.tieneRestriccion):
                restricciones.append(RestriccionVista(
                    id=restriccion.name,
                    codigo=_como_texto(restriccion.codigoPractica),
                    etiqueta=_como_texto(restriccion.etiqueta),
                    descripcion=_como_texto(restriccion.descripcion),
                    fuentes=[item.name for item in _como_lista(restriccion.justificadoPor)],
                ))
            vistas.append(RelacionVista(
                id=relacion.name,
                plaga_id=relacion.involucraPlaga.name,
                agente_id=agente.name,
                agente_nombre=_como_texto(agente.nombreComun),
                agente_cientifico=_como_texto(agente.nombreCientifico),
                nivel=_como_texto(relacion.tieneNivelEvidencia),
                temp_min=_numero(condicion.temperaturaMin),
                temp_max=_numero(condicion.temperaturaMax),
                hum_min=_numero(condicion.humedadMin),
                hum_max=_numero(condicion.humedadMax),
                descripcion_condicion=_como_texto(condicion.descripcionCondicion),
                fuente_principal=_como_texto(fuente.citaCorta),
                fuentes=[item.name for item in _como_lista(relacion.respaldadoPor)],
                restricciones=restricciones,
                variable_respuesta=_como_texto(relacion.variableRespuesta),
                resultado=_como_texto(relacion.resultado),
                condicion_experimental=_como_texto(relacion.condicionExperimental),
                criterio_nivel=_como_texto(relacion.criterioNivel),
            ))
        return sorted(vistas, key=lambda item: item.id)

    def _leer_plagas(self) -> list[PlagaVista]:
        con_agente = {relacion.plaga_id for relacion in self.relaciones}
        plagas = []
        for plaga in self.onto.Plaga.instances():
            # La subclase de cierre también es Plaga; se lee una sola vez.
            if plaga.name in {item.id for item in plagas}:
                continue
            plagas.append(PlagaVista(
                id=plaga.name,
                nombre_cientifico=_como_texto(plaga.nombreCientifico),
                nombre_comun=_como_texto(plaga.nombreComun),
                descripcion=_como_texto(plaga.descripcion),
                cultivos=[_como_texto(cultivo.nombreCientifico) for cultivo in _como_lista(plaga.afectaA)],
                sin_agente=plaga.name not in con_agente,
            ))
        return sorted(plagas, key=lambda item: item.nombre_cientifico)


def _local(iri: str) -> str:
    if "#" in iri:
        return iri.rsplit("#", 1)[-1]
    return iri.rsplit("/", 1)[-1]


def obtener_gestor() -> OntologyManager:
    """Devuelve el gestor cargado, uno solo por proceso."""
    global _GESTOR
    with _CANDADO:
        if _GESTOR is None:
            _GESTOR = OntologyManager()
        return _GESTOR
