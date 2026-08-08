import type { GeneDrugFinding } from "../types/audit";
import { pubmedUrl } from "../display";

interface Props {
  finding: GeneDrugFinding;
}

export function FindingTier1({ finding }: Props) {
  const missingCitations = finding.citations.length === 0;

  return (
    <>
      {missingCitations && (
        <p className="citation-error">
          Citation: MISSING — Tier 1 requires a source
        </p>
      )}
      {finding.notes.length > 0 && (
        <ul className="notes-list">
          {finding.notes.map((note, i) => (
            <li key={i}>{note}</li>
          ))}
        </ul>
      )}
      {finding.citations.length > 0 && (
        <p>
          {finding.citations.map((pmid, i) => (
            <span key={pmid}>
              {i > 0 && ", "}
              <a href={pubmedUrl(pmid)} target="_blank" rel="noreferrer">
                PMID {pmid}
              </a>
            </span>
          ))}
        </p>
      )}
    </>
  );
}
