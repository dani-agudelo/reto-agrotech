import { Loader2 } from "lucide-react";

export function LoadingSpinner() {
  return (
    <div className="flex items-center gap-3 text-gray-500" role="status">
      <Loader2 aria-hidden="true" className="animate-spin" size={16} strokeWidth={1.75} />
      <span>Aplicando reglas SWRL...</span>
    </div>
  );
}
