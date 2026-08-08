"""API-only response/request schemas.

These are presentation-layer contracts for the HTTP surface. They do not carry
any audit logic — the engine's own models live in ``cohortfit.models``. Keeping
them here means the OpenAPI schema is descriptive without leaking engine
internals or reshaping the deterministic layer for the sake of the UI.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Liveness probe payload."""

    status: str = Field("ok", description="Always ``ok`` when the service is up.")


class ProtocolCard(BaseModel):
    """One entry in the demo protocol catalogue (``GET /fixtures/protocols``).

    The catalogue exists so the UI's selection cards are driven by the API
    rather than hardcoded in TypeScript: the reason each fixture is in the demo
    set lives next to the data. The pinned protocol JSON itself is fetched
    separately via ``GET /fixtures/protocols/{slug}``.
    """

    slug: str = Field(..., description="Stable identifier used in the fetch URL.")
    title: str = Field(..., description="Human-readable trial title.")
    trial_id: str = Field(..., description="Registry ID (NCT…) or internal fixture ID.")
    cohort: str = Field(..., description="One-line cohort summary (size · sites/ancestry).")
    demonstrates: str = Field(
        ..., description="The engine behaviour this fixture is chosen to exercise."
    )
    detail: str = Field(..., description="Longer rationale shown on the card body.")
    expect: str = Field(..., description="Expected verdict shape, e.g. 'ACTIONABLE + CONTESTED'.")


class ErrorResponse(BaseModel):
    """Standard error envelope returned by the API's exception handlers."""

    detail: str = Field(..., description="Human-readable explanation of what went wrong.")
