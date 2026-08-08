"""GET /provenance/{gene} — read-only frequency fixture metadata."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ...frequencies import FixtureError, load_gene_provenance

router = APIRouter(tags=["provenance"])


@router.get("/provenance/{gene}")
def get_provenance(gene: str) -> dict:
    """Return pinned allele-frequency provenance for a gene."""
    try:
        return load_gene_provenance(gene.upper())
    except FixtureError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
