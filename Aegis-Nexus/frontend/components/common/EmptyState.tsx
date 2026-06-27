export function EmptyState({ label }: { label: string }) {
  return (
    <div className="rounded border border-slate-800 bg-slate-950/70 p-6 text-sm text-slate-400">
      {label}
    </div>
  );
}
