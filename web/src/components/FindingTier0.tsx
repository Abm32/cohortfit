import type { GeneDrugFinding } from "../types/audit";
import { pubmedUrl } from "../display";
import { CoverageBadge } from "./CoverageBadge";
import { DistributionTable } from "./DistributionTable";

interface Props {
  finding: GeneDrugFinding;
}

export function FindingTier0({ finding }: Props) {
  return (
    <>
      {finding.coverage && (
        <CoverageBadge coverage={finding.coverage} notes={finding.notes} />
      )}
      <DistributionTable rows={finding.distribution} />
      {finding.cpic_level && (
        <p>
          <strong>CPIC Level {finding.cpic_level}</strong>
        </p>
      )}
      {finding.missing_exclusion && (
        <p className="notes-list" style={{ listStyle: "none", padding: 0 }}>
          {finding.missing_exclusion}
        </p>
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
