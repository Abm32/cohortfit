"""POST /extract — prose to Protocol via Claude (503 without API key)."""

from __future__ import annotations

import os

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ...extract import ExtractionError, extract_protocol
from ...models import Protocol
from ..schemas import ErrorResponse

router = APIRouter(tags=["extract"])


class ExtractRequest(BaseModel):
    """Free-text protocol source for Claude to structure."""

    prose: str = Field(
        ...,
        min_length=1,
        description="Protocol text or ClinicalTrials.gov export to extract structure from.",
        examples=["A phase II trial of capecitabine 1250 mg/m² BID in advanced breast cancer…"],
    )
    model: str = Field(
        "claude-sonnet-4-20250514", description="Anthropic model ID used for extraction."
    )
    infer_ancestry: bool = Field(
        True,
        description="Apply country-default ancestry_mix when a site omits it (e.g. IN → SAS).",
    )


@router.post(
    "/extract",
    response_model=Protocol,
    summary="Extract a structured Protocol from protocol prose (Claude)",
    response_description="A validated `Protocol` — drugs, criteria, sites, and enrolment only.",
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Claude returned output that failed Protocol validation.",
        },
        503: {
            "model": ErrorResponse,
            "description": "ANTHROPIC_API_KEY is not set on the server; extraction is unavailable.",
        },
    },
)
def post_extract(body: ExtractRequest) -> Protocol:
    """Convert unstructured protocol prose into a validated `Protocol`.

    Claude extracts structure only — drugs, dose regimen, inclusion/exclusion
    criteria, sites, and enrolment. It never estimates an allele frequency or a
    phenotype; those are computed downstream by `POST /audit`. Requires an
    `ANTHROPIC_API_KEY` on the server, otherwise responds `503`.
    """
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise HTTPException(
            status_code=503,
            detail="ANTHROPIC_API_KEY is not set. Extraction requires an API key.",
        )
    try:
        protocol = extract_protocol(
            body.prose,
            model=body.model,
            infer_ancestry=body.infer_ancestry,
        )
    except ExtractionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return protocol
