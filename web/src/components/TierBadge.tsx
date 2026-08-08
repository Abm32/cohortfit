import type { Tier } from "../types/audit";
import { tierLabel } from "../display";

interface Props {
  tier: Tier;
}

export function TierBadge({ tier }: Props) {
  return <span className={`tier-badge tier-${tier}`}>{tierLabel(tier)}</span>;
}
