import type { AppMode } from "../api/client";

const LABELS: Record<AppMode, { text: string; hint: string }> = {
  live: { text: "Live sandbox", hint: "Calls go to the PayPal sandbox and real services." },
  replay: { text: "Replay", hint: "Showing recorded API responses. No live calls are made." },
};

/** Always visible, so cached results are never mistaken for live ones. */
export function ModeBadge({ mode }: { mode: AppMode }) {
  const { text, hint } = LABELS[mode];
  return (
    <span className={`mode-badge mode-badge--${mode}`} title={hint}>
      {text}
    </span>
  );
}
