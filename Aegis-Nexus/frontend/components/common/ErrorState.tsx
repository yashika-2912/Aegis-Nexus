export function ErrorState({ message }: { message: string }) {
  return (
    <div className="rounded border border-rose-500/30 bg-rose-950/20 p-4 text-sm text-rose-200">
      {message}
    </div>
  );
}
