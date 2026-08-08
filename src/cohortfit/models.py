"""Core data model.

The boundary between what Claude produces and what the deterministic engine
consumes. Claude fills `Protocol`; everything downstream is computed.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field

# --------------------------------------------------------------------------
# Extraction side — what Claude is allowed to produce
# --------------------------------------------------------------------------


class Site(BaseModel):
    """A planned trial site and the ancestry mix it is expected to recruit.

    `ancestry_mix` maps a population code (SAS, EUR, EAS, AFR, AMR) to its
    fraction of expected enrolment at this site. Fractions should sum to ~1.0.
    """

    name: str
    country: str
    planned_n: int
    ancestry_mix: dict[str, float]


class DoseRegimen(BaseModel):
    drug: str
    dose: str | None = None
    route: str | None = None
    schedule: str | None = None


class Protocol(BaseModel):
    """Structured protocol. This is Claude's only output surface."""

    trial_id: str | None = None
    title: str
    drugs: list[DoseRegimen]
    inclusion_criteria: list[str] = Field(default_factory=list)
    exclusion_criteria: list[str] = Field(default_factory=list)
    sites: list[Site] = Field(default_factory=list)
    target_n: int | None = None

    @property
    def total_planned_n(self) -> int:
        if self.target_n is not None:
            return self.target_n
        return sum(s.planned_n for s in self.sites)


# --------------------------------------------------------------------------
# Verdict side — what the deterministic engine produces
# --------------------------------------------------------------------------


class Verdict(str, Enum):
    """Findings inherit the platform's refusal discipline.

    CONTESTED is a real answer, not a hedge: it means the literature genuinely
    disagrees and the tool declines to invent a consensus.
    """

    ACTIONABLE = "ACTIONABLE"
    CONTESTED = "CONTESTED"
    NO_SIGNAL = "NO_SIGNAL"


class Tier(int, Enum):
    """What supports a claim.

    TIER_0 — arithmetic on pinned tables. Defensible without qualification.
    TIER_1 — needs a literature effect multiplier. Must carry a citation.
    TIER_2 — labelled scenario. Never presented as prediction.
    """

    DISTRIBUTION = 0
    BURDEN = 1
    SCENARIO = 2


class PhenotypeCount(BaseModel):
    """Expected number of enrollees in one phenotype class."""

    phenotype: str
    fraction: float
    expected_n: float


class PopulationCoverage(BaseModel):
    """Which ancestry groups the pinned frequency data actually covered.

    `blend_allele_frequencies` skips populations with no pinned data and
    renormalises the remaining weights. That is the honest arithmetic choice,
    but it is invisible in the resulting distribution: a US cohort declared
    68% EUR / 13% AFR / 19% AMR yields *exactly* the EUR-only numbers while
    still summing to 1.0. This record makes the omission part of the report,
    so a reader can tell a fully-covered cohort from a partially-covered one.

    Population-level counterpart to the "Indeterminate" phenotype bucket.
    """

    covered: dict[str, float] = Field(default_factory=dict)
    dropped: dict[str, float] = Field(default_factory=dict)

    @property
    def dropped_weight(self) -> float:
        """Total declared enrolment fraction with no pinned frequency data."""
        return sum(self.dropped.values())

    @property
    def is_complete(self) -> bool:
        return not self.dropped


class GeneDrugFinding(BaseModel):
    gene: str
    drug: str
    verdict: Verdict
    tier: Tier
    distribution: list[PhenotypeCount] = Field(default_factory=list)
    cpic_level: str | None = None
    missing_exclusion: str | None = None
    notes: list[str] = Field(default_factory=list)
    citations: list[str] = Field(default_factory=list)
    coverage: PopulationCoverage | None = None


class SiteFinding(BaseModel):
    """Per-site metabolic burden, used for site-selection deltas."""

    site_name: str
    gene: str
    at_risk_fraction: float
    expected_at_risk_n: float


class AuditReport(BaseModel):
    protocol_title: str
    trial_id: str | None = None
    total_planned_n: int
    findings: list[GeneDrugFinding] = Field(default_factory=list)
    site_findings: list[SiteFinding] = Field(default_factory=list)
    data_sources: list[str] = Field(default_factory=list)
    offline: bool = True
    warnings: list[str] = Field(default_factory=list)
