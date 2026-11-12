import { Leaf } from "lucide-react";

import { urlDocumentacion } from "../services/api";

export function Navbar() {
  return (
    <header className="h-16 border-b border-gray-200 bg-white">
      <div className="mx-auto flex h-full max-w-[1100px] items-center justify-between px-4">
        <div className="flex items-center gap-2 text-gray-900">
          <Leaf aria-hidden="true" size={18} strokeWidth={1.75} />
          <span className="text-xl font-bold">BioControl</span>
        </div>
        <div className="flex items-center gap-4">
          <a
            className="text-sm text-gray-500 hover:text-gray-900"
            href={urlDocumentacion()}
            rel="noreferrer"
            target="_blank"
          >
            Documentación
          </a>
          <span className="flex h-8 w-8 items-center justify-center rounded-full bg-gray-100 text-xs font-medium text-gray-600">
            IA
          </span>
        </div>
      </div>
    </header>
  );
}
