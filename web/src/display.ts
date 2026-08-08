/** Display formatters — parity with src/cohortfit/display.py (no audit math). */

import type { Tier, Verdict } from "./types/audit";

const TIER_LABELS: Record<Tier, string> = {
  0: "TIER 0",
  1: "TIER 1",
  2: "SCENARIO",
};

const TIER_SUBTITLES: Record<Tier, string> = {
  0: "Arithmetic on pinned tables + HWE",
  1: "Literature effect multiplier — citation required",
  2: "Directional only — not a prediction",
};

export function tierLabel(tier: Tier): string {
  return TIER_LABELS[tier];
}

export function tierSubtitle(tier: Tier): string {
  return TIER_SUBTITLES[tier];
}

export function verdictLabel(verdict: Verdict): string {
  return verdict;
}

export function formatFraction(fraction: number): string {
  const pct = fraction * 100;
  if (pct === 0) return "0%";
  if (pct < 0.01) return `${pct.toFixed(3)}%`;
  if (pct < 1) return `${pct.toFixed(2)}%`;
  return `${pct.toFixed(1)}%`;
}

export function formatExpectedN(expectedN: number): string {
  if (expectedN === 0) return "0";
  if (expectedN < 0.1) return expectedN.toFixed(2);
  return expectedN.toFixed(1);
}

export function formatAtRiskRate(fraction: number): string {
  return `${(fraction * 100).toFixed(2)}%`;
}

export function pubmedUrl(pmid: string): string {
  if (/^\d+$/.test(pmid)) {
    return `https://pubmed.ncbi.nlm.nih.gov/${pmid}/`;
  }
  return pmid;
}

export function inferPlannedN(expectedAtRiskN: number, atRiskFraction: number): number {
  if (atRiskFraction <= 0) return 0;
  return Math.round(expectedAtRiskN / atRiskFraction);
}

export function formatCitationList(citations: string[], required = false): string {
  if (citations.length === 0) {
    return required ? "Citation: MISSING — Tier 1 requires a source" : "";
  }
  const cites = citations.map((c) => (/^\d+$/.test(c) ? `PMID ${c}` : c)).join(", ");
  const prefix = required ? "Citation (required)" : "Citation";
  return `${prefix}: ${cites}`;
}
