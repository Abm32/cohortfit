"""GET /provenance/{gene} — read-only frequency fixture metadata."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Path

from ...frequencies import FixtureError, load_gene_provenance
from ..schemas import ErrorResponse

router = APIRouter(tags=["provenance"])


@router.get(
    "/provenance/{gene}",
    summary="Frequency-fixture provenance for a gene",
    response_description=(
        "Pinned allele-frequency provenance: source metadata, per-population "
        "frequencies, ground-truth diplotypes, and any recorded known discrepancies."
    ),
    responses={
        404: {
            "model": ErrorResponse,
            "description": "No pinned frequency fixture exists for the requested gene.",
        }
    },
)
def get_provenance(
    gene: str = Path(
        ...,
        description="Gene symbol, case-insensitive (e.g. DPYD).",
        examples=["DPYD"],
    ),
) -> dict[str, Any]:
    """Return the pinned allele-frequency provenance for a gene.

    This is what makes a number in the report auditable: rsIDs, gnomAD
    alt/total counts, query dates, and the discrepancies the fixture explicitly
    refuses to resolve.
    """
    try:
        return load_gene_provenance(gene.upper())
    except FixtureError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
