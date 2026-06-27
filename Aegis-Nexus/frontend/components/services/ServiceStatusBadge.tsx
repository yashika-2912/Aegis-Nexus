import type { ServiceStatus } from "@/types/service";
import { STATUS_COLORS } from "@/utils/constants";

export function ServiceStatusBadge({ status }: { status: ServiceStatus }) {
  return (
    <span className={`inline-flex min-w-20 justify-center rounded border px-2 py-1 text-xs font-semibold ${STATUS_COLORS[status]}`}>
      {status}
    </span>
  );
}
