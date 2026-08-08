import type { GeneDrugFinding } from "../types/audit";
import { tierSubtitle } from "../display";
import { FindingTier0 } from "./FindingTier0";
import { FindingTier1 } from "./FindingTier1";
import { FindingTier2 } from "./FindingTier2";
import { TierBadge } from "./TierBadge";
import { VerdictBadge } from "./VerdictBadge";

interface Props {
  finding: GeneDrugFinding;
}

export function FindingCard({ finding }: Props) {
  return (
    <article className={`finding-card tier-${finding.tier}-border`}>
      <div className="finding-header">
        <span className="finding-title">
          {finding.gene} × {finding.drug}
        </span>
        <TierBadge tier={finding.tier} />
        <VerdictBadge verdict={finding.verdict} />
      </div>
      <p className="tier-subtitle">{tierSubtitle(finding.tier)}</p>
      {finding.tier === 0 && <FindingTier0 finding={finding} />}
      {finding.tier === 1 && <FindingTier1 finding={finding} />}
      {finding.tier === 2 && <FindingTier2 finding={finding} />}
    </article>
  );
}
