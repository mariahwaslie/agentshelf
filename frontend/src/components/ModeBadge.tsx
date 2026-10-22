import type { AppMode } from "../api/client";

const LABELS: Record<AppMode, { text: string; hint: string }> = {
  live: {
    text: "Live sandbox",
    hint: "PayPal calls are live. Reused recordings of competitor or AI results are labeled.",
  },
  replay: { text: "Replay", hint: "Showing recorded API responses. No live calls are made." },
};

/** Always visible, so recorded results are never mistaken for live ones. */
export function ModeBadge({ mode }: { mode: AppMode }) {
  const { text, hint } = LABELS[mode];
  return (
    <span className="mode">
      <span className={`mode-badge mode-badge--${mode}`} aria-describedby="mode-hint">
        {text}
      </span>
      <span id="mode-hint" className="mode-hint">
        {hint}
      </span>
    </span>
  );
}
