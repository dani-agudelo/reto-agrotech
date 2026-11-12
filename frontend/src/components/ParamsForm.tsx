import { FormEvent, useEffect, useMemo, useState } from "react";

import type { ConsultaInput, PlagaCatalogo } from "../types/consulta";

interface Props {
  plagas: PlagaCatalogo[];
  enviando: boolean;
  onConsultar: (entrada: ConsultaInput) => void;
}

const ETIQUETA_CULTIVO: Record<string, string> = {
  "Citrus spp.": "Citrus spp. (cítricos)",
  "Citrus limon": "Citrus limon (limón)",
  "Citrus sinensis": "Citrus sinensis (naranja dulce)",
};

function etiquetaCultivo(nombre: string): string {
  return ETIQUETA_CULTIVO[nombre] ?? nombre;
}

export function ParamsForm({ plagas, enviando, onConsultar }: Props) {
  const [cultivo, setCultivo] = useState("");
  const [plaga, setPlaga] = useState("");
  const [temperatura, setTemperatura] = useState(25);
  const [humedad, setHumedad] = useState(70);

  const cultivos = useMemo(() => {
    const vistos = new Set<string>();
    for (const item of plagas) {
      for (const nombre of item.cultivos) vistos.add(nombre);
    }
    return [...vistos];
  }, [plagas]);

  const plagasVisibles = useMemo(
    () => plagas.filter((item) => item.cultivos.includes(cultivo)),
    [plagas, cultivo],
  );

  useEffect(() => {
    if (plagas.length === 0 || cultivo) return;
    const preferida = plagas.find((item) => item.id === "Diaphorina_citri") ?? plagas[0];
    setCultivo(preferida.cultivos[0] ?? "");
    setPlaga(preferida.id);
  }, [plagas, cultivo]);

  useEffect(() => {
    if (plagasVisibles.length === 0) return;
    if (!plagasVisibles.some((item) => item.id === plaga)) {
      setPlaga(plagasVisibles[0].id);
    }
  }, [plagasVisibles, plaga]);

  function enviar(evento: FormEvent) {
    evento.preventDefault();
    if (!plaga || enviando) return;
    onConsultar({ plaga, temperatura, humedad });
  }

  return (
    <form className="flex flex-col" onSubmit={enviar}>
      <h1 className="text-2xl font-bold text-gray-900">Nueva Consulta</h1>
      <p className="mb-8 mt-1 text-sm text-gray-500">
        Ingresa los parámetros del cultivo y la plaga.
      </p>

      <div className="flex flex-col gap-6">
        <label className="flex flex-col gap-2">
          <span className="text-sm font-medium text-gray-700">Cultivo</span>
          <select
            className="w-full rounded-md border border-gray-300 bg-white p-2 focus:outline-none focus:ring-2 focus:ring-[#0D336E]"
            value={cultivo}
            onChange={(evento) => setCultivo(evento.target.value)}
            disabled={cultivos.length === 0}
          >
            {cultivos.length === 0 ? <option value="">Cargando inventario…</option> : null}
            {cultivos.map((nombre) => (
              <option key={nombre} value={nombre}>
                {etiquetaCultivo(nombre)}
              </option>
            ))}
          </select>
        </label>

        <label className="flex flex-col gap-2">
          <span className="text-sm font-medium text-gray-700">Plaga Objetivo</span>
          <select
            className="w-full rounded-md border border-gray-300 bg-white p-2 focus:outline-none focus:ring-2 focus:ring-[#0D336E]"
            value={plaga}
            onChange={(evento) => setPlaga(evento.target.value)}
            disabled={plagasVisibles.length === 0}
          >
            {plagasVisibles.map((item) => (
              <option key={item.id} value={item.id}>
                {item.nombre_cientifico} ({item.nombre_comun})
              </option>
            ))}
          </select>
        </label>

        <label className="flex flex-col gap-2">
          <span className="flex items-center justify-between text-sm font-medium text-gray-700">
            Temperatura (°C)
            <span className="font-bold text-gray-900">{temperatura}°C</span>
          </span>
          <input
            className="w-full accent-[#0D336E]"
            type="range"
            min={10}
            max={40}
            step={1}
            value={temperatura}
            onChange={(evento) => setTemperatura(Number(evento.target.value))}
          />
        </label>

        <label className="flex flex-col gap-2">
          <span className="flex items-center justify-between text-sm font-medium text-gray-700">
            Humedad Relativa (%)
            <span className="font-bold text-gray-900">{humedad}%</span>
          </span>
          <input
            className="w-full accent-[#0D336E]"
            type="range"
            min={20}
            max={100}
            step={1}
            value={humedad}
            onChange={(evento) => setHumedad(Number(evento.target.value))}
          />
        </label>
      </div>

      <button
        className="mt-8 w-full rounded-md bg-[#0D336E] py-3 font-medium text-white transition-colors hover:bg-blue-900 disabled:cursor-not-allowed disabled:opacity-60"
        type="submit"
        disabled={enviando || !plaga}
      >
        Ejecutar Consulta
      </button>
      <p className="mt-4 text-center text-xs text-gray-400">
        El sistema evalúa reglas SWRL sobre la ontología OWL.
      </p>
    </form>
  );
}
