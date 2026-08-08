"""Panel coverage concentration — how many alleles a gene panel really tests.

Implements FINDINGS.md Findings 1 and 2. A four-variant panel is only a
four-variant panel where all four fire: in SAS, DPYD collapses to 1.12
effective alleles with 94% of the actionable burden on HapB3 alone.

Two independent measures, deliberately kept apart:

* ``panel_concentration`` is pure allele-frequency arithmetic (Herfindahl over
  the variant pool) — cheap, and says nothing about phenotype.
* ``burden_shares`` is leave-one-out ablation through the real Tier 0 pipeline
  — expensive, and is what actually attributes IM+PM risk.

They agree closely for DPYD, but the second is the one to quote.
"""

from __future__ import annotations

from dataclasses import dataclass

from .pgx import cohort_phenotype_distribution
from .sites import at_risk_fraction  # re-exported below; same IM+PM sum, one definition

__all__ = [
    "PanelConcentration",
    "at_risk_fraction",
    "burden_shares",
    "coverage_note",
    "panel_concentration",
]

# Ablation reruns the Tier 0 distribution; planned_n only scales expected_n,
# which we discard, so any positive value works. 1000 matches _ground_truth.
_ABLATION_N = 1000


@dataclass(frozen=True)
class PanelConcentration:
    """Herfindahl concentration of one population's variant allele pool."""

    total_variant_load: float
    hhi: float
    effective_alleles: float
    dominant_allele: str | None
    dominant_share: float
    silent_alleles: tuple[str, ...]


def panel_concentration(
    allele_freqs: dict[str, float],
    *,
    reference_allele: str = "*1",
) -> PanelConcentration:
    """Measure how concentrated the non-reference allele pool is.

    Shares are of the variant pool, not of the population, so a panel where one
    variant dominates scores the same whether that variant is common or rare.
    An all-reference population has no pool: everything comes back zero rather
    than dividing by it.
    """
    variants = {a: f for a, f in allele_freqs.items() if a != reference_allele}
    total = sum(variants.values())
    silent = tuple(sorted(a for a, f in variants.items() if f == 0.0))
    if total == 0:
        return PanelConcentration(0.0, 0.0, 0.0, None, 0.0, silent)

    hhi = sum((f / total) ** 2 for f in variants.values())
    dominant = max(variants, key=lambda a: variants[a])
    return PanelConcentration(
        total_variant_load=total,
        hhi=hhi,
        effective_alleles=1 / hhi,
        dominant_allele=dominant,
        dominant_share=variants[dominant] / total,
        silent_alleles=silent,
    )


def burden_shares(
    gene: str,
    allele_freqs: dict[str, float],
    *,
    reference_allele: str = "*1",
) -> dict[str, float]:
    """Leave-one-out ablation: each variant allele's share of actionable burden.

    Drops one allele at a time and gives its frequency back to the reference,
    preserving the sum-to-one invariant ``diplotype_frequencies()`` requires,
    then attributes the drop in at-risk fraction to the removed allele.

    Returns allele -> share of baseline IM+PM burden, empty when the baseline
    at-risk fraction is zero (nothing to apportion).
    """
    baseline = _at_risk(gene, allele_freqs)
    if baseline == 0:
        return {}

    shares: dict[str, float] = {}
    for allele, freq in allele_freqs.items():
        if allele == reference_allele:
            continue
        ablated = {a: f for a, f in allele_freqs.items() if a != allele}
        ablated[reference_allele] = ablated.get(reference_allele, 0.0) + freq
        shares[allele] = (baseline - _at_risk(gene, ablated)) / baseline
    return shares


def coverage_note(concentration: PanelConcentration, shares: dict[str, float]) -> str:
    """One-sentence panel coverage note for AuditReport finding notes."""
    parts = [f"Panel concentration: {concentration.effective_alleles:.2f} effective alleles"]
    dominant = concentration.dominant_allele
    if dominant is not None:
        share = shares.get(dominant, concentration.dominant_share)
        parts.append(f"{dominant} carries {share:.1%} of actionable burden")
    if concentration.silent_alleles:
        never = ", ".join(concentration.silent_alleles)
        parts.append(f"{never} never fires (pinned frequency 0.0)")
    return "; ".join(parts) + "."


def _at_risk(gene: str, allele_freqs: dict[str, float]) -> float:
    distribution, _ = cohort_phenotype_distribution(gene, allele_freqs, _ABLATION_N)
    return at_risk_fraction(distribution)
