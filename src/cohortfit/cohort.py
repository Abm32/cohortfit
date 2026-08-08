"""Tier 0 cohort engine — Hardy-Weinberg diplotype expansion.

This is the load-bearing, fully defensible layer: given allele frequencies for a
population, compute expected diplotype frequencies, then map them to phenotypes
using pinned CPIC tables.

No LLM is involved past this module's inputs. No network calls. Pure arithmetic.
"""

from __future__ import annotations

from itertools import combinations_with_replacement

from .models import PhenotypeCount, Site


def diplotype_frequencies(allele_freqs: dict[str, float]) -> dict[tuple[str, str], float]:
    """Expand allele frequencies into diplotype frequencies under Hardy-Weinberg.

    For alleles i != j the unordered heterozygote frequency is 2*p_i*p_j;
    for i == j the homozygote frequency is p_i^2.

    Args:
        allele_freqs: allele label -> frequency. Should sum to ~1.0; the caller
            is responsible for including a reference/wildtype allele so that it
            does.

    Returns:
        Mapping of sorted (allele, allele) tuple -> expected frequency.
    """
    out: dict[tuple[str, str], float] = {}
    for a, b in combinations_with_replacement(sorted(allele_freqs), 2):
        p, q = allele_freqs[a], allele_freqs[b]
        out[(a, b)] = p * p if a == b else 2 * p * q
    return out


def cohort_ancestry_mix(sites: list[Site]) -> dict[str, float]:
    """Collapse per-site ancestry mixes into one enrolment-weighted mix.

    Weighted by each site's planned_n, so a large site dominates the expected
    cohort composition as it should.
    """
    totals: dict[str, float] = {}
    denom = sum(s.planned_n for s in sites)
    if denom == 0:
        return {}
    for site in sites:
        for pop, frac in site.ancestry_mix.items():
            totals[pop] = totals.get(pop, 0.0) + frac * site.planned_n
    return {pop: weight / denom for pop, weight in totals.items()}


def blend_allele_frequencies(
    per_population: dict[str, dict[str, float]],
    ancestry_mix: dict[str, float],
) -> dict[str, float]:
    """Blend population-specific allele frequencies by ancestry mix.

    Populations present in `ancestry_mix` but absent from `per_population` are
    skipped and the remaining weights renormalised — an honest partial answer
    beats a silently wrong one.
    """
    usable = {p: w for p, w in ancestry_mix.items() if p in per_population}
    total_weight = sum(usable.values())
    if total_weight == 0:
        return {}

    blended: dict[str, float] = {}
    for pop, weight in usable.items():
        share = weight / total_weight
        for allele, freq in per_population[pop].items():
            blended[allele] = blended.get(allele, 0.0) + freq * share
    return blended


def phenotype_distribution(
    diplotype_freqs: dict[tuple[str, str], float],
    phenotype_of: dict[tuple[str, str], str],
    planned_n: int,
) -> list[PhenotypeCount]:
    """Aggregate diplotype frequencies into a phenotype distribution.

    Diplotypes with no phenotype mapping are aggregated under "Indeterminate"
    rather than dropped. Dropping them would silently inflate the confidence of
    everything else.
    """
    by_phenotype: dict[str, float] = {}
    for diplotype, freq in diplotype_freqs.items():
        pheno = phenotype_of.get(diplotype, "Indeterminate")
        by_phenotype[pheno] = by_phenotype.get(pheno, 0.0) + freq

    return [
        PhenotypeCount(
            phenotype=pheno,
            fraction=frac,
            expected_n=frac * planned_n,
        )
        for pheno, frac in sorted(by_phenotype.items(), key=lambda kv: -kv[1])
    ]
