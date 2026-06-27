import Link from "next/link";
import { Boxes, Gauge, GitBranch, History, ServerCog } from "lucide-react";

const items = [
  { label: "Overview", icon: Gauge, href: "/" },
  { label: "Digital Twin", icon: GitBranch, href: "/digital-twin" },
  { label: "Services", icon: ServerCog, href: "/" },
  { label: "Telemetry", icon: Boxes, href: "/" },
  { label: "Timeline", icon: History, href: "/" },
];

export function Sidebar() {
  return (
    <aside className="hidden w-56 shrink-0 border-r border-slate-800 bg-slate-950 p-4 lg:block">
      <div className="mb-7 text-lg font-semibold text-white">Aegis Nexus</div>
      <nav className="space-y-1">
        {items.map(({ label, icon: Icon }) => (
          <Link key={label} href={label === "Digital Twin" ? "/digital-twin" : "/"} className="flex items-center gap-3 rounded px-3 py-2 text-sm text-slate-400 transition hover:bg-slate-900 hover:text-white">
            <Icon className="h-4 w-4" />
            {label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
