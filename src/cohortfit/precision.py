"""Sampling precision — how well the reference panel measured each allele.

Implements FINDINGS.md Findings 9 and 11. Every non-reference allele record in
the fixture already carries ``alt_observed`` and ``total_alleles``: a binomial
numerator and denominator. That is enough for a Wilson score interval, so the
precision of each pinned frequency is computable with no new data.

Two things this makes visible that the point estimate cannot:

* **Unequal precision.** The rare SAS alleles are measured to roughly ±58%
  relative width against ±5% for their European counterparts, because the
  reference panel holds ~45.5k South Asian individuals against ~590k
  Non-Finnish European. Identically-formatted numbers are not equally trustworthy
  and the report should not imply that they are.
* **Observed zero vs absent.** ``*13`` is pinned at 0.0 for SAS on 0/91,074
  observations. By the rule of three that allele could still be as frequent as
  0.0033% and simply never have been seen. "Not observed" and "absent" are
  different claims; only the first is supported.

Deliberately *not* folded into the Tier 0 distribution. FINDINGS.md Finding 10
measured provenance uncertainty at 6.2x the sampling width for SAS, so the
range that ships on ``PhenotypeCount`` is the provenance one (``sensitivity``).
This module reports sampling precision alongside it rather than compounding the
two into a single interval that would mean neither.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

__all__ = [
    "RULE_OF_THREE",
    "AllelePrecision",
    "allele_precision",
    "detection_floor",
    "population_precision",
    "precision_notes",
    "wilson_interval",
]

# z for a two-sided 95% interval.
_Z_95 = 1.959963984540054

# Numerator of the rule-of-three upper bound: with zero observations in n
# trials, the true rate is below 3/n at ~95% confidence.
RULE_OF_THREE = 3.0

# Relative CI width above which an estimate is flagged as imprecise. 0.25 is a
# judgement call, not a standard: it separates the DPYD SAS rare alleles (~0.58)
# from their EUR counterparts (~0.05) with room on both sides.
_IMPRECISE_RELATIVE_WIDTH = 0.25


def _pct(fraction: float) -> str:
    """Percent with enough significant figures that rare alleles do not read as zero.

    Mirrors the intent of ``display.format_fraction`` but is kept local: this
    module reports frequencies (which run to 1e-5), not phenotype fractions.
    """
    pct = fraction * 100
    if pct == 0:
        return "0%"
    if pct < 0.001:
        return f"{pct:.5f}%"
    if pct < 0.01:
        return f"{pct:.4f}%"
    if pct < 1:
        return f"{pct:.3f}%"
    return f"{pct:.2f}%"


@dataclass(frozen=True)
class AllelePrecision:
    """Sampling precision of one pinned allele frequency."""

    allele: str
    population: str
    frequency: float
    alt_observed: int
    total_alleles: int
    ci_low: float
    ci_high: float

    @property
    def observed(self) -> bool:
        """Whether the allele was seen at all in this population's sample."""
        return self.alt_observed > 0

    @property
    def detection_floor(self) -> float:
        """Rule-of-three upper bound for this allele's sample size.

        Meaningful only when the allele was never observed: it is the highest
        frequency consistent with seeing zero copies in this many alleles.
        """
        return detection_floor(self.total_alleles)

    @property
    def relative_width(self) -> float | None:
        """CI width as a fraction of the point estimate.

        ``None`` when the point estimate is zero — a relative width against zero
        is undefined, and ``detection_floor`` is the meaningful quantity there
        instead.
        """
        if self.frequency == 0:
            return None
        return (self.ci_high - self.ci_low) / self.frequency

    @property
    def imprecise(self) -> bool:
        """True when the interval is wide enough to distrust the point estimate."""
        width = self.relative_width
        return width is not None and width > _IMPRECISE_RELATIVE_WIDTH

    def describe(self) -> str:
        """Human-readable one-liner for report notes."""
        if not self.observed:
            return (
                f"{self.allele} was not observed in {self.total_alleles:,} "
                f"{self.population} alleles — pinned 0.0 means not detected, not "
                f"absent (95% upper bound {_pct(self.detection_floor)}, rule of three)"
            )
        return (
            f"{self.allele} {self.population} {_pct(self.frequency)} "
            f"[{_pct(self.ci_low)}, {_pct(self.ci_high)}] "
            f"on {self.total_alleles:,} alleles"
        )


def wilson_interval(
    successes: int,
    trials: int,
    *,
    z: float = _Z_95,
) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion.

    Preferred over the normal approximation because allele frequencies here are
    small enough that ``p ± z·sqrt(p(1-p)/n)`` produces negative lower bounds —
    an impossible frequency, which would then break the sum-to-one invariant if
    it ever reached Hardy-Weinberg.

    With zero successes the interval starts at exactly 0.0. Its upper bound is
    then ``z²/(n + z²)`` ≈ ``3.84/n``, which is close to but not the same as the
    rule-of-three ``3/n`` — ``detection_floor()`` is the one the report quotes,
    because that is the bound the documented provenance tables were computed
    with.
    """
    if trials <= 0:
        raise ValueError("trials must be positive")
    if successes < 0 or successes > trials:
        raise ValueError(f"successes {successes} out of range for {trials} trials")

    p = successes / trials
    denom = 1 + z * z / trials
    centre = (p + z * z / (2 * trials)) / denom
    half = z * math.sqrt(p * (1 - p) / trials + z * z / (4 * trials * trials)) / denom
    return max(0.0, centre - half), min(1.0, centre + half)


def detection_floor(trials: int) -> float:
    """Highest frequency consistent with zero observations, by the rule of three.

    An allele at or below this frequency can plausibly be missed entirely by a
    sample of this size, so a pinned 0.0 carries no information below it.
    """
    if trials <= 0:
        raise ValueError("trials must be positive")
    return RULE_OF_THREE / trials


def allele_precision(
    allele: str,
    population: str,
    record: dict,
) -> AllelePrecision | None:
    """Precision for one fixture allele record, or None if it lacks counts.

    The reference allele is a computed remainder rather than an observation, so
    it has no counts and no sampling interval — returning None keeps that
    distinction rather than inventing one.
    """
    if "alt_observed" not in record or "total_alleles" not in record:
        return None

    observed = int(record["alt_observed"])
    total = int(record["total_alleles"])
    low, high = wilson_interval(observed, total)
    return AllelePrecision(
        allele=allele,
        population=population,
        frequency=float(record.get("frequency", observed / total if total else 0.0)),
        alt_observed=observed,
        total_alleles=total,
        ci_low=low,
        ci_high=high,
    )


def population_precision(provenance: dict) -> dict[str, list[AllelePrecision]]:
    """Per-population precision for every allele carrying observation counts.

    Takes the mapping returned by ``frequencies.load_gene_provenance()``.
    """
    out: dict[str, list[AllelePrecision]] = {}
    for population, alleles in provenance.get("populations", {}).items():
        entries = [
            precision
            for allele, record in sorted(alleles.items())
            if isinstance(record, dict)
            and (precision := allele_precision(allele, population, record)) is not None
        ]
        if entries:
            out[population] = entries
    return out


def precision_notes(
    precision: dict[str, list[AllelePrecision]],
    populations: set[str] | None = None,
) -> list[str]:
    """Notes for alleles that are imprecise or unobserved in the cohort's populations.

    Restricted to populations that actually contribute to the cohort, so a
    report does not carry caveats about ancestry groups it never used. Precise,
    observed alleles produce no note — the point estimate speaks for itself.
    """
    notes: list[str] = []
    for population in sorted(precision):
        if populations is not None and population not in populations:
            continue
        for entry in precision[population]:
            if not entry.observed or entry.imprecise:
                notes.append(entry.describe() + ".")
    return notes
