"""Semilla alineada con data/inventario_fuentes.tex.

Los identificadores F01–F17, los niveles de confiabilidad y las limitaciones
salen de ese inventario. Una fuente puede ser
confiable y, aun así, no traer una ventana de uso: en ese caso la relación
se conserva y la ventana no se inventa.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Fuente:
    """Ficha del inventario: metadatos, extracción y confiabilidad."""

    id: str
    autores: str
    anio: int | None
    titulo: str
    tipo: str
    iniciativa: str
    nivel: str
    naturaleza: str
    cita_corta: str
    informacion_extraida: str
    alcance: str
    acceso: str
    doi: str = ""
    url: str = ""
    fecha_consulta: str = "11/nov/2026"


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
    """Ventana de uso. La humedad solo decide si humedad_decide es verdadera."""

    id: str
    temp_min: float
    temp_max: float
    descripcion: str
    hum_min: float | None = None
    hum_max: float | None = None
    humedad_decide: bool = False


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
    fuente_id: str


@dataclass(frozen=True)
class Experimento:
    id: str
    etiqueta: str
    plataforma_id: str
    estado: str
    variable_respuesta: str
    condicion_experimental: str
    resultado: str
    fuente_id: str


@dataclass(frozen=True)
class Relacion:
    id: str
    plaga_id: str
    agente_id: str
    nivel: str
    fuente_principal_id: str
    fuentes_ids: tuple[str, ...]
    variable_respuesta: str
    resultado: str
    condicion_experimental: str
    criterio_nivel: str
    condicion_id: str | None = None
    restricciones_ids: tuple[str, ...] = ()
    analisis_ids: tuple[str, ...] = ()
    experimento_ids: tuple[str, ...] = ()


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
    (
        "aplicacion_insecticida_botanico",
        "Aplicación de insecticida botánico (Biodie o NeemPHC, F10)",
    ),
    (
        "aplicacion_extractos_vegetales",
        "Aplicación de extractos vegetales evaluados con Tamarixia (F06)",
    ),
)


FUENTES: tuple[Fuente, ...] = (
    Fuente(
        id="F01",
        autores="Arias-Ortega, P. L.; Restrepo-García, A. M.; Soto-Giraldo, A.",
        anio=2016,
        titulo="Primer registro de Diaphorencyrtus sp. (Hymenoptera: Encyrtidae) en Colombia",
        tipo="Artículo científico (registro)",
        iniciativa="Biocontroladores",
        nivel="Alta",
        naturaleza="Hecho (presencia); hipótesis (control)",
        cita_corta="F01 - Arias-Ortega et al. (2016)",
        informacion_extraida=(
            "Primer registro en Colombia de Diaphorencyrtus sp., parasitoide de ninfas "
            "de Diaphorina citri, capturado a mano en brotes de cítricos en Manizales."
        ),
        alcance=(
            "Documenta presencia. No mide parasitismo ni condiciones de uso; "
            "el efecto de control queda como hipótesis."
        ),
        acceso="Abierto · CC BY 4.0",
        doi="10.17151/bccm.2016.20.1.12",
        url="https://doi.org/10.17151/bccm.2016.20.1.12",
    ),
    Fuente(
        id="F02",
        autores="Restrepo-García, A. M.; Arias-Ortega, P. L.; Soto-Giraldo, A.",
        anio=2016,
        titulo=(
            "Primer reporte de Tamarixia radiata (Waterston) (Hymenoptera: Eulophidae) "
            "en el departamento de Caldas, Colombia"
        ),
        tipo="Artículo científico (registro)",
        iniciativa="Biocontroladores",
        nivel="Alta",
        naturaleza="Hecho documentado",
        cita_corta="F02 - Restrepo-García et al. (2016)",
        informacion_extraida=(
            "Tamarixia radiata está presente en Caldas y parasita ninfas de Diaphorina citri "
            "en brotes colectados entre enero y abril de 2016."
        ),
        alcance=(
            "Documenta presencia y parasitismo en Caldas. No reporta rangos agroclimáticos "
            "ni dosis de liberación. Boletín Científico Centro de Museos, 20(1), 204-210."
        ),
        acceso="Abierto (licencia no verificada)",
        doi="10.17151/bccm.2016.20.1.15",
        url="https://doi.org/10.17151/bccm.2016.20.1.15",
    ),
    Fuente(
        id="F03",
        autores="Soto G., A.; Ocampo S., A.",
        anio=2011,
        titulo=(
            "Estudio preliminar de Trigonospila sp. (Diptera: Tachinidae), parasitoide "
            "de Compsus viridilineatus (Coleoptera: Curculionidae)"
        ),
        tipo="Artículo científico (descripción)",
        iniciativa="Biocontroladores",
        nivel="Alta",
        naturaleza="Hecho documentado",
        cita_corta="F03 - Soto y Ocampo (2011)",
        informacion_extraida=(
            "Descripción morfológica de larvas, pupas y adultos de Trigonospila sp., "
            "parasitoide de adultos del picudo. Adultos de Compsus recolectados en "
            "Maltería, Manizales (2250 msnm)."
        ),
        alcance=(
            "Estudio preliminar morfológico, sin eficacia de campo. "
            "Volumen y páginas por completar al citar."
        ),
        acceso="Abierto (licencia no verificada)",
        url="https://revistasojs.ucaldas.edu.co/index.php/boletincientifico/article/view/4434",
    ),
    Fuente(
        id="F04",
        autores="Vinasco, N.; Vallejo, L. F.; Soto, A.",
        anio=2017,
        titulo=(
            "New species of the genus Trigonospila Pokorny (Diptera: Tachinidae) "
            "parasitises adult Compsus sp. Schoenherr (Coleoptera: Curculionidae) in Colombia"
        ),
        tipo="Artículo científico (descripción de especie)",
        iniciativa="Biocontroladores",
        nivel="Alta",
        naturaleza="Hecho documentado",
        cita_corta="F04 - Vinasco et al. (2017)",
        informacion_extraida=(
            "Descripción de Trigonospila unicaldasi. Holotipo en la Granja Tesorito, "
            "Valle de Maltería, Manizales (2280 m), sobre adultos de Compsus sp. en limón."
        ),
        alcance=(
            "Descripción taxonómica y registro de parasitismo. No ofrece condiciones "
            "de uso ni protocolo de liberación. Boletín Científico Centro de Museos, 21(2), 207-219."
        ),
        acceso="Abierto (licencia no verificada)",
        doi="10.17151/bccm.2017.21.2.14",
        url="https://doi.org/10.17151/bccm.2017.21.2.14",
    ),
    Fuente(
        id="F05",
        autores="Restrepo-García, A. M.; Soto-Giraldo, A.",
        anio=2017,
        titulo=(
            "Control alternativo de Diaphorina citri Kuwayama (Hemiptera: Liviidae) "
            "utilizando caldo sulfocálcico"
        ),
        tipo="Artículo científico (laboratorio)",
        iniciativa="Biocontroladores",
        nivel="Alta",
        naturaleza="Hecho documentado (laboratorio)",
        cita_corta="F05 - Restrepo-García y Soto-Giraldo (2017)",
        informacion_extraida=(
            "Toxicidad letal y subletal del caldo sulfocálcico sobre Diaphorina citri "
            "en el Centro de Investigación y Cría de Enemigos Naturales de la Universidad de Caldas."
        ),
        alcance=(
            "Ensayo de laboratorio sobre la plaga. No se codifica como restricción de "
            "enemigos naturales: el inventario pide verificar ese efecto antes de usarlo en R4. "
            "Boletín Científico Centro de Museos, 21(2), 51-60."
        ),
        acceso="Abierto (licencia no verificada)",
        doi="10.17151/bccm.2017.21.2.4",
        url="https://doi.org/10.17151/bccm.2017.21.2.4",
    ),
    Fuente(
        id="F06",
        autores="Barros-Barrios, M. M.; Restrepo-García, A. M.; Narváez-Solarte, W.; Soto-Giraldo, A.",
        anio=2024,
        titulo=(
            "Efecto de extractos vegetales compuestos sobre Diaphorina citri "
            "(Hemiptera: Liviidae) y su parasitoide Tamarixia radiata (Hymenoptera: Eulophidae)"
        ),
        tipo="Artículo científico (laboratorio)",
        iniciativa="Biocontroladores",
        nivel="Alta",
        naturaleza="Hecho documentado (laboratorio)",
        cita_corta="F06 - Barros-Barrios et al. (2024)",
        informacion_extraida=(
            "Efecto de extractos de Murraya paniculata, Cocos nucifera, Syzygium aromaticum "
            "y Psidium guajava sobre Diaphorina citri y Tamarixia radiata, en olfatometría."
        ),
        alcance=(
            "Condiciones controladas. Los valores cuantitativos por extracto no están en la ficha; "
            "la restricción advierte la interacción, no una prohibición numérica. "
            "Boletín Científico Centro de Museos, 28(1), 125-138."
        ),
        acceso="Abierto (licencia no verificada)",
        doi="10.17151/bccm.2024.28.1.7",
        url="https://doi.org/10.17151/bccm.2024.28.1.7",
    ),
    Fuente(
        id="F07",
        autores="Restrepo-García, A. M.; Pérez-González, O.; Soto-Giraldo, A.",
        anio=2024,
        titulo=(
            "Primer aislamiento de Hirsutella citriformis en Colombia y evaluación de su patogenicidad"
        ),
        tipo="Artículo científico (laboratorio)",
        iniciativa="Biocontroladores",
        nivel="Alta",
        naturaleza="Hecho documentado (laboratorio)",
        cita_corta="F07 - Restrepo-García et al. (2024)",
        informacion_extraida=(
            "Cepa de la Granja Montelindo: mortalidad acumulada de Diaphorina citri de 98 % "
            "con conidios y 3 % en el control, en bioensayo de laboratorio."
        ),
        alcance=(
            "El artículo reporta incubación a 25 ± 20 °C, probable error tipográfico, y no "
            "reporta humedad relativa. No se deriva un rango agroclimático ni hay ensayo de campo. "
            "Boletín Científico Centro de Museos, 28(2), 181-190."
        ),
        acceso="Abierto (licencia no verificada)",
        doi="10.17151/bccm.2024.28.2.9",
        url="https://doi.org/10.17151/bccm.2024.28.2.9",
    ),
    Fuente(
        id="F08",
        autores="Gómez-Torres, M. L.; Nava, D. E. et al.",
        anio=2012,
        titulo=(
            "Life table of Tamarixia radiata (Hymenoptera: Eulophidae) on Diaphorina citri "
            "(Hemiptera: Psyllidae) at different temperatures"
        ),
        tipo="Artículo científico (laboratorio)",
        iniciativa="Biocontroladores",
        nivel="Alta",
        naturaleza="Hecho documentado (laboratorio)",
        cita_corta="F08 - Gómez-Torres et al. (2012)",
        informacion_extraida=(
            "Tabla de vida a 15, 20, 25, 30 y 35 °C, con 70 ± 10 % de humedad relativa. "
            "Hubo desarrollo en todas esas temperaturas y la mayor viabilidad y tasa "
            "reproductiva neta ocurrió a 25 °C."
        ),
        alcance=(
            "Población brasileña en laboratorio. La viabilidad es de desarrollo, no de una "
            "liberación en campo. La humedad es condición de ensayo, no un umbral de uso. "
            "Journal of Economic Entomology, 105(2). Páginas por completar al citar."
        ),
        acceso="Resumen abierto; texto completo posiblemente restringido",
        doi="10.1603/EC11280",
        url="https://doi.org/10.1603/EC11280",
    ),
    Fuente(
        id="F09",
        autores="McCalla, K. A.; Keçeci, M.; Milosavljevic, I.; Ratkowsky, D. A.; Hoddle, M. S.",
        anio=2019,
        titulo=(
            "The influence of temperature variation on life history parameters and thermal "
            "performance curves of Tamarixia radiata, a parasitoid of the Asian citrus psyllid"
        ),
        tipo="Artículo científico (laboratorio)",
        iniciativa="Biocontroladores",
        nivel="Alta",
        naturaleza="Hecho documentado (laboratorio)",
        cita_corta="F09 - McCalla et al. (2019)",
        informacion_extraida=(
            "Temperaturas constantes y fluctuantes, con promedios de 12 a 38 °C, "
            "afectan el desarrollo y la longevidad de Tamarixia radiata."
        ),
        alcance=(
            "Población de Pakistán liberada en California, en laboratorio. Complementa a F08 "
            "con un rango térmico más amplio, pero no fija un umbral de liberación. "
            "Journal of Economic Entomology, 112(4), 1560-1574."
        ),
        acceso="Resumen abierto; texto completo posiblemente restringido",
        doi="10.1093/jee/toz067",
        url="https://doi.org/10.1093/jee/toz067",
    ),
    Fuente(
        id="F10",
        autores="Monsreal-Ceballos, R. J.; Ruíz-Sánchez, E.; Sánchez-Borja, M. et al.",
        anio=2017,
        titulo=(
            "Efectos de insecticidas botánicos comerciales en Tamarixia radiata, "
            "un ectoparasitoide de Diaphorina citri"
        ),
        tipo="Artículo científico (laboratorio)",
        iniciativa="Biocontroladores",
        nivel="Alta",
        naturaleza="Hecho documentado (laboratorio)",
        cita_corta="F10 - Monsreal-Ceballos et al. (2017)",
        informacion_extraida=(
            "Mortalidad de Tamarixia radiata por residualidad de 12,7 % (Biodie) y 12,3 % "
            "(NeemPHC), y por ingestión de 33,3 % y 28,7 %. Bioensayo a 25 ± 5 °C y 60 ± 10 % HR."
        ),
        alcance=(
            "Evalúa insecticidas botánicos, no organofosforados como el clorpirifos. "
            "Estudio hecho en México. La carencia de 21 días tras clorpirifos no tiene fuente "
            "en este inventario. Ecosistemas y Recursos Agropecuarios, 4(12), 589-596."
        ),
        acceso="Abierto (Dialnet; licencia no verificada)",
        url="https://dialnet.unirioja.es/descarga/articulo/6343377.pdf",
    ),
    Fuente(
        id="F11",
        autores="Cruz-Cruz, D.; Gómez-Ruiz, J.; Barrera, J. F.; Sánchez-Peña, S. R.; Valle-Mora, J. F.",
        anio=2020,
        titulo=(
            "Pathogenicity of Beauveria bassiana against immature stages of Diaphorina citri "
            "under laboratory conditions"
        ),
        tipo="Artículo científico (laboratorio)",
        iniciativa="Biocontroladores",
        nivel="Alta",
        naturaleza="Hecho documentado (laboratorio)",
        cita_corta="F11 - Cruz-Cruz et al. (2020)",
        informacion_extraida=(
            "Cepas de Beauveria bassiana a 1×10^8 conidios/mL: sin efecto sobre huevos; "
            "mortalidad de ninfas entre 21 y 58 % según la cepa. CL50 en ninfas IV-V de "
            "8,34×10^6 (Bb-Dc) y 1×10^7 (Bb-Rhy) conidios/mL."
        ),
        alcance=(
            "Cepas mexicanas en laboratorio. No valida una cepa local «UC10» ni aplica "
            "directamente a Caldas. Southwestern Entomologist, 45(3), 609-620."
        ),
        acceso="Resumen abierto; texto completo por suscripción",
        doi="10.3958/059.045.0303",
        url="https://doi.org/10.3958/059.045.0303",
    ),
    Fuente(
        id="F12",
        autores="Imbachi, K.; Mesa, N. C.; Rodríguez, I. V. et al.",
        anio=2012,
        titulo=(
            "Evaluación de estrategias de control biológico de Polyphagotarsonemus latus (Banks) "
            "y Phyllocoptruta oleivora (Ashmead) en naranja Valencia"
        ),
        tipo="Artículo científico (campo)",
        iniciativa="Biocontroladores",
        nivel="Alta",
        naturaleza="Hecho documentado (campo)",
        cita_corta="F12 - Imbachi et al. (2012)",
        informacion_extraida=(
            "En naranja Valencia (Caicedonia, Valle del Cauca, 1150 msnm) la liberación de "
            "Chrysoperla carnea redujo el daño de Phyllocoptruta oleivora a 10 % en el primer ciclo. "
            "Los ácaros Phytoseiidae se dispersaron rápido de los frutos."
        ),
        alcance=(
            "Las plagas objetivo son ácaros, no Diaphorina citri. No sustenta que Chrysoperla "
            "controle al psílido. Región distinta a Caldas. Acta Agronómica, 61(4), 333-338."
        ),
        acceso="Abierto (licencia no verificada)",
        url="https://revistas.unal.edu.co/index.php/acta_agronomica/article/download/38139/40315/169692",
    ),
    Fuente(
        id="F13",
        autores="Autor por verificar en la ficha del repositorio",
        anio=2025,
        titulo=(
            "Efecto del tratamiento magnético de semillas sobre un sistema productivo de "
            "Solanum lycopersicum L., a escala comercial"
        ),
        tipo="Tesis de doctorado",
        iniciativa="MAGNETIME",
        nivel="Media",
        naturaleza="Hecho documentado (tesis)",
        cita_corta="F13 - Repositorio UCaldas (2025)",
        informacion_extraida=(
            "Tratamiento magnético de semillas de tomate a escala comercial: revisión sistemática, "
            "optimización de parámetros, crecimiento, floración y rendimiento. El rendimiento "
            "aumentó y la floración no cambió."
        ),
        alcance=(
            "Tesis, no artículo revisado por pares. Cultivo: tomate. No hay validación en cítricos. "
            "Es la evidencia que el caso integrador señala como faltante para trasladar MAGNETIME al cultivo."
        ),
        acceso="Abierto · CC BY-NC-ND 4.0",
        url="https://repositorio.ucaldas.edu.co/handle/ucaldas/22551",
    ),
    Fuente(
        id="F14",
        autores="Torres-Osorio, J. I.; Aranzazu-Osorio, J. E.; Carbonell-Padrino, M. V.",
        anio=2015,
        titulo=(
            "Efecto del campo magnético estático homogéneo en la germinación y absorción "
            "de agua en semillas de soja"
        ),
        tipo="Artículo científico (laboratorio)",
        iniciativa="MAGNETIME",
        nivel="Alta",
        naturaleza="Hecho documentado (laboratorio)",
        cita_corta="F14 - Torres-Osorio et al. (2015)",
        informacion_extraida=(
            "Soja expuesta a 125 y 300 mT durante 10, 20 y 60 min. El electroimán superó a los "
            "imanes. 300 mT por 10 min redujo más el tiempo medio de germinación. La absorción "
            "de agua no mostró diferencias significativas."
        ),
        alcance="Especie: soja. No hay evidencia en cítricos ni en control de plagas. Tecno Lógicas, 18(35), 11-20.",
        acceso="Abierto · CC BY",
        url="https://www.redalyc.org/pdf/3442/344243102002.pdf",
    ),
    Fuente(
        id="F15",
        autores="Villa Carmona, E.; Torres Osorio, J. I.; Zamorano-Montañez, C.",
        anio=2023,
        titulo=(
            "Análisis del desarrollo vegetativo de plantas de Solanum lycopersicum L. "
            "generadas de semillas tratadas magnéticamente"
        ),
        tipo="Tesis de pregrado",
        iniciativa="MAGNETIME",
        nivel="Media",
        naturaleza="Hecho documentado (tesis)",
        cita_corta="F15 - Villa Carmona et al. (2023)",
        informacion_extraida=(
            "Semillas de tomate tratadas con campo magnético estático no homogéneo: "
            "plantas con 21 % más área foliar y 9 % más altura que el control."
        ),
        alcance="Trabajo de grado, sin revisión por pares. Cultivo: tomate. Ingeniería Agronómica, Universidad de Caldas.",
        acceso="Abierto (openAccess)",
        url="https://repositorio.ucaldas.edu.co/handle/ucaldas/19679",
    ),
    Fuente(
        id="F16",
        autores="Universidad de Caldas",
        anio=2022,
        titulo="Spin Off ClayOMICs de la Universidad de Caldas obtiene su registro de marca",
        tipo="Noticia institucional",
        iniciativa="ClayOMICS",
        nivel="Media",
        naturaleza="Contexto institucional",
        cita_corta="F16 - Universidad de Caldas (2022)",
        informacion_extraida=(
            "ClayOMICS ofrece análisis de datos químicos mediante técnicas de medición, "
            "separación e identificación. Surge del grupo de Cromatografía y Técnicas Afines "
            "y obtuvo registro de marca ante la SIC en 2022."
        ),
        alcance=(
            "Sirve para la existencia y el alcance de los servicios, no como evidencia científica. "
            "La fecha exacta de publicación de la nota queda por completar."
        ),
        acceso="Abierto (web institucional)",
        url="https://www.ucaldas.edu.co/portal/spin-off-clayomics-de-la-universidad-de-caldas-obtiene-su-registro-de-marca/",
    ),
    Fuente(
        id="F17",
        autores="Betancourt Arango, J. P.; Patiño Ospina, A.; Taborda Ocampo, G.; Fiscal Ladino, J. A.",
        anio=2020,
        titulo=(
            "Aplicaciones de la xenometabolómica para la identificación de biomarcadores "
            "de toxicidad: una revisión del tema"
        ),
        tipo="Artículo de revisión",
        iniciativa="ClayOMICS",
        nivel="Alta",
        naturaleza="Hecho documentado (revisión)",
        cita_corta="F17 - Betancourt Arango et al. (2020)",
        informacion_extraida=(
            "Revisión de GC-MS, LC-MS, UHPLC-QTOF-MS, RMN e ICP-MS aplicadas a plaguicidas, "
            "metales pesados, micotoxinas y otros analitos, en agua, tejidos, plantas y alimentos."
        ),
        alcance=(
            "Revisión del grupo de Cromatografía de la Universidad de Caldas. No es un servicio "
            "ni un resultado de ClayOMICS. Sirve de puente conceptual con residuos de plaguicidas. "
            "Biosalud, 19(1), 7-30."
        ),
        acceso="Abierto (licencia no verificada)",
        doi="10.17151/biosa.2020.19.1.1",
        url="https://doi.org/10.17151/biosa.2020.19.1.1",
    ),
)


CULTIVOS: tuple[Cultivo, ...] = (
    Cultivo(
        id="Citricos",
        nombre_cientifico="Citrus spp.",
        nombre_comun="cítricos",
        descripcion=(
            "Hospedero citado de forma genérica en los registros de Diaphorina citri "
            "y sus parasitoides en Caldas (F01, F02). La ficha no fija la especie."
        ),
    ),
    Cultivo(
        id="Citrus_limon",
        nombre_cientifico="Citrus limon",
        nombre_comun="limón",
        descripcion="Hospedero del holotipo de Trigonospila unicaldasi en la Granja Tesorito (F04).",
    ),
    Cultivo(
        id="Citrus_sinensis",
        nombre_cientifico="Citrus sinensis",
        nombre_comun="naranja dulce",
        descripcion="Naranja Valencia del ensayo de campo en Caicedonia sobre ácaros (F12).",
    ),
)


PLAGAS: tuple[Plaga, ...] = (
    Plaga(
        id="Diaphorina_citri",
        nombre_cientifico="Diaphorina citri",
        nombre_comun="psílido asiático de los cítricos",
        descripcion=(
            "Psílido de los cítricos. En el inventario tiene parasitoides, un hongo "
            "entomopatógeno y un ensayo con Beauveria. El caldo sulfocálcico (F05) "
            "se evaluó sobre la plaga, no como restricción de los enemigos naturales."
        ),
        cultivos=("Citricos",),
        contexto=("F01", "F02", "F05"),
    ),
    Plaga(
        id="Compsus_sp",
        nombre_cientifico="Compsus sp.",
        nombre_comun="picudo de los cítricos",
        descripcion=(
            "Picudo recolectado en Maltería y en limón de la Granja Tesorito. "
            "F03 lo trata como Compsus viridilineatus y F04 como Compsus sp."
        ),
        cultivos=("Citrus_limon",),
        contexto=("F03", "F04"),
    ),
    Plaga(
        id="Phyllocoptruta_oleivora",
        nombre_cientifico="Phyllocoptruta oleivora",
        nombre_comun="ácaro tostador de los cítricos",
        descripcion=(
            "Ácaro eriófido evaluado en naranja Valencia junto con Polyphagotarsonemus latus (F12). "
            "Esa fuente no autoriza a usar el mismo agente contra Diaphorina citri."
        ),
        cultivos=("Citrus_sinensis",),
        contexto=("F12",),
    ),
)


AGENTES: tuple[Agente, ...] = (
    Agente(
        id="Tamarixia_radiata",
        nombre_cientifico="Tamarixia radiata",
        nombre_comun="Tamarixia radiata",
        tipo="parasitoide",
        descripcion=(
            "Ectoparasitoide de ninfas de Diaphorina citri. Presencia y parasitismo en Caldas (F02); "
            "desarrollo entre 15 y 35 °C en laboratorio, con mejor viabilidad a 25 °C (F08)."
        ),
    ),
    Agente(
        id="Diaphorencyrtus_sp",
        nombre_cientifico="Diaphorencyrtus sp.",
        nombre_comun="Diaphorencyrtus sp.",
        tipo="parasitoide",
        descripcion=(
            "Parasitoide de ninfas de Diaphorina citri. F01 es un registro de presencia en Manizales; "
            "el control queda como hipótesis porque no mide parasitismo ni condiciones de uso."
        ),
    ),
    Agente(
        id="Hirsutella_citriformis",
        nombre_cientifico="Hirsutella citriformis",
        nombre_comun="Hirsutella citriformis",
        tipo="hongo_entomopatogeno",
        descripcion=(
            "Hongo entomopatógeno aislado en la Granja Montelindo. En laboratorio causó 98 % "
            "de mortalidad acumulada de Diaphorina citri (F07). Es la cepa colombiana documentada; "
            "el inventario no trae una cepa local de Beauveria llamada UC10."
        ),
    ),
    Agente(
        id="Beauveria_bassiana",
        nombre_cientifico="Beauveria bassiana",
        nombre_comun="Beauveria bassiana",
        tipo="hongo_entomopatogeno",
        descripcion=(
            "Cepas mexicanas Bb-Dc y Bb-Rhy, patógenas de ninfas de Diaphorina citri en laboratorio (F11). "
            "No corresponden a una cepa validada en la Universidad de Caldas."
        ),
    ),
    Agente(
        id="Trigonospila_unicaldasi",
        nombre_cientifico="Trigonospila unicaldasi",
        nombre_comun="Trigonospila unicaldasi",
        tipo="parasitoide",
        descripcion=(
            "Parasitoide de adultos de Compsus. F03 describió el género en Maltería; "
            "F04 describió la especie con holotipo en la Granja Tesorito."
        ),
    ),
    Agente(
        id="Chrysoperla_carnea",
        nombre_cientifico="Chrysoperla carnea",
        nombre_comun="Chrysoperla carnea",
        tipo="depredador",
        descripcion=(
            "Depredador liberado contra ácaros en naranja Valencia (F12). "
            "El inventario no lo documenta como controlador de Diaphorina citri."
        ),
    ),
)


CONDICIONES: tuple[Condicion, ...] = (
    Condicion(
        id="Condicion_Tamarixia",
        temp_min=15,
        temp_max=35,
        hum_min=60,
        hum_max=80,
        humedad_decide=False,
        descripcion=(
            "Ventana térmica documentada por la tabla de vida de F08: desarrollo a 15, 20, 25, 30 "
            "y 35 °C, con mayor viabilidad y tasa reproductiva neta a 25 °C. F09 estudia promedios "
            "de 12 a 38 °C y no se usa como umbral de liberación. La humedad 70 ± 10 % (60-80 %) "
            "es la condición de ensayo de F08; el inventario la marca como no equivalente a un "
            "rango de viabilidad, así que no decide la recomendación."
        ),
    ),
)


RESTRICCIONES: tuple[Restriccion, ...] = (
    Restriccion(
        id="Restriccion_botanicos",
        codigo_practica="aplicacion_insecticida_botanico",
        etiqueta="Mortalidad por insecticidas botánicos",
        descripcion=(
            "Biodie y NeemPHC causaron mortalidad de Tamarixia radiata por residualidad "
            "(12,7 % y 12,3 %) y por ingestión (33,3 % y 28,7 %) en laboratorio (F10). "
            "No hay fuente en el inventario para una carencia tras clorpirifos."
        ),
        fuentes=("F10",),
    ),
    Restriccion(
        id="Restriccion_extractos",
        codigo_practica="aplicacion_extractos_vegetales",
        etiqueta="Interacción con extractos vegetales",
        descripcion=(
            "F06 evaluó extractos de Murraya paniculata, cocotero, clavo y guayaba sobre "
            "Diaphorina citri y Tamarixia radiata. La ficha no trae los valores por extracto; "
            "la alerta pide revisarlos antes de liberar, no afirma una dosis incompatible."
        ),
        fuentes=("F06",),
    ),
)


PLATAFORMAS: tuple[Plataforma, ...] = (
    Plataforma(
        id="ClayOMICS",
        etiqueta="ClayOMICS",
        tipo="analisis_quimico",
        descripcion=(
            "Spin-off de la Universidad de Caldas para análisis de datos químicos. "
            "La noticia F16 acredita el servicio; la revisión F17 es del grupo de Cromatografía "
            "y no es un resultado del spin-off."
        ),
        url="https://www.ucaldas.edu.co/portal/spin-off-clayomics-de-la-universidad-de-caldas-obtiene-su-registro-de-marca/",
    ),
    Plataforma(
        id="MAGNETIME",
        etiqueta="MAGNETIME",
        tipo="magnetobiologia",
        descripcion=(
            "Línea de tratamiento magnético de semillas. Las fuentes del inventario son de "
            "tomate y soja, no de cítricos ni de control de plagas."
        ),
        url="https://repositorio.ucaldas.edu.co/handle/ucaldas/22551",
    ),
)


ANALISIS: tuple[Analisis, ...] = (
    Analisis(
        id="Analisis_xenometabolomica",
        etiqueta="Revisión de técnicas analíticas para biomarcadores de toxicidad",
        plataforma_id="ClayOMICS",
        estado="contexto",
        fuente_id="F17",
        variable_respuesta="técnica analítica, analito y matriz",
        condicion_experimental=(
            "Revisión del tema. No es un análisis encargado a ClayOMICS ni un perfil de una cepa."
        ),
        resultado=(
            "F17 reseña GC-MS, LC-MS, UHPLC-QTOF-MS, RMN e ICP-MS frente a plaguicidas, metales "
            "y micotoxinas. Sirve de puente conceptual con residuos; no es un resultado del spin-off (F16)."
        ),
    ),
)


EXPERIMENTOS: tuple[Experimento, ...] = (
    Experimento(
        id="Experimento_magnetico_tomate_comercial",
        etiqueta="Tratamiento magnético de semilla de tomate a escala comercial",
        plataforma_id="MAGNETIME",
        estado="documentado",
        fuente_id="F13",
        variable_respuesta="rendimiento y floración de Solanum lycopersicum",
        condicion_experimental="Sistema productivo comercial de tomate. Tesis de doctorado, autor por verificar en la ficha.",
        resultado=(
            "El rendimiento aumentó y la floración no cambió (F13, confiabilidad media). "
            "No hay validación en cítricos."
        ),
    ),
    Experimento(
        id="Experimento_magnetico_soja",
        etiqueta="Campo magnético estático en germinación de soja",
        plataforma_id="MAGNETIME",
        estado="documentado",
        fuente_id="F14",
        variable_respuesta="tiempo medio de germinación y absorción de agua",
        condicion_experimental="Semillas de soja a 125 y 300 mT durante 10, 20 y 60 min.",
        resultado=(
            "300 mT por 10 min redujo más el tiempo medio de germinación. "
            "La absorción de agua no cambió de forma significativa (F14). Especie: soja."
        ),
    ),
    Experimento(
        id="Experimento_magnetico_tomate_pregrado",
        etiqueta="Desarrollo vegetativo de tomate tras tratamiento magnético de la semilla",
        plataforma_id="MAGNETIME",
        estado="documentado",
        fuente_id="F15",
        variable_respuesta="área foliar y altura",
        condicion_experimental="Campo magnético estático no homogéneo sobre semillas de tomate.",
        resultado=(
            "21 % más área foliar y 9 % más altura que el control (F15, trabajo de grado). Cultivo: tomate."
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
        fuentes_ids=("F02", "F08", "F09"),
        restricciones_ids=("Restriccion_botanicos", "Restriccion_extractos"),
        variable_respuesta="parasitismo de ninfas y viabilidad del desarrollo de Tamarixia radiata",
        resultado=(
            "Presencia y parasitismo en Caldas (F02). En laboratorio hay desarrollo entre 15 y 35 °C "
            "y la mayor viabilidad a 25 °C (F08). F09 amplía el estudio térmico a promedios de 12 a 38 °C."
        ),
        condicion_experimental=(
            "Colecta de brotes en Caldas, enero a abril de 2016 (F02). Tabla de vida a cinco "
            "temperaturas constantes y 70 ± 10 % HR (F08)."
        ),
        criterio_nivel=(
            "Alta porque F02, F08 y F09 documentan la relación. La ventana de decisión es 15-35 °C. "
            "No se usa 20-30 °C ni 60-85 % HR como umbral: el inventario los marca como parcial o sin fuente."
        ),
    ),
    Relacion(
        id="Relacion_DC_Diaphorencyrtus",
        plaga_id="Diaphorina_citri",
        agente_id="Diaphorencyrtus_sp",
        nivel="Media",
        fuente_principal_id="F01",
        fuentes_ids=("F01",),
        variable_respuesta="presencia del parasitoide sobre ninfas",
        resultado="Primer registro en Colombia, en brotes de cítricos de Manizales (F01).",
        condicion_experimental="Captura manual en brotes. Sin medición de parasitismo ni de clima de uso.",
        criterio_nivel=(
            "Media para el control: la fuente es de confiabilidad alta, pero solo prueba presencia. "
            "El efecto sobre la plaga es una hipótesis y no hay ventana de uso."
        ),
    ),
    Relacion(
        id="Relacion_DC_Hirsutella",
        plaga_id="Diaphorina_citri",
        agente_id="Hirsutella_citriformis",
        nivel="Alta",
        fuente_principal_id="F07",
        fuentes_ids=("F07",),
        variable_respuesta="mortalidad acumulada de Diaphorina citri",
        resultado="98 % de mortalidad acumulada con conidios y 3 % en el control (F07).",
        condicion_experimental=(
            "Bioensayo de laboratorio con la cepa de Montelindo. La incubación publicada "
            "como 25 ± 20 °C no se convierte en rango de campo."
        ),
        criterio_nivel=(
            "Alta para la patogenicidad de laboratorio. Sin ventana agroclimática ni ensayo de campo, "
            "así que no compite con Tamarixia en la regla climática."
        ),
    ),
    Relacion(
        id="Relacion_DC_Beauveria",
        plaga_id="Diaphorina_citri",
        agente_id="Beauveria_bassiana",
        nivel="Alta",
        fuente_principal_id="F11",
        fuentes_ids=("F11",),
        variable_respuesta="mortalidad de ninfas de Diaphorina citri",
        resultado=(
            "Sin efecto sobre huevos. Mortalidad de ninfas entre 21 y 58 % según la cepa, "
            "a 1×10^8 conidios/mL (F11)."
        ),
        condicion_experimental="Laboratorio, cepas mexicanas Bb-Dc y Bb-Rhy.",
        criterio_nivel=(
            "Alta para ese bioensayo. La limitación se anota aparte: no es una cepa de la "
            "Universidad de Caldas y no se extrapola a Caldas."
        ),
    ),
    Relacion(
        id="Relacion_Compsus_Trigonospila",
        plaga_id="Compsus_sp",
        agente_id="Trigonospila_unicaldasi",
        nivel="Alta",
        fuente_principal_id="F04",
        fuentes_ids=("F04", "F03"),
        variable_respuesta="parasitismo de adultos de Compsus",
        resultado=(
            "Parasitismo de adultos en limón, con la especie descrita en 2017 (F04) "
            "y un estudio morfológico previo del género (F03)."
        ),
        condicion_experimental="Colecta en Maltería (2250 msnm) y holotipo en la Granja Tesorito (2280 m).",
        criterio_nivel=(
            "Alta para el hecho del parasitismo. No hay condiciones de uso ni protocolo de liberación, "
            "así que no se activa una recomendación climática."
        ),
    ),
    Relacion(
        id="Relacion_PO_Chrysoperla",
        plaga_id="Phyllocoptruta_oleivora",
        agente_id="Chrysoperla_carnea",
        nivel="Alta",
        fuente_principal_id="F12",
        fuentes_ids=("F12",),
        variable_respuesta="daño de Phyllocoptruta oleivora en fruto",
        resultado="La liberación redujo el daño a 10 % en el primer ciclo, en naranja Valencia (F12).",
        condicion_experimental="Campo en Caicedonia, Valle del Cauca, 1150 msnm. También se observó a Phytoseiidae.",
        criterio_nivel=(
            "Alta para el ensayo de campo contra el ácaro. No autoriza a recomendar Chrysoperla "
            "contra Diaphorina citri ni trae una ventana numérica de temperatura."
        ),
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
    estados = {"documentado", "contexto", "propuesto", "publicado"}

    if len(FUENTES) != 17:
        raise ValueError("El inventario debe conservar las fuentes F01 a F17.")
    if any(item.nivel not in niveles for item in FUENTES):
        raise ValueError("Hay una fuente con nivel de confiabilidad fuera de la escala.")

    for plaga in PLAGAS:
        if set(plaga.cultivos) - cultivos or set(plaga.contexto) - fuentes:
            raise ValueError(f"Referencias rotas en la plaga {plaga.id}")

    for item in (*ANALISIS, *EXPERIMENTOS):
        if item.plataforma_id not in plataformas or item.estado not in estados or item.fuente_id not in fuentes:
            raise ValueError(f"Enlace externo inválido en {item.id}")

    for restriccion in RESTRICCIONES:
        if set(restriccion.fuentes) - fuentes:
            raise ValueError(f"Fuente desconocida en {restriccion.id}")

    for relacion in RELACIONES:
        if relacion.plaga_id not in plagas or relacion.agente_id not in agentes:
            raise ValueError(f"Extremos rotos en {relacion.id}")
        if relacion.condicion_id is not None and relacion.condicion_id not in condiciones:
            raise ValueError(f"Condición desconocida en {relacion.id}")
        if relacion.nivel not in niveles:
            raise ValueError(f"Nivel inválido en {relacion.id}")
        citados = {relacion.fuente_principal_id, *relacion.fuentes_ids}
        if citados - fuentes or relacion.fuente_principal_id not in relacion.fuentes_ids:
            raise ValueError(f"Fuentes inconsistentes en {relacion.id}")
        if set(relacion.restricciones_ids) - restricciones:
            raise ValueError(f"Restricción desconocida en {relacion.id}")
        if set(relacion.analisis_ids) - analisis or set(relacion.experimento_ids) - experimentos:
            raise ValueError(f"Enlace externo roto en {relacion.id}")

    for condicion in CONDICIONES:
        if condicion.temp_min > condicion.temp_max:
            raise ValueError(f"Rango térmico invertido en {condicion.id}")
        if condicion.hum_min is not None and condicion.hum_max is not None and condicion.hum_min > condicion.hum_max:
            raise ValueError(f"Rango de humedad invertido en {condicion.id}")
