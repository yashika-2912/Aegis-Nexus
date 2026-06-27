import type { TimelineEvent as TimelineEventType } from "@/types/event";
import { TimelineItem } from "./TimelineItem";

export function EventTimeline({ events }: { events: TimelineEventType[] }) {
  return (
    <section className="rounded border border-slate-800 bg-slate-950 p-4">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-sm font-semibold text-white">System Timeline</h2>
        <span className="text-xs text-slate-500">{events.length} events</span>
      </div>
      <div className="max-h-[420px] space-y-2 overflow-y-auto pr-1">
        {events.length ? (
          events.slice(0, 12).map((event) => <TimelineItem key={event.id} event={event} />)
        ) : (
          <p className="text-sm text-slate-500">No events received yet.</p>
        )}
      </div>
    </section>
  );
}
