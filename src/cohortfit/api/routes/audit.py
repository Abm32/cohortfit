"""POST /audit — run deterministic audit engine on Protocol JSON."""

from __future__ import annotations

from fastapi import APIRouter

from ...audit import audit_protocol
from ...models import Protocol

router = APIRouter(tags=["audit"])


@router.post("/audit")
def post_audit(protocol: Protocol, offline: bool = True) -> dict:
    """Audit a structured protocol and return AuditReport JSON."""
    report = audit_protocol(protocol, offline=offline)
    return report.model_dump(mode="json")
