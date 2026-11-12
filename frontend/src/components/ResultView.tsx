import { useState } from "react";

import type { ConsultaOutput, FaseConsulta } from "../types/consulta";
import { LoadingSpinner } from "./LoadingSpinner";
import { SourceCitation } from "./SourceCitation";

interface Props {
  fase: FaseConsulta;
  resultado: ConsultaOutput | null;
  error: string | null;
  descripcionAgente: string | null;
  tituloFuente: string | null;
  enlaceFuente: string | null;
}

const PUNTO: Record<string, string> = {
  AltamenteRecomendado: "bg-[#10B981]",
  PotencialmenteRecomendado: "bg-amber-500",
  "Evidencia insuficiente": "bg-red-500",
  "Condiciones no satisfechas": "bg-gray-400",
  "Documentado sin ventana de uso": "bg-gray-400",
};

const ETIQUETA: Record<string, string> = {
  AltamenteRecomendado: "Altamente Recomendado",
  PotencialmenteRecomendado: "Recomendado con Precaución",
  "Evidencia insuficiente": "Evidencia Insuficiente",
  "Condiciones no satisfechas": "Condiciones no satisfechas",
  "Documentado sin ventana de uso": "Documentado sin ventana de uso",
};

function rango(par: [number, number] | undefined, unidad: string): string {
  if (!par) return "No documentada";
  return `${par[0]}${unidad} – ${par[1]}${unidad}`;
}

export function ResultView({
  fase,
  resultado,
  error,
  descripcionAgente,
  tituloFuente,
  enlaceFuente,
}: Props) {
  const [abierta, setAbierta] = useState(false);

  if (fase === "idle") {
    return (
      <p className="text-gray-400 italic">
        Ajusta los parámetros y presiona Ejecutar Consulta para iniciar el razonamiento.
      </p>
    );
  }

  if (fase === "loading") {
    return <LoadingSpinner />;
  }

  if (fase === "error" || !resultado) {
    return (
      <p className="text-sm text-gray-600">
        {error ?? "No se pudo mostrar la consulta."}
      </p>
    );
  }

  const recomendacion = resultado.recomendacion;
  const punto = PUNTO[recomendacion] ?? "bg-gray-400";
  const etiqueta = ETIQUETA[recomendacion] ?? recomendacion;
  const pasos = resultado.explicacion.arbol ?? [];
  const muestraFicha = Boolean(resultado.agente) && fase !== "insufficient";

  if (!muestraFicha) {
    return (
      <div>
        <Estado punto={punto} etiqueta={etiqueta} />
        <p className="mt-6 text-sm leading-6 text-gray-600">
          {resultado.explicacion.justificacion ||
            "No se encontró un agente documentado para esta combinación. Se ha registrado una laguna de conocimiento (R3)."}
        </p>
      </div>
    );
  }

  const humedadEsEnsayo = Boolean(resultado.condiciones?.humedad_ensayo) && !resultado.condiciones?.humedad;

  return (
    <div>
      <Estado punto={punto} etiqueta={etiqueta} />
      <h2 className="mt-2 text-3xl font-bold italic text-gray-900">{resultado.agente}</h2>
      {descripcionAgente ? <p className="mt-1 text-gray-600">{descripcionAgente}</p> : null}
      {fase === "warning" && resultado.nota_precaucion ? (
        <p className="mt-3 text-sm text-amber-700">{resultado.nota_precaucion}</p>
      ) : null}

      <hr className="my-6 border-gray-200" />

      <div className="grid grid-cols-3 gap-4">
        <Metrica etiqueta="Nivel de Evidencia" valor={resultado.nivel_evidencia ?? "—"} />
        <Metrica
          etiqueta="Temperatura"
          valor={rango(resultado.condiciones?.temperatura, "°C")}
        />
        <Metrica
          etiqueta="Humedad"
          valor={
            humedadEsEnsayo
              ? rango(resultado.condiciones?.humedad_ensayo, "%")
              : rango(resultado.condiciones?.humedad, "%")
          }
          nota={humedadEsEnsayo ? "Condición de ensayo, no umbral" : undefined}
        />
      </div>

      <hr className="my-6 border-gray-200" />

      <section>
        <h3 className="text-base font-semibold text-gray-900">¿Por qué se recomienda?</h3>
        <ul className="mt-4 space-y-3">
          {pasos.map((paso) => (
            <li key={paso.codigo} className="flex gap-3 text-sm text-gray-600">
              <span className={paso.activada ? "text-green-600" : "text-gray-400"}>
                {paso.activada ? "✓" : "×"}
              </span>
              <span>
                <strong className="font-semibold text-gray-900">{paso.codigo}:</strong> {paso.detalle}
              </span>
            </li>
          ))}
        </ul>
        {resultado.restricciones_activas && resultado.restricciones_activas.length > 0 ? (
          <p className="mt-4 text-sm text-gray-700">
            Restricción activa: {resultado.restricciones_activas.join("; ")}
          </p>
        ) : null}
      </section>

      <hr className="my-6 border-gray-200" />

      <SourceCitation cita={resultado.fuente} titulo={tituloFuente} enlace={enlaceFuente} />

      {resultado.advertencia ? (
        <p className="mt-6 text-xs text-gray-400">{resultado.advertencia}</p>
      ) : null}

      <button
        className="mt-6 text-xs text-gray-400 hover:text-gray-600"
        type="button"
        onClick={() => setAbierta((valor) => !valor)}
      >
        Ver lógica SPARQL
      </button>
      {abierta ? (
        <p className="mt-3 text-sm leading-6 text-gray-600">{resultado.explicacion.justificacion}</p>
      ) : null}
    </div>
  );
}

function Estado({ punto, etiqueta }: { punto: string; etiqueta: string }) {
  return (
    <div className="flex items-center gap-2">
      <span className={`h-2 w-2 rounded-full ${punto}`} />
      <span className="text-sm font-semibold text-gray-700">{etiqueta}</span>
    </div>
  );
}

function Metrica({ etiqueta, valor, nota }: { etiqueta: string; valor: string; nota?: string }) {
  return (
    <div>
      <p className="text-xs text-gray-500">{etiqueta}</p>
      <p className="text-base font-bold text-gray-900">{valor}</p>
      {nota ? <p className="mt-1 text-xs text-gray-400">{nota}</p> : null}
    </div>
  );
}
