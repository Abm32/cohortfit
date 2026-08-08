"""Provenance sensitivity — phenotype fractions as ranges, not point estimates.

The pinned SAS ``*2A`` frequency is a gnomAD v4 exome call that six other
published sources contradict, all upward (``_meta.known_discrepancies``).
Re-running Tier 0 at each candidate value shows the at-risk fraction moving
1.41x while Poor Metabolizer moves 10.1x (FINDINGS.md Findings 4 and 5), so PM
must be reported as an interval. This module produces that interval; it adds no
new data and no model, only re-runs the existing blend + HWE path.
"""

from __future__ import annotations

from typing import Any

from .cohort import blend_allele_frequencies
from .pgx import cohort_phenotype_distribution


def _candidate_values(value: Any) -> list[float]:
    """Numeric candidates from one conflicting_sources value.

    Accepts a number, or a ``"lo-hi"`` range string (one source publishes a
    range rather than a point). Anything else yields nothing — a value we
    cannot parse is skipped, never guessed at.
    """
    if isinstance(value, bool):
        return []
    if isinstance(value, (int, float)):
        return [float(value)]
    if isinstance(value, str):
        parts = value.split("-")
        if len(parts) == 2:
            try:
                return [float(parts[0]), float(parts[1])]
            except ValueError:
                return []
    return []


def discrepancy_candidates(provenance: dict) -> list[tuple[str, str, float]]:
    """Alternative (allele, population, frequency) triples worth testing.

    Drawn from every UNRESOLVED entry in ``known_discrepancies``; entries whose
    ``status`` starts with RESOLVED are already reconciled into the pinned value
    and would double-count. Sorted and deduplicated.
    """
    out: set[tuple[str, str, float]] = set()
    for entry in provenance.get("known_discrepancies", []):
        if str(entry.get("status", "")).strip().upper().startswith("RESOLVED"):
            continue
        allele, population = entry.get("allele"), entry.get("population")
        if not allele or not population:
            continue
        for raw in entry.get("conflicting_sources", {}).values():
            for freq in _candidate_values(raw):
                out.add((allele, population, freq))
    return sorted(out)


def substitute_allele(
    per_population: dict[str, dict[str, float]],
    population: str,
    allele: str,
    frequency: float,
    *,
    reference_allele: str = "*1",
) -> dict[str, dict[str, float]]:
    """Copy of *per_population* with one frequency swapped, ``*1`` re-derived.

    Hardy-Weinberg is only valid over a complete allele space, so the reference
    allele absorbs the change as the remainder and the population still sums to
    1.0. The input is never mutated; untouched populations are copied as-is.
    """
    out = {pop: dict(freqs) for pop, freqs in per_population.items()}
    if population not in out:
        raise KeyError(f"population {population!r} not in frequency table")
    out[population][allele] = frequency
    remainder = 1.0 - sum(f for a, f in out[population].items() if a != reference_allele)
    if remainder < 0:
        raise ValueError(
            f"{population}/{allele}={frequency} leaves no room for {reference_allele}"
        )
    out[population][reference_allele] = remainder
    return out


def phenotype_bounds(
    gene: str,
    per_population: dict[str, dict[str, float]],
    ancestry_mix: dict[str, float],
    planned_n: int,
    provenance: dict,
) -> dict[str, tuple[float, float]]:
    """phenotype -> (min, max) fraction across the pinned and candidate values.

    Empty when nothing is unresolved: no disagreement, no range to report. A
    phenotype absent from one scenario counts as 0.0 there, so the low bound
    reflects scenarios where the phenotype does not appear at all.
    """
    scenarios = [per_population]
    for allele, population, freq in discrepancy_candidates(provenance):
        if population in per_population:
            scenarios.append(substitute_allele(per_population, population, allele, freq))
    if len(scenarios) == 1:
        return {}

    fractions: list[dict[str, float]] = []
    for scenario in scenarios:
        blended = blend_allele_frequencies(scenario, ancestry_mix)
        if not blended:
            continue
        dist, _ = cohort_phenotype_distribution(gene, blended, planned_n)
        fractions.append({d.phenotype: d.fraction for d in dist})

    phenotypes = {p for f in fractions for p in f}
    return {
        pheno: (
            min(f.get(pheno, 0.0) for f in fractions),
            max(f.get(pheno, 0.0) for f in fractions),
        )
        for pheno in sorted(phenotypes)
    }
