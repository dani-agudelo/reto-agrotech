/**
 * Cliente HTTP del motor de biocontrol.
 * La base sale de VITE_API_URL; si el archivo .env no existe, se usa el
 * puerto local de uvicorn para que `npm run dev` funcione sin configuración.
 */
import axios from "axios";

import type {
  AgenteCatalogo,
  ConsultaInput,
  ConsultaOutput,
  FuenteCatalogo,
  PlagaCatalogo,
} from "../types/consulta";

const baseURL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL,
  timeout: 30_000,
  headers: { "Content-Type": "application/json" },
});

export function urlDocumentacion(): string {
  return `${baseURL.replace(/\/$/, "")}/docs`;
}

export async function consultar(entrada: ConsultaInput): Promise<ConsultaOutput> {
  const respuesta = await api.post<ConsultaOutput>("/consultar", entrada);
  return respuesta.data;
}

export async function obtenerPlagas(): Promise<PlagaCatalogo[]> {
  const respuesta = await api.get<PlagaCatalogo[]>("/plagas");
  return respuesta.data;
}

export async function obtenerAgentes(): Promise<AgenteCatalogo[]> {
  const respuesta = await api.get<AgenteCatalogo[]>("/agentes");
  return respuesta.data;
}

export async function obtenerFuentes(): Promise<FuenteCatalogo[]> {
  const respuesta = await api.get<FuenteCatalogo[]>("/fuentes");
  return respuesta.data;
}
