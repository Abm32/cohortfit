import type { Verdict } from "../types/audit";
import { verdictLabel } from "../display";

interface Props {
  verdict: Verdict;
}

export function VerdictBadge({ verdict }: Props) {
  const cls = verdict.toLowerCase().replace("_", "-");
  return (
    <span className={`verdict-badge verdict-${cls}`}>{verdictLabel(verdict)}</span>
  );
}
