/** AuditReport contract — mirrors src/cohortfit/models.py */

export type Verdict = "ACTIONABLE" | "CONTESTED" | "NO_SIGNAL";
export type Tier = 0 | 1 | 2;

export interface PhenotypeCount {
  phenotype: string;
  fraction: number;
  expected_n: number;
}

export interface PopulationCoverage {
  covered: Record<string, number>;
  dropped: Record<string, number>;
}

export interface GeneDrugFinding {
  gene: string;
  drug: string;
  verdict: Verdict;
  tier: Tier;
  distribution: PhenotypeCount[];
  cpic_level: string | null;
  missing_exclusion: string | null;
  notes: string[];
  citations: string[];
  coverage?: PopulationCoverage | null;
}

export interface SiteFinding {
  site_name: string;
  gene: string;
  at_risk_fraction: number;
  expected_at_risk_n: number;
}

export interface AuditReport {
  protocol_title: string;
  trial_id: string | null;
  total_planned_n: number;
  findings: GeneDrugFinding[];
  site_findings: SiteFinding[];
  data_sources: string[];
  offline: boolean;
  warnings: string[];
}

export interface Protocol {
  trial_id?: string | null;
  title: string;
  drugs: { drug: string; dose?: string | null; route?: string | null; schedule?: string | null }[];
  inclusion_criteria?: string[];
  exclusion_criteria?: string[];
  sites?: {
    name: string;
    country: string;
    planned_n: number;
    ancestry_mix: Record<string, number>;
  }[];
  target_n?: number | null;
}

export interface ProvenanceResponse {
  meta: Record<string, unknown>;
  known_discrepancies: unknown[];
  populations: Record<string, Record<string, unknown>>;
  ground_truth: Record<string, unknown>;
}

export interface ApiError {
  detail: string | { loc: string[]; msg: string; type: string }[];
}
