"""Per-site metabolic burden — site-selection deltas for CRO decisions.

Reruns the same Tier 0 math per ``Site`` instead of on the pooled cohort mix.
``at_risk_fraction`` is ancestry-driven; ``expected_at_risk_n`` scales by
``planned_n``.
"""

from __future__ import annotations

from .cohort import blend_allele_frequencies
from .models import PhenotypeCount, Site, SiteFinding
from .pgx import cohort_phenotype_distribution

_AT_RISK_PHENOTYPES = frozenset({"Poor Metabolizer", "Intermediate Metabolizer"})


def at_risk_fraction(distribution: list[PhenotypeCount]) -> float:
    """Fraction of a site cohort in IM or PM phenotype classes."""
    return sum(d.fraction for d in distribution if d.phenotype in _AT_RISK_PHENOTYPES)


def site_metabolic_burden(
    gene: str,
    per_pop_freqs: dict[str, dict[str, float]],
    sites: list[Site],
) -> list[SiteFinding]:
    """Compute per-site at-risk fraction and expected count for one gene.

    Each site uses its own ``ancestry_mix`` and ``planned_n`` — not the
    enrolment-weighted cohort blend.
    """
    findings: list[SiteFinding] = []
    for site in sites:
        site_blended = blend_allele_frequencies(per_pop_freqs, site.ancestry_mix)
        if not site_blended:
            continue
        site_dist, _ = cohort_phenotype_distribution(
            gene, site_blended, site.planned_n
        )
        rate = at_risk_fraction(site_dist)
        findings.append(
            SiteFinding(
                site_name=site.name,
                gene=gene,
                at_risk_fraction=rate,
                expected_at_risk_n=rate * site.planned_n,
            )
        )
    return findings


def rank_sites_by_burden(
    findings: list[SiteFinding],
    *,
    gene: str | None = None,
) -> list[SiteFinding]:
    """Return site findings sorted by ``at_risk_fraction`` descending."""
    filtered = [f for f in findings if gene is None or f.gene == gene]
    return sorted(filtered, key=lambda f: f.at_risk_fraction, reverse=True)


def burden_rate_ratio(a: SiteFinding, b: SiteFinding) -> float | None:
    """Rate ratio of site *a* over site *b* (ancestry-driven, not headcount).

    Returns None when the denominator rate is zero.
    """
    if b.at_risk_fraction == 0:
        return None
    return a.at_risk_fraction / b.at_risk_fraction
