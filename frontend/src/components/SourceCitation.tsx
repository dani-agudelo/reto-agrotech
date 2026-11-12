interface Props {
  cita: string | null;
  titulo: string | null;
  enlace: string | null;
}

export function SourceCitation({ cita, titulo, enlace }: Props) {
  if (!cita) return null;
  const texto = titulo ? `${cita}. ${titulo}` : cita;

  return (
    <section>
      <h3 className="text-sm font-semibold text-gray-900">Fuente Documental</h3>
      <p className="mt-1 text-sm text-gray-600">{texto}</p>
      {enlace ? (
        <a
          className="mt-2 inline-block text-sm text-[#0D336E] hover:underline"
          href={enlace}
          rel="noreferrer"
          target="_blank"
        >
          {enlace.includes("doi.org") ? "Ver DOI →" : "Ver fuente →"}
        </a>
      ) : null}
    </section>
  );
}
