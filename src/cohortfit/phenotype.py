"""Diplotype -> phenotype, via anukriti-pgx-core's pinned CPIC tables.

This is the only place cohortfit calls into pgx-core. No frequency or
phenotype number is computed here or anywhere else in this codebase — it is
looked up.
"""

from __future__ import annotations

from anukriti_pgx_core import PhenotypeEngine

_engine = PhenotypeEngine()


def phenotype_map(gene: str, diplotypes: list[tuple[str, str]]) -> dict[tuple[str, str], str]:
    """Look up the CPIC phenotype for each (allele, allele) diplotype.

    Diplotypes pgx-core doesn't recognise (e.g. a *1/*1-adjacent combination
    with no CPIC table entry) come back as "Indeterminate" rather than
    raising, matching `cohort.phenotype_distribution`'s own fallback.
    """
    return {dt: _engine.infer(gene, dt[0], dt[1]).phenotype for dt in diplotypes}
