"""POST /extract — prose to Protocol via Claude (503 without API key)."""

from __future__ import annotations

import os

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ...extract import ExtractionError, extract_protocol

router = APIRouter(tags=["extract"])


class ExtractRequest(BaseModel):
    prose: str = Field(..., min_length=1)
    model: str = "claude-sonnet-4-20250514"
    infer_ancestry: bool = True


@router.post("/extract")
def post_extract(body: ExtractRequest) -> dict:
    """Extract structured Protocol JSON from protocol prose."""
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
    return protocol.model_dump(mode="json")
