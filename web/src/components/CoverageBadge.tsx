import type { PopulationCoverage } from "../types/audit";

interface Props {
  coverage: PopulationCoverage;
  notes?: string[];
}

export function CoverageBadge({ coverage, notes = [] }: Props) {
  const dropped = Object.entries(coverage.dropped);
  if (dropped.length === 0) return null;

  const droppedLabel = dropped
    .map(([pop, frac]) => `${pop} (${(frac * 100).toFixed(0)}%)`)
    .join(", ");

  return (
    <div>
      <span className="coverage-badge">
        Partial coverage — no pinned frequencies for: {droppedLabel}
      </span>
      {notes.map((note, i) => (
        <p key={i} className="footnote">
          {note}
        </p>
      ))}
    </div>
  );
}
