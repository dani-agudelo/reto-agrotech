import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";

import { Navbar } from "./components/Navbar";
import { ParamsForm } from "./components/ParamsForm";
import { ResultView } from "./components/ResultView";
import { useConsulta } from "./hooks/useConsulta";
import { obtenerAgentes, obtenerFuentes, obtenerPlagas } from "./services/api";
import type { AgenteCatalogo, FuenteCatalogo, PlagaCatalogo } from "./types/consulta";

function enlaceDe(fuente: FuenteCatalogo | undefined): string | null {
  if (!fuente) return null;
  if (fuente.doi) return `https://doi.org/${fuente.doi}`;
  return fuente.url || null;
}

export default function App() {
  const consulta = useConsulta();
  const [plagas, setPlagas] = useState<PlagaCatalogo[]>([]);
  const [agentes, setAgentes] = useState<AgenteCatalogo[]>([]);
  const [fuentes, setFuentes] = useState<FuenteCatalogo[]>([]);
  const [errorCatalogo, setErrorCatalogo] = useState<string | null>(null);

  useEffect(() => {
    let vigente = true;
    Promise.all([obtenerPlagas(), obtenerAgentes(), obtenerFuentes()])
      .then(([listaPlagas, listaAgentes, listaFuentes]) => {
        if (!vigente) return;
        setPlagas(listaPlagas);
        setAgentes(listaAgentes);
        setFuentes(listaFuentes);
      })
      .catch(() => {
        if (vigente) {
          setErrorCatalogo("No se pudo cargar el inventario. Revisa que la API esté en marcha.");
        }
      });
    return () => {
      vigente = false;
    };
  }, []);

  const descripcionAgente = useMemo(() => {
    const nombre = consulta.resultado?.agente;
    if (!nombre) return null;
    const agente = agentes.find(
      (item) => item.nombre_comun === nombre || item.nombre_cientifico === nombre,
    );
    return agente?.descripcion ?? null;
  }, [agentes, consulta.resultado]);

  const fuente = useMemo(() => {
    const cita = consulta.resultado?.fuente;
    if (!cita) return undefined;
    return fuentes.find((item) => item.cita_corta === cita);
  }, [fuentes, consulta.resultado]);

  const clave =
    consulta.fase === "loading"
      ? "loading"
      : `${consulta.fase}-${consulta.resultado?.recomendacion ?? ""}-${consulta.resultado?.agente ?? ""}`;

  return (
    <div className="min-h-screen bg-white">
      <Navbar />
      <main className="mx-auto mt-12 grid max-w-[1100px] grid-cols-1 gap-12 px-4 md:grid-cols-[35%_65%]">
        <section>
          <ParamsForm
            plagas={plagas}
            enviando={consulta.fase === "loading"}
            onConsultar={consulta.ejecutar}
          />
          {errorCatalogo ? <p className="mt-4 text-xs text-gray-500">{errorCatalogo}</p> : null}
        </section>
        <motion.section
          key={clave}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
        >
          <ResultView
            fase={consulta.fase}
            resultado={consulta.resultado}
            error={consulta.error}
            descripcionAgente={descripcionAgente}
            tituloFuente={fuente?.titulo ?? null}
            enlaceFuente={enlaceDe(fuente)}
          />
        </motion.section>
      </main>
      <footer className="py-8 text-center text-xs text-gray-400">
        Prototipo académico. Universidad de Caldas, 2026.
      </footer>
    </div>
  );
}
