"""POST /audit — run the deterministic audit engine on a Protocol."""

from __future__ import annotations

from fastapi import APIRouter, Body, Query

from ...audit import audit_protocol
from ...models import AuditReport, Protocol
from ..schemas import ErrorResponse

router = APIRouter(tags=["audit"])

_PROTOCOL_EXAMPLE = {
    "trial_id": "NCT01095003",
    "title": "Vinflunine Plus Capecitabine in Advanced Breast Cancer",
    "drugs": [
        {
            "drug": "capecitabine",
            "dose": "1250 mg/m² twice daily",
            "route": "oral",
            "schedule": "days 1-14 every 21 days",
        }
    ],
    "inclusion_criteria": ["Histologically confirmed advanced breast cancer"],
    "exclusion_criteria": ["Known hypersensitivity to fluoropyrimidines"],
    "sites": [
        {
            "name": "Mumbai",
            "country": "IN",
            "planned_n": 100,
            "ancestry_mix": {"SAS": 1.0},
        },
        {
            "name": "Munich",
            "country": "DE",
            "planned_n": 80,
            "ancestry_mix": {"EUR": 1.0},
        },
    ],
}


@router.post(
    "/audit",
    response_model=AuditReport,
    summary="Run the deterministic audit engine on a structured protocol",
    response_description=(
        "The computed AuditReport: tiered gene-drug findings, per-site metabolic "
        "burden, provenance warnings, and the pinned data sources every number came from."
    ),
    responses={
        422: {
            "model": ErrorResponse,
            "description": "The protocol body failed schema validation.",
        }
    },
)
def post_audit(
    protocol: Protocol = Body(
        ...,
        openapi_examples={
            "demo": {
                "summary": "Two-site capecitabine trial (India + Germany)",
                "description": (
                    "Minimal protocol that raises an ACTIONABLE DPYD screening gap and a "
                    "CONTESTED HapB3-burden finding."
                ),
                "value": _PROTOCOL_EXAMPLE,
            }
        },
    ),
    offline: bool = Query(
        True,
        description=(
            "Run against pinned fixtures only (default). Live frequency lookups are not "
            "implemented; the engine always uses pinned gnomAD/CPIC tables regardless of "
            "this flag, and the flag is echoed back on the report for transparency."
        ),
    ),
) -> AuditReport:
    """Audit a structured `Protocol` and return the deterministic `AuditReport`.

    This is the core endpoint. Claude (or a human) supplies the structured
    protocol; every number in the response is computed here from pinned allele
    frequencies and CPIC tables — no LLM is involved past this boundary.
    """
    return audit_protocol(protocol, offline=offline)
