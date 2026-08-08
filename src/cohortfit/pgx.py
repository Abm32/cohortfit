"""Table-direct diplotype → phenotype adapter.

Loads pinned CPIC named-diplotype JSON from the installed anukriti-pgx-core
package. No PhenotypeEngine, no VCF variants — the cohort path already has
star alleles from Hardy-Weinberg expansion.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass
from importlib import resources
from itertools import combinations_with_replacement

from .cohort import diplotype_frequencies, phenotype_distribution
from .models import PhenotypeCount

# Default named-diplotype table per gene (pgx-core 0.7.1 pin).
_DEFAULT_TABLE_FILES: dict[str, str] = {
    "DPYD": "DPYD_diplotypes_anukriti_v2024.01.json",
}


class PgxTableError(ValueError):
    """Raised when a diplotype table cannot be loaded or is unsupported."""


@dataclass(frozen=True)
class DiplotypeTable:
    """Pinned CPIC named-diplotype table for one gene."""

    gene: str
    table_id: str
    source: str
    version: str
    diplotype_phenotypes: dict[str, str]


def _table_filename(gene: str, table_id: str | None) -> str:
    gene_upper = gene.upper()
    if table_id is not None:
        if table_id.endswith(".json"):
            return table_id
        return f"{gene_upper}_{table_id}.json"
    try:
        return _DEFAULT_TABLE_FILES[gene_upper]
    except KeyError as exc:
        supported = ", ".join(sorted(_DEFAULT_TABLE_FILES))
        raise PgxTableError(
            f"Unsupported gene {gene_upper!r}; supported: {supported}"
        ) from exc


def load_diplotype_table(gene: str, *, table_id: str | None = None) -> DiplotypeTable:
    """Load a pinned named-diplotype table from anukriti-pgx-core."""
    filename = _table_filename(gene, table_id)
    try:
        raw = resources.files("anukriti_pgx_core.phenotype.tables").joinpath(filename).read_text(
            encoding="utf-8"
        )
    except (FileNotFoundError, TypeError, OSError) as exc:
        raise PgxTableError(f"Cannot load diplotype table {filename!r}: {exc}") from exc

    data = json.loads(raw)
    diplotype_phenotypes = {k: v for k, v in data.items() if not k.startswith("_")}
    stem = filename.removesuffix(".json")

    return DiplotypeTable(
        gene=gene.upper(),
        table_id=stem,
        source=str(data.get("_source", "")),
        version=str(data.get("_version", "")),
        diplotype_phenotypes=diplotype_phenotypes,
    )


def lookup_phenotype(table: DiplotypeTable, allele_a: str, allele_b: str) -> str:
    """Resolve phenotype for a diplotype; unmapped → Indeterminate."""
    for key in (f"{allele_a}/{allele_b}", f"{allele_b}/{allele_a}"):
        if key in table.diplotype_phenotypes:
            return table.diplotype_phenotypes[key]
    return "Indeterminate"


def phenotype_map_for_alleles(
    table: DiplotypeTable,
    alleles: Iterable[str],
) -> dict[tuple[str, str], str]:
    """Build phenotype_of dict keyed like diplotype_frequencies() output."""
    return {
        (a, b): lookup_phenotype(table, a, b)
        for a, b in combinations_with_replacement(sorted(alleles), 2)
    }


def table_citation(table: DiplotypeTable) -> str:
    """Human-readable citation string for AuditReport.data_sources."""
    parts = [f"CPIC {table.gene} diplotype table {table.table_id}"]
    if table.source:
        parts.append(f"({table.source})")
    if table.version:
        parts.append(f"v{table.version}")
    return " ".join(parts)


def cohort_phenotype_distribution(
    gene: str,
    allele_freqs: dict[str, float],
    planned_n: int,
) -> tuple[list[PhenotypeCount], DiplotypeTable]:
    """Compose HWE expansion + table lookup into a cohort phenotype distribution."""
    table = load_diplotype_table(gene)
    pheno_map = phenotype_map_for_alleles(table, allele_freqs.keys())
    diplo = diplotype_frequencies(allele_freqs)
    return phenotype_distribution(diplo, pheno_map, planned_n), table
