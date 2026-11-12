"""Semilla única del prototipo.

Editar este archivo y regenerar con `python -m ontology.construir_ontologia`
cuando se agregue una plaga, un agente, una fuente o una regla de datos.
Los niveles de evidencia son una clasificación del inventario: no son una
prescripción ni un metaanálisis.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Fuente:
    """Fuente de evidencia o de contexto institucional."""

    id: str
    autores: str
    anio: int | None
    titulo: str
    tipo: str
    rol: str
    cita_corta: str
    notas: str
    doi: str = ""
    url: str = ""


@dataclass(frozen=True)
class Cultivo:
    id: str
    nombre_cientifico: str
    nombre_comun: str
    descripcion: str


@dataclass(frozen=True)
class Plaga:
    id: str
    nombre_cientifico: str
    nombre_comun: str
    descripcion: str
    cultivos: tuple[str, ...]
    contexto: tuple[str, ...] = ()


@dataclass(frozen=True)
class Agente:
    id: str
    nombre_cientifico: str
    nombre_comun: str
    tipo: str
    descripcion: str


@dataclass(frozen=True)
class Condicion:
    id: str
    temp_min: float
    temp_max: float
    hum_min: float
    hum_max: float
    descripcion: str


@dataclass(frozen=True)
class Restriccion:
    id: str
    codigo_practica: str
    etiqueta: str
    descripcion: str
    fuentes: tuple[str, ...]


@dataclass(frozen=True)
class Plataforma:
    id: str
    etiqueta: str
    tipo: str
    descripcion: str
    url: str


@dataclass(frozen=True)
class Analisis:
    id: str
    etiqueta: str
    plataforma_id: str
    estado: str
    variable_respuesta: str
    condicion_experimental: str
    resultado: str


@dataclass(frozen=True)
class Experimento:
    id: str
    etiqueta: str
    plataforma_id: str
    estado: str
    variable_respuesta: str
    condicion_experimental: str
    resultado: str


@dataclass(frozen=True)
class Relacion:
    id: str
    plaga_id: str
    agente_id: str
    condicion_id: str
    nivel: str
    fuente_principal_id: str
    fuentes_ids: tuple[str, ...]
    restricciones_ids: tuple[str, ...]
    variable_respuesta: str
    resultado: str
    condicion_experimental: str
    criterio_nivel: str
    analisis_ids: tuple[str, ...] = ()
    experimento_ids: tuple[str, ...] = ()


# Alias aceptados por el resolvedor de la consulta, ya normalizados
# (minúsculas, sin tildes ni puntos).
ALIAS_PLAGA = {
    "d citri": "Diaphorina_citri",
    "psilido asiatico": "Diaphorina_citri",
    "psilido asiatico de los citricos": "Diaphorina_citri",
    "acaro tostador": "Phyllocoptruta_oleivora",
    "acaro tostador de los citricos": "Phyllocoptruta_oleivora",
    "picudo": "Compsus_sp",
    "picudo de los citricos": "Compsus_sp",
    "compsus": "Compsus_sp",
}

PRACTICAS = (
    ("aplicacion_piretroide", "Aplicación de insecticida piretroide"),
    ("aplicacion_neonicotinoide", "Aplicación de neonicotinoide (p. ej. imidacloprid)"),
    ("aplicacion_fungicida_cuprico", "Aplicación de fungicida cúprico"),
    ("aplicacion_azufre", "Aplicación de azufre"),
)


FUENTES: tuple[Fuente, ...] = (
    Fuente(
        id="F01",
        autores="Bové, J. M.",
        anio=2006,
        titulo=(
            "Huanglongbing: a destructive, newly-emerging, century-old disease of citrus"
        ),
        tipo="articulo",
        rol="contexto",
        cita_corta="F01 - Bové (2006)",
        notas=(
            "Journal of Plant Pathology, 88(1), 7-37. Revisión del patosistema HLB. "
            "No evalúa la eficacia de un agente de biocontrol."
        ),
    ),
    Fuente(
        id="F02",
        autores="Restrepo-García, A. M.; Arias-Ortega, P. L.; Soto-Giraldo, A.",
        anio=2016,
        titulo=(
            "Primer reporte de Tamarixia radiata (Waterston) (Hymenoptera: Eulophidae) "
            "en el departamento de Caldas, Colombia"
        ),
        tipo="articulo",
        rol="respalda_relacion",
        cita_corta="F02 - Restrepo-García et al. (2016)",
        notas=(
            "Boletín Científico Centro de Museos Museo de Historia Natural, "
            "Universidad de Caldas, 20(1), 204-210. Presencia y acción parasítica "
            "de Tamarixia radiata sobre ninfas de Diaphorina citri en Caldas."
        ),
        doi="10.17151/bccm.2016.20.1.15",
        url="https://doi.org/10.17151/bccm.2016.20.1.15",
    ),
    Fuente(
        id="F03",
        autores="Chen, X.; Stansly, P. A.",
        anio=2014,
        titulo=(
            "Biology of Tamarixia radiata (Hymenoptera: Eulophidae), parasitoid of "
            "the citrus greening disease vector Diaphorina citri (Hemiptera: Psyllidae): "
            "a mini review"
        ),
        tipo="articulo",
        rol="respalda_relacion",
        cita_corta="F03 - Chen y Stansly (2014)",
        notas="Florida Entomologist, 97(4), 1404-1412. Revisión biológica del parasitoide.",
    ),
    Fuente(
        id="F04",
        autores="McFarland, C. D.; Hoy, M. A.",
        anio=2001,
        titulo=(
            "Survival of Diaphorina citri, and its two parasitoids Tamarixia radiata "
            "and Diaphorencyrtus aligarhensis, under different relative humidities "
            "and temperature regimes"
        ),
        tipo="articulo",
        rol="respalda_relacion",
        cita_corta="F04 - McFarland y Hoy (2001)",
        notas=(
            "Florida Entomologist, 84(2), 227-233. Supervivencia adulta a 25 °C y 30 °C "
            "con humedades relativas de 7 %, 33 %, 53 %, 75 % y 97 %."
        ),
        doi="10.2307/3496171",
        url="https://doi.org/10.2307/3496171",
    ),
    Fuente(
        id="F05",
        autores="Kondo, T.; Woolley, J. B.; Arciniegas, K. T.; Campos-Patiño, Y.",
        anio=2022,
        titulo=(
            "First report in Colombia and diagnosis of Diaphorencyrtus aligarhensis "
            "(Hymenoptera: Encyrtidae), a parasitoid wasp of Diaphorina citri"
        ),
        tipo="articulo",
        rol="respalda_relacion",
        cita_corta="F05 - Kondo et al. (2022)",
        notas=(
            "Caldasia, 44(3), 541-552. Primer reporte confirmado de la especie en Colombia "
            "(Palmira). Parasitismo de 0,3 % a 1,0 %, frente a 1,5 %–24,2 % de Tamarixia "
            "en el mismo estudio. Una aspersión de imidacloprid interrumpió el seguimiento."
        ),
        doi="10.15446/caldasia.v44n3.95918",
        url="https://doi.org/10.15446/caldasia.v44n3.95918",
    ),
    Fuente(
        id="F06",
        autores="Alemán, J.; Baños, H.; Ravelo, J.",
        anio=2007,
        titulo=(
            "Diaphorina citri y la enfermedad huanglongbing: una combinación destructiva "
            "para la producción citrícola"
        ),
        tipo="articulo",
        rol="respalda_restriccion",
        cita_corta="F06 - Alemán et al. (2007)",
        notas=(
            "Revista Protección Vegetal, 22(3), 154-165. Citado por Restrepo-García et al. "
            "(2016) al señalar que el control químico puede eliminar enemigos naturales."
        ),
    ),
    Fuente(
        id="F07",
        autores="Pérez-González, O.; Gómez-Flores, R.; Tamez-Guerra, P.",
        anio=2022,
        titulo=(
            "Insight into biological control potential of Hirsutella citriformis against "
            "Asian citrus psyllid as a vector of citrus Huanglongbing disease in America"
        ),
        tipo="articulo",
        rol="respalda_relacion",
        cita_corta="F07 - Pérez-González et al. (2022)",
        notas=(
            "Journal of Fungi, 8(6), 573. Revisión: desarrollo óptimo cerca de 25 °C, "
            "epizootias con humedad relativa superior al 80 % y precaución frente a "
            "cobre, aceite y azufre a dosis altas. El papel de los exudados sigue poco caracterizado."
        ),
        doi="10.3390/jof8060573",
        url="https://doi.org/10.3390/jof8060573",
    ),
    Fuente(
        id="F08",
        autores="Restrepo-García, A. M.; Pérez-González, O.; Soto-Giraldo, A.",
        anio=2024,
        titulo=(
            "Primer aislamiento de Hirsutella citriformis en Colombia y evaluación "
            "de su patogenicidad"
        ),
        tipo="articulo",
        rol="respalda_relacion",
        cita_corta="F08 - Restrepo-García et al. (2024)",
        notas=(
            "Boletín Científico Centro de Museos, 28(2), 181-190. Cepa de la Granja "
            "Montelindo. Mortalidad acumulada de 98 % en bioensayo de contacto y 3 % "
            "en el control; similitud del 98,86 % en el gen 28S."
        ),
        doi="10.17151/bccm.2024.28.2.9",
        url="https://doi.org/10.17151/bccm.2024.28.2.9",
    ),
    Fuente(
        id="F09",
        autores=(
            "Casique-Valdes, R.; Reyes-Martinez, A. Y.; Sanchez-Peña, S. R.; "
            "Bidochka, M. J.; Lopez-Arroyo, J. I."
        ),
        anio=2011,
        titulo=(
            "Pathogenicity of Hirsutella citriformis to Diaphorina citri and "
            "Bactericera cockerelli"
        ),
        tipo="articulo",
        rol="respalda_relacion",
        cita_corta="F09 - Casique-Valdes et al. (2011)",
        notas="Florida Entomologist, 94(3), 703-705. Patogenicidad del hongo sobre el psílido.",
        url="https://www.jstor.org/stable/41336460",
    ),
    Fuente(
        id="F10",
        autores="AgroSavia",
        anio=None,
        titulo="Rutas de acceso al parasitoide Tamarixia radiata",
        tipo="recomendacion_tecnologica",
        rol="respalda_relacion",
        cita_corta="F10 - AgroSavia (s. f.)",
        notas=(
            "Oferta tecnológica: incremento in situ, traspatios y reservorios. "
            "No es un artículo de eficacia y no aporta un porcentaje de control."
        ),
        url=(
            "https://www.agrosavia.co/productos-y-servicios/oferta-tecnologica/"
            "linea-agricola/frutales/recomendaciones-protocolos-y-metodologias/"
            "758-rutas-de-acceso-al-parasitoide-tamarixia-radiata"
        ),
    ),
    Fuente(
        id="F11",
        autores="Instituto Colombiano Agropecuario",
        anio=2017,
        titulo=(
            "Demostración de método: liberación de controladores biológicos "
            "para Diaphorina citri"
        ),
        tipo="nota_institucional",
        rol="contexto",
        cita_corta="F11 - ICA (2017)",
        notas=(
            "Jornada de campo en el Atlántico, 6 de diciembre de 2017, con Tamarixia "
            "y hongos entomopatógenos. No es un ensayo publicado."
        ),
        url="https://www.ica.gov.co/noticias/agricola/el-ica-y-corpoica-realizaron-demostracion-de-metod",
    ),
    Fuente(
        id="F12",
        autores="Hernández Arredondo, C.; Rosero Álvarez, N. V.",
        anio=2025,
        titulo=(
            "Aislamiento y multiplicación de cepas nativas de Hirsutella citriformis "
            "Speare como controlador biológico de Diaphorina citri"
        ),
        tipo="tesis",
        rol="respalda_relacion",
        cita_corta="F12 - Hernández Arredondo y Rosero Álvarez (2025)",
        notas=(
            "Trabajo de grado, Ingeniería Agronómica, Universidad de Caldas. "
            "Asesores: Alberto Soto Giraldo y Ana María Restrepo García. "
            "Aislamiento y medios de cultivo; el propio trabajo pide validación de campo."
        ),
        url="https://repositorio.ucaldas.edu.co/entities/publication/75c38aef-0b76-4171-8a69-e3a3f06c53f1",
    ),
    Fuente(
        id="F13",
        autores="Universidad de Caldas",
        anio=None,
        titulo="Spin-off ClayOMICS de la Universidad de Caldas obtiene su registro de marca",
        tipo="nota_institucional",
        rol="interoperabilidad",
        cita_corta="F13 - Universidad de Caldas (ClayOMICS)",
        notas=(
            "ClayOMICS ofrece análisis de datos químicos. La nota no reporta un ensayo "
            "de biocontrol ni un perfil de Hirsutella."
        ),
        url="https://www.ucaldas.edu.co/portal/spin-off-clayomics-de-la-universidad-de-caldas-obtiene-su-registro-de-marca/",
    ),
    Fuente(
        id="F14",
        autores="Universidad de Caldas",
        anio=2024,
        titulo=(
            "Universidad de Caldas seleccionada en la convocatoria ALDEA del "
            "Ministerio de Comercio, Industria y Turismo"
        ),
        tipo="nota_institucional",
        rol="interoperabilidad",
        cita_corta="F14 - Universidad de Caldas (2024)",
        notas=(
            "Nota del 4 de abril de 2024. Nombra los emprendimientos de base tecnológica "
            "Compocol, Clayomics, Biocontroladores y Magnetime."
        ),
        url="https://www.ucaldas.edu.co/portal/universidad-de-caldas-seleccionada-en-convocatoria-del-ministerio-de-comercio-industria-y-turismo-de-colombia/",
    ),
    Fuente(
        id="F15",
        autores="Universidad de Caldas",
        anio=2024,
        titulo="Semillero de Magnetobiología",
        tipo="ficha_institucional",
        rol="interoperabilidad",
        cita_corta="F15 - Semillero de Magnetobiología UCaldas",
        notas=(
            "Grupo de Magnetobiología. Estudia campos electromagnéticos en sistemas "
            "biológicos. Coordinación: Javier Ignacio Torres Osorio. Ficha publicada en 2024."
        ),
        url="https://investigacionesyposgrados.ucaldas.edu.co/semilleros-de-investigacion/semillero-de-magnetobiologia/",
    ),
    Fuente(
        id="F16",
        autores="Universidad de Caldas",
        anio=None,
        titulo="Biocontroladores, spin-off de la Universidad de Caldas",
        tipo="nota_institucional",
        rol="contexto",
        cita_corta="F16 - Universidad de Caldas (Biocontroladores)",
        notas=(
            "La nota menciona a Tamarixia radiata entre los desarrollos del spin-off. "
            "El prototipo no transcribe cifras de eficacia."
        ),
        url="https://www.ucaldas.edu.co/portal/biocontraladores-spin-off-de-la-universidad-de-caldas-en-pro-de-la-agricultura/",
    ),
    Fuente(
        id="F17",
        autores="Gómez, C.",
        anio=2024,
        titulo="Control biológico y microbiológico de plagas y enfermedades en cítricos",
        tipo="documento_repositorio",
        rol="contexto",
        cita_corta="F17 - Gómez (2024)",
        notas=(
            "Registro del repositorio institucional de la Universidad de Caldas. "
            "La ficha pública consultada no detalla resultados, así que no se transcriben."
        ),
        url="https://repositorio.ucaldas.edu.co/handle/ucaldas/19978",
    ),
)


CULTIVOS: tuple[Cultivo, ...] = (
    Cultivo(
        id="Citrus_sinensis",
        nombre_cientifico="Citrus sinensis",
        nombre_comun="naranja dulce",
        descripcion="Cultivo de cítricos usado como hospedero en el inventario semilla.",
    ),
    Cultivo(
        id="Citrus_reticulata",
        nombre_cientifico="Citrus reticulata",
        nombre_comun="mandarina",
        descripcion="Cultivo de cítricos usado como hospedero en el inventario semilla.",
    ),
)


PLAGAS: tuple[Plaga, ...] = (
    Plaga(
        id="Diaphorina_citri",
        nombre_cientifico="Diaphorina citri",
        nombre_comun="psílido asiático de los cítricos",
        descripcion=(
            "Vector del Huanglongbing (HLB). En Caldas se documentó a Tamarixia radiata "
            "alimentándose y parasitando sus ninfas."
        ),
        cultivos=("Citrus_sinensis", "Citrus_reticulata"),
        contexto=("F01", "F02", "F11"),
    ),
    Plaga(
        id="Compsus_sp",
        nombre_cientifico="Compsus sp.",
        nombre_comun="picudo de los cítricos",
        descripcion=(
            "Picudo asociado a cítricos. Esta base no registra un enemigo natural. "
            "La laguna es del inventario: no afirma que no existan controladores en la literatura."
        ),
        cultivos=("Citrus_sinensis", "Citrus_reticulata"),
    ),
    Plaga(
        id="Phyllocoptruta_oleivora",
        nombre_cientifico="Phyllocoptruta oleivora",
        nombre_comun="ácaro tostador de los cítricos",
        descripcion=(
            "Ácaro eriófido que daña la epidermis del fruto. Hirsutella thompsonii se discute "
            "en la literatura de ácaros, pero no se codifica en esta semilla. Por eso la "
            "consulta dispara la laguna de conocimiento de la base."
        ),
        cultivos=("Citrus_sinensis", "Citrus_reticulata"),
    ),
)


AGENTES: tuple[Agente, ...] = (
    Agente(
        id="Tamarixia_radiata",
        nombre_cientifico="Tamarixia radiata",
        nombre_comun="Tamarixia radiata",
        tipo="parasitoide",
        descripcion=(
            "Ectoparasitoide de ninfas de Diaphorina citri. Es el enemigo natural "
            "con evidencia convergente en este inventario."
        ),
    ),
    Agente(
        id="Diaphorencyrtus_sp",
        nombre_cientifico="Diaphorencyrtus aligarhensis",
        nombre_comun="Diaphorencyrtus aligarhensis",
        tipo="parasitoide",
        descripcion=(
            "Endoparasitoide de Diaphorina citri. El identificador conserva "
            "Diaphorencyrtus_sp, como en reportes tempranos; Kondo et al. (2022) "
            "asignan el registro colombiano a D. aligarhensis."
        ),
    ),
    Agente(
        id="Hirsutella_citriformis",
        nombre_cientifico="Hirsutella citriformis",
        nombre_comun="Hirsutella citriformis",
        tipo="hongo_entomopatogeno",
        descripcion=(
            "Hongo entomopatógeno aislado en la Granja Montelindo de la Universidad "
            "de Caldas y patógeno de Diaphorina citri en bioensayo de laboratorio."
        ),
    ),
)


CONDICIONES: tuple[Condicion, ...] = (
    Condicion(
        id="Condicion_Tamarixia",
        temp_min=20,
        temp_max=30,
        hum_min=60,
        hum_max=85,
        descripcion=(
            "Ventana operativa del prototipo. Cubre el óptimo de laboratorio cercano "
            "a 25 °C y los regímenes de 25 °C y 30 °C de McFarland y Hoy (2001, F04). "
            "La humedad 60-85 % excluye los extremos secos del ensayo (7 % y 33 %) "
            "y la saturación (97 %). No es la tabla de un único experimento."
        ),
    ),
    Condicion(
        id="Condicion_Diaphorencyrtus",
        temp_min=22,
        temp_max=32,
        hum_min=50,
        hum_max=90,
        descripcion=(
            "Ventana operativa más amplia. McFarland y Hoy (2001, F04) compararon "
            "supervivencia adulta a 25 °C y 30 °C; Kondo et al. (2022, F05) confirman "
            "la especie en campo sin publicar una curva térmica propia."
        ),
    ),
    Condicion(
        id="Condicion_Hirsutella",
        temp_min=23,
        temp_max=28,
        hum_min=80,
        hum_max=98,
        descripcion=(
            "Ventana de la revisión de Pérez-González et al. (2022, F07): desarrollo "
            "óptimo cerca de 25 °C y epizootias con humedad relativa superior al 80 %, "
            "con registros de campo entre 25 °C y 28 °C. El bioensayo de 2024 (F08) "
            "demuestra patogenicidad en laboratorio, no esta ventana en Caldas."
        ),
    ),
)


RESTRICCIONES: tuple[Restriccion, ...] = (
    Restriccion(
        id="Restriccion_piretroide",
        codigo_practica="aplicacion_piretroide",
        etiqueta="Incompatibilidad con piretroides",
        descripcion=(
            "Un insecticida piretroide de amplio espectro en la ventana de liberación "
            "deprime a los parasitoides. No conviene liberarlos mientras la práctica esté vigente."
        ),
        fuentes=("F06", "F02"),
    ),
    Restriccion(
        id="Restriccion_neonicotinoide",
        codigo_practica="aplicacion_neonicotinoide",
        etiqueta="Incompatibilidad con neonicotinoides",
        descripcion=(
            "Los neonicotinoides, por ejemplo imidacloprid, interfieren con los parasitoides. "
            "En Palmira una aspersión de imidacloprid interrumpió el seguimiento de parasitismo (F05)."
        ),
        fuentes=("F05", "F06"),
    ),
    Restriccion(
        id="Restriccion_cuprico",
        codigo_practica="aplicacion_fungicida_cuprico",
        etiqueta="Incompatibilidad con fungicida cúprico",
        descripcion=(
            "Los fungicidas cúpricos comprometen a Hirsutella citriformis. "
            "La revisión desaconseja aplicar cobre a dosis altas junto con el hongo (F07)."
        ),
        fuentes=("F07",),
    ),
    Restriccion(
        id="Restriccion_azufre",
        codigo_practica="aplicacion_azufre",
        etiqueta="Incompatibilidad con azufre",
        descripcion=(
            "El azufre elemental a dosis altas afecta al hongo entomopatógeno (F07)."
        ),
        fuentes=("F07",),
    ),
)


PLATAFORMAS: tuple[Plataforma, ...] = (
    Plataforma(
        id="ClayOMICS",
        etiqueta="ClayOMICS",
        tipo="analisis_quimico",
        descripcion=(
            "Spin-off de la Universidad de Caldas para análisis de datos químicos "
            "mediante técnicas de medición, separación e identificación."
        ),
        url="https://www.ucaldas.edu.co/portal/spin-off-clayomics-de-la-universidad-de-caldas-obtiene-su-registro-de-marca/",
    ),
    Plataforma(
        id="MAGNETIME",
        etiqueta="MAGNETIME",
        tipo="magnetobiologia",
        descripcion=(
            "Emprendimiento de base tecnológica de la Universidad de Caldas, "
            "vinculado al grupo de Magnetobiología, sobre campos electromagnéticos "
            "en sistemas biológicos."
        ),
        url="https://www.ucaldas.edu.co/portal/universidad-de-caldas-seleccionada-en-convocatoria-del-ministerio-de-comercio-industria-y-turismo-de-colombia/",
    ),
)


ANALISIS: tuple[Analisis, ...] = (
    Analisis(
        id="Analisis_exudados_Hirsutella",
        etiqueta="Perfil químico propuesto de exudados de Hirsutella citriformis",
        plataforma_id="ClayOMICS",
        estado="propuesto",
        variable_respuesta=(
            "exudados con actividad biológica y compatibilidad de soportes de formulación"
        ),
        condicion_experimental=(
            "No hay un protocolo ejecutado en este prototipo. La revisión F07 indica "
            "que el papel de los exudados del hongo está poco caracterizado."
        ),
        resultado=(
            "Enlace de interoperabilidad propuesto con ClayOMICS (F13). "
            "El prototipo no afirma un resultado medido por esa plataforma."
        ),
    ),
)


EXPERIMENTOS: tuple[Experimento, ...] = (
    Experimento(
        id="Experimento_campo_magnetico_conidios",
        etiqueta="Germinación de conidios bajo campo electromagnético",
        plataforma_id="MAGNETIME",
        estado="propuesto",
        variable_respuesta="porcentaje de germinación de conidios",
        condicion_experimental=(
            "Conidios de H. citriformis en la ventana 23-28 °C y humedad relativa "
            "superior al 80 %, con y sin campo electromagnético de baja intensidad. "
            "Protocolo no ejecutado."
        ),
        resultado=(
            "Sin resultado medido. La pregunta se articula con MAGNETIME y con el "
            "semillero de Magnetobiología (F14, F15). No es un experimento realizado."
        ),
    ),
)


RELACIONES: tuple[Relacion, ...] = (
    Relacion(
        id="Relacion_DC_Tamarixia",
        plaga_id="Diaphorina_citri",
        agente_id="Tamarixia_radiata",
        condicion_id="Condicion_Tamarixia",
        nivel="Alta",
        fuente_principal_id="F02",
        fuentes_ids=("F02", "F03", "F04", "F10", "F16"),
        restricciones_ids=("Restriccion_piretroide", "Restriccion_neonicotinoide"),
        variable_respuesta="parasitismo de ninfas de Diaphorina citri",
        resultado=(
            "Presencia y acción parasítica documentadas en Caldas (F02). "
            "El inventario no codifica un porcentaje único de eficacia de campo."
        ),
        condicion_experimental=(
            "Observación de momias y emergencia del parasitoide sobre brotes de cítricos "
            "en el Centro de Investigación y Cría de Enemigos Naturales de la Universidad "
            "de Caldas, entre enero y abril de 2016 (F02)."
        ),
        criterio_nivel=(
            "Alta por convergencia: reporte local de presencia y acción parasítica (F02), "
            "revisión biológica (F03), supervivencia bajo regímenes de temperatura y humedad (F04) "
            "y rutas de acceso en Colombia (F10). No es un metaanálisis de eficacia de campo."
        ),
    ),
    Relacion(
        id="Relacion_DC_Diaphorencyrtus",
        plaga_id="Diaphorina_citri",
        agente_id="Diaphorencyrtus_sp",
        condicion_id="Condicion_Diaphorencyrtus",
        nivel="Media",
        fuente_principal_id="F05",
        fuentes_ids=("F05", "F04"),
        restricciones_ids=("Restriccion_piretroide", "Restriccion_neonicotinoide"),
        variable_respuesta="parasitismo de ninfas de Diaphorina citri",
        resultado=(
            "Parasitismo de 0,3 % a 1,0 % en Palmira, frente a 1,5 %–24,2 % de Tamarixia "
            "en el mismo estudio (F05)."
        ),
        condicion_experimental=(
            "Conteos de momias y emergencia de adultos en un huerto de Agrosavia, Palmira, "
            "en 2020 y 2021 (F05)."
        ),
        criterio_nivel=(
            "Media: la especie está confirmada en Colombia, pero las tasas de campo son bajas "
            "frente a Tamarixia (F05). La regla R2 agrega precaución."
        ),
    ),
    Relacion(
        id="Relacion_DC_Hirsutella",
        plaga_id="Diaphorina_citri",
        agente_id="Hirsutella_citriformis",
        condicion_id="Condicion_Hirsutella",
        nivel="Media",
        fuente_principal_id="F08",
        fuentes_ids=("F08", "F07", "F09", "F12"),
        restricciones_ids=("Restriccion_cuprico", "Restriccion_azufre"),
        variable_respuesta="mortalidad acumulada de adultos de Diaphorina citri",
        resultado=(
            "Mortalidad acumulada de 98 % con conidios de H. citriformis y 3 % en el control; "
            "sinnemas a los 7 días post-mortem (F08)."
        ),
        condicion_experimental=(
            "Bioensayo de contacto directo entre adultos de D. citri y cultivos esporulados; "
            "caracterización morfológica, morfométrica y del gen ribosomal 28S (F08)."
        ),
        criterio_nivel=(
            "Media: hay patogenicidad alta en laboratorio (F08) y una ventana ambiental "
            "descrita en la revisión (F07), pero el inventario no incluye un programa "
            "comercial de campo. Por eso no se asigna Alta y, si la ventana se cumple, se activa R2."
        ),
        analisis_ids=("Analisis_exudados_Hirsutella",),
        experimento_ids=("Experimento_campo_magnetico_conidios",),
    ),
)


def validar_semilla() -> None:
    """Comprueba que las referencias cruzadas de la semilla cierran."""
    fuentes = {item.id for item in FUENTES}
    cultivos = {item.id for item in CULTIVOS}
    plagas = {item.id for item in PLAGAS}
    agentes = {item.id for item in AGENTES}
    condiciones = {item.id for item in CONDICIONES}
    restricciones = {item.id for item in RESTRICCIONES}
    plataformas = {item.id for item in PLATAFORMAS}
    analisis = {item.id for item in ANALISIS}
    experimentos = {item.id for item in EXPERIMENTOS}
    niveles = {"Alta", "Media", "Baja", "Insuficiente"}

    if len(FUENTES) != 17:
        raise ValueError("El inventario debe conservar las fuentes F01 a F17.")

    for plaga in PLAGAS:
        desconocidos = set(plaga.cultivos) - cultivos
        if desconocidos or set(plaga.contexto) - fuentes:
            raise ValueError(f"Referencias rotas en la plaga {plaga.id}")

    for item in list(ANALISIS) + list(EXPERIMENTOS):
        if item.plataforma_id not in plataformas or item.estado not in {"propuesto", "publicado"}:
            raise ValueError(f"Enlace externo inválido en {item.id}")

    for restriccion in RESTRICCIONES:
        if set(restriccion.fuentes) - fuentes:
            raise ValueError(f"Fuente desconocida en {restriccion.id}")

    for relacion in RELACIONES:
        if relacion.plaga_id not in plagas or relacion.agente_id not in agentes:
            raise ValueError(f"Extremos rotos en {relacion.id}")
        if relacion.condicion_id not in condiciones or relacion.nivel not in niveles:
            raise ValueError(f"Condición o nivel inválido en {relacion.id}")
        citados = {relacion.fuente_principal_id, *relacion.fuentes_ids}
        if citados - fuentes or relacion.fuente_principal_id not in relacion.fuentes_ids:
            raise ValueError(f"Fuentes inconsistentes en {relacion.id}")
        if set(relacion.restricciones_ids) - restricciones:
            raise ValueError(f"Restricción desconocida en {relacion.id}")
        if set(relacion.analisis_ids) - analisis or set(relacion.experimento_ids) - experimentos:
            raise ValueError(f"Enlace ClayOMICS o MAGNETIME roto en {relacion.id}")

    for condicion in CONDICIONES:
        if condicion.temp_min > condicion.temp_max or condicion.hum_min > condicion.hum_max:
            raise ValueError(f"Rango invertido en {condicion.id}")
