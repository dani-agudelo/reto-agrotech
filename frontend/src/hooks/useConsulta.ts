/**
 * Traduce una consulta del formulario al estado visual de la columna derecha.
 * No decide la recomendación: solo clasifica el texto que devuelve el motor.
 */
import { useCallback, useState } from "react";
import axios from "axios";

import { consultar } from "../services/api";
import type { ConsultaInput, ConsultaOutput, FaseConsulta } from "../types/consulta";

interface EstadoConsulta {
  fase: FaseConsulta;
  resultado: ConsultaOutput | null;
  error: string | null;
  ejecutar: (entrada: ConsultaInput) => Promise<void>;
}

function clasificar(recomendacion: string): FaseConsulta {
  if (recomendacion === "AltamenteRecomendado") return "success";
  if (recomendacion === "PotencialmenteRecomendado") return "warning";
  if (recomendacion === "Evidencia insuficiente") return "insufficient";
  return "notice";
}

function mensajeDeError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    if (!error.response) {
      return "No se pudo conectar con el motor de consulta. Confirma que la API esté en marcha.";
    }
    const detalle: unknown = error.response.data;
    if (
      detalle &&
      typeof detalle === "object" &&
      "detail" in detalle &&
      typeof detalle.detail === "string"
    ) {
      return detalle.detail;
    }
    return "El motor no pudo completar la consulta.";
  }
  return "Ocurrió un error inesperado al consultar.";
}

export function useConsulta(): EstadoConsulta {
  const [fase, setFase] = useState<FaseConsulta>("idle");
  const [resultado, setResultado] = useState<ConsultaOutput | null>(null);
  const [error, setError] = useState<string | null>(null);

  const ejecutar = useCallback(async (entrada: ConsultaInput) => {
    setFase("loading");
    setError(null);
    try {
      const salida = await consultar(entrada);
      setResultado(salida);
      setFase(clasificar(salida.recomendacion));
    } catch (fallo) {
      setResultado(null);
      setError(mensajeDeError(fallo));
      setFase("error");
    }
  }, []);

  return { fase, resultado, error, ejecutar };
}
