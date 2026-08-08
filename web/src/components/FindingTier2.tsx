import type { GeneDrugFinding } from "../types/audit";

interface Props {
  finding: GeneDrugFinding;
}

export function FindingTier2({ finding }: Props) {
  return (
    <>
      {finding.notes.length > 0 && (
        <ul className="notes-list">
          {finding.notes.map((note, i) => (
            <li key={i}>{note}</li>
          ))}
        </ul>
      )}
      <p className="disclaimer">
        Scenario analysis — directional only, not a prediction of trial outcome.
      </p>
    </>
  );
}
