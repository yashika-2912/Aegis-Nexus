export function compactNumber(value: number): string {
  return new Intl.NumberFormat("en", { notation: "compact" }).format(value);
}

export function percentage(value: number): string {
  return `${Math.round(value)}%`;
}

export function milliseconds(value: number): string {
  return `${Math.round(value)}ms`;
}

export function timeLabel(timestamp: string): string {
  return new Intl.DateTimeFormat("en", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  }).format(new Date(timestamp));
}
