/** Contrato de POST /consultar y de los catálogos que arma el formulario. */

export interface ConsultaInput {
  plaga: string;
  temperatura: number;
  humedad: number;
}

export interface PasoRegla {
  codigo: string;
  nombre: string;
  activada: boolean;
  detalle: string;
}

export interface ExplicacionConsulta {
  reglas_activadas: string[];
  reglas_no_activadas: string[];
  justificacion: string;
  arbol?: PasoRegla[];
}

/**
 * El motor devuelve estas recomendaciones, con el texto exacto de la API:
 * AltamenteRecomendado, PotencialmenteRecomendado, "Evidencia insuficiente",
 * "Condiciones no satisfechas" y "Documentado sin ventana de uso".
 * La humedad solo viene como umbral si la fuente la documentó; si no, llega
 * en humedad_ensayo y no debe pintarse como rango de viabilidad.
 */
export interface ConsultaOutput {
  recomendacion: string;
  agente: string | null;
  nivel_evidencia: "Alta" | "Media" | "Baja" | "Insuficiente" | null;
  condiciones: {
    temperatura?: [number, number];
    humedad?: [number, number];
    humedad_ensayo?: [number, number];
  } | null;
  fuente: string | null;
  explicacion: ExplicacionConsulta;
  advertencia?: string;
  nota_precaucion?: string | null;
  restricciones_activas?: string[];
}

export interface PlagaCatalogo {
  id: string;
  nombre_cientifico: string;
  nombre_comun: string;
  cultivos: string[];
  sin_agente: boolean;
}

export interface AgenteCatalogo {
  id: string;
  nombre_comun: string;
  nombre_cientifico: string;
  tipo: string;
  descripcion: string;
}

export interface FuenteCatalogo {
  codigo: string;
  cita_corta: string;
  titulo: string;
  doi: string;
  url: string;
}

export type FaseConsulta =
  | "idle"
  | "loading"
  | "success"
  | "warning"
  | "insufficient"
  | "notice"
  | "error";
