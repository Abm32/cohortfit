"""Pinned population allele-frequency fixtures.

Runtime loads JSON from ``fixtures/frequencies/`` — no network, no LLM.
Every allele must carry provenance or be an explicit computed_remainder *1.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
_FIXTURES_DIR = _REPO_ROOT / "fixtures" / "frequencies"

_REQUIRED_PROVENANCE = frozenset({"source", "rsid"})
_COMPUTED_SOURCES = frozenset({"computed_remainder"})


class FixtureError(ValueError):
    """Pinned frequency data is missing, incomplete, or internally inconsistent."""


def fixture_path(gene: str) -> Path:
    """Return the pinned JSON path for a gene symbol."""
    return _FIXTURES_DIR / f"{gene.lower()}.json"


def load_fixture(gene: str, *, offline: bool = True) -> dict[str, Any]:
    """Load the raw fixture document for a gene.

    ``offline`` is accepted for API symmetry with the CLI; fixtures are
    always read from disk.
    """
    _ = offline
    path = fixture_path(gene)
    if not path.is_file():
        raise FixtureError(f"No frequency fixture for gene {gene!r} at {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def validate_fixture(data: dict[str, Any]) -> None:
    """Ensure provenance completeness and that allele frequencies sum to 1.0."""
    populations = data.get("populations")
    if not isinstance(populations, dict) or not populations:
        raise FixtureError("fixture must contain a non-empty 'populations' object")

    for pop_code, pop_data in populations.items():
        alleles = pop_data.get("alleles")
        if not isinstance(alleles, dict) or not alleles:
            raise FixtureError(f"population {pop_code!r} has no 'alleles'")

        if "*1" not in alleles:
            raise FixtureError(f"population {pop_code!r} missing required *1 reference allele")

        for allele, record in alleles.items():
            if not isinstance(record, dict):
                raise FixtureError(f"{pop_code}/{allele}: allele record must be an object")
            source = record.get("source")
            if not source:
                raise FixtureError(f"{pop_code}/{allele}: missing 'source'")
            if source in _COMPUTED_SOURCES:
                if allele != "*1":
                    raise FixtureError(f"{pop_code}/{allele}: only *1 may use computed_remainder")
                continue
            missing = _REQUIRED_PROVENANCE - set(record)
            if missing:
                raise FixtureError(
                    f"{pop_code}/{allele}: incomplete provenance, missing {sorted(missing)}"
                )
            if "alt_observed" not in record or "total_alleles" not in record:
                raise FixtureError(
                    f"{pop_code}/{allele}: non-*1 allele must include alt_observed and total_alleles"
                )

        total = sum(float(record["frequency"]) for record in alleles.values())
        if abs(total - 1.0) > 1e-6:
            raise FixtureError(
                f"population {pop_code!r} allele frequencies sum to {total}, expected 1.0"
            )


def load_gene_frequencies(gene: str, *, offline: bool = True) -> dict[str, dict[str, float]]:
    """Return ``{population: {allele: frequency}}`` for blend_allele_frequencies()."""
    data = load_fixture(gene, offline=offline)
    validate_fixture(data)
    out: dict[str, dict[str, float]] = {}
    for pop_code, pop_data in data["populations"].items():
        out[pop_code] = {
            allele: float(record["frequency"])
            for allele, record in pop_data["alleles"].items()
        }
    return out


def load_gene_provenance(gene: str, *, offline: bool = True) -> dict[str, Any]:
    """Return fixture metadata and per-allele provenance for audit reports."""
    data = load_fixture(gene, offline=offline)
    validate_fixture(data)
    meta = data.get("_meta", {})
    populations: dict[str, Any] = {}
    for pop_code, pop_data in data["populations"].items():
        populations[pop_code] = pop_data.get("alleles", {})
    ground_truth = data.get("_ground_truth")
    return {
        "gene": meta.get("gene", gene),
        "meta": meta,
        "populations": populations,
        "ground_truth": ground_truth,
    }


def data_source_labels(gene: str, *, offline: bool = True) -> list[str]:
    """Short strings suitable for AuditReport.data_sources."""
    prov = load_gene_provenance(gene, offline=offline)
    meta = prov["meta"]
    version = meta.get("gnomad_version", "unknown")
    date = meta.get("query_date", "unknown")
    return [
        f"{gene} allele frequencies: gnomAD {version} (pinned {date})",
        meta.get("cpic_guideline", "CPIC guideline"),
    ]
