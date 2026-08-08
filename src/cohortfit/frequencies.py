"""Pinned population allele frequency fixtures.

Offline-only loader for gene frequency tables. Every frequency must carry
provenance in the JSON fixture — entries without source metadata fail validation.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_FIXTURES_DIR = Path(__file__).resolve().parents[2] / "fixtures" / "frequencies"

# Alleles that must never appear as hand-written round numbers without rsID backing.
_SUSPICIOUS_FREQUENCIES = frozenset({0.27, 0.05})


class FixtureError(ValueError):
    """Raised when a frequency fixture is missing, malformed, or incomplete."""


def repo_root() -> Path:
    """Return the cohortfit repository root (contains fixtures/ and src/)."""
    return _FIXTURES_DIR.parents[1]


def fixture_path(gene: str) -> Path:
    return _FIXTURES_DIR / f"{gene.lower()}.json"


def load_fixture(gene: str) -> dict[str, Any]:
    """Load the raw JSON fixture for a gene."""
    path = fixture_path(gene)
    if not path.is_file():
        raise FixtureError(f"No frequency fixture at {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def validate_fixture(data: dict[str, Any]) -> None:
    """Ensure every population's allele table is complete and sums to 1.0."""
    populations = data.get("populations")
    if not isinstance(populations, dict) or not populations:
        raise FixtureError("fixture missing non-empty 'populations' key")

    for pop_code, pop_data in populations.items():
        alleles = pop_data.get("alleles")
        if not isinstance(alleles, dict) or not alleles:
            raise FixtureError(f"{pop_code}: missing 'alleles'")

        if "*1" not in alleles:
            raise FixtureError(f"{pop_code}: missing required reference allele '*1'")

        total = 0.0
        for allele_name, record in alleles.items():
            if not isinstance(record, dict):
                raise FixtureError(f"{pop_code}/{allele_name}: entry must be an object")

            freq = record.get("frequency")
            if freq is None:
                raise FixtureError(f"{pop_code}/{allele_name}: missing 'frequency'")

            source = record.get("source")
            if not source:
                raise FixtureError(f"{pop_code}/{allele_name}: missing 'source' (provenance)")

            if allele_name != "*1" and source != "computed_remainder":
                if not record.get("rsid"):
                    raise FixtureError(f"{pop_code}/{allele_name}: non-*1 allele missing 'rsid'")
                if "alt_observed" not in record or "total_alleles" not in record:
                    raise FixtureError(
                        f"{pop_code}/{allele_name}: missing alt_observed/total_alleles counts"
                    )

            if freq in _SUSPICIOUS_FREQUENCIES and allele_name not in ("*9A",):
                raise FixtureError(
                    f"{pop_code}/{allele_name}: suspicious round frequency {freq} — verify rsID"
                )

            total += float(freq)

        if abs(total - 1.0) > 1e-6:
            raise FixtureError(f"{pop_code}: allele frequencies sum to {total}, not 1.0")


def load_gene_frequencies(gene: str, *, offline: bool = True) -> dict[str, dict[str, float]]:
    """Load population → allele → frequency for blend_allele_frequencies().

    Args:
        gene: Gene symbol (e.g. ``"DPYD"``).
        offline: Must be True; reserved for future live-query guard.

    Returns:
        ``{"SAS": {"*1": 0.98, "*2A": 0.0005, ...}, "EUR": {...}}``
    """
    if not offline:
        raise FixtureError("Live frequency queries are not supported; use offline=True")

    data = load_fixture(gene)
    validate_fixture(data)

    out: dict[str, dict[str, float]] = {}
    for pop_code, pop_data in data["populations"].items():
        out[pop_code] = {
            allele: float(record["frequency"])
            for allele, record in pop_data["alleles"].items()
        }
    return out


def load_gene_provenance(gene: str) -> dict[str, Any]:
    """Return fixture metadata and per-allele provenance for audit reports."""
    data = load_fixture(gene)
    validate_fixture(data)
    return {
        "meta": data.get("_meta", {}),
        "populations": {
            pop: pop_data.get("alleles", {})
            for pop, pop_data in data["populations"].items()
        },
        "ground_truth": data.get("_ground_truth", {}),
    }


def load_ground_truth(gene: str) -> dict[str, Any]:
    """Return pre-computed phenotype fractions from the fixture (for tests)."""
    data = load_fixture(gene)
    gt = data.get("_ground_truth")
    if not gt:
        raise FixtureError(f"{gene}: fixture missing '_ground_truth'")
    return gt
