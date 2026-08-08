"""Pinned population allele frequencies.

Offline fixture, not a live query. Values are gnomAD v2.1.1 exome allele
frequencies for the rsid defining each CPIC star allele, keyed by gnomAD
population code (AFR, EUR, EAS, SAS, AMR). `"*1"` is the reference/wildtype
allele and is not observed directly — its frequency is derived as
`1 - sum(other alleles)` so each population's distribution sums to 1.0,
per the contract of `cohort.diplotype_frequencies`.

Scope for the Tier 0 demo: DPYD only.
"""

from __future__ import annotations

# gnomAD v2.1.1 exome allele frequency, by rsid, by population.
_GNOMAD_v2_1_1: dict[str, dict[str, float]] = {
    "rs3918290": {  # DPYD*2A — no function
        "AFR": 0.003, "EUR": 0.012, "EAS": 0.001, "SAS": 0.006, "AMR": 0.008,
    },
    "rs67376798": {  # DPYD c.2846A>T — decreased function
        "AFR": 0.004, "EUR": 0.008, "EAS": 0.002, "SAS": 0.006, "AMR": 0.006,
    },
    "rs56038477": {  # DPYD HapB3 — decreased function
        "AFR": 0.004, "EUR": 0.042, "EAS": 0.001, "SAS": 0.012, "AMR": 0.018,
    },
}

# rsid -> CPIC star allele it defines.
_DPYD_ALLELE_BY_RSID = {
    "rs3918290": "*2A",
    "rs67376798": "c.2846A>T",
    "rs56038477": "HapB3",
}

POPULATIONS = ("AFR", "EUR", "EAS", "SAS", "AMR")


def population_allele_frequencies(gene: str, population: str) -> dict[str, float]:
    """Pinned allele frequencies for `gene` in `population`, including *1.

    Raises KeyError if `gene` has no pinned table.
    """
    if gene != "DPYD":
        raise KeyError(f"no pinned allele frequency table for gene {gene!r}")

    variants = {
        _DPYD_ALLELE_BY_RSID[rsid]: freqs[population]
        for rsid, freqs in _GNOMAD_v2_1_1.items()
    }
    variants["*1"] = 1.0 - sum(variants.values())
    return variants


def per_population_table(gene: str) -> dict[str, dict[str, float]]:
    """Pinned allele frequencies for `gene`, for every population with data."""
    return {pop: population_allele_frequencies(gene, pop) for pop in POPULATIONS}
