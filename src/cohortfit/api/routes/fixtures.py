"""Read-only fixture endpoints for demo and UI development."""

from __future__ import annotations

from fastapi import APIRouter

from ...frequencies import repo_root
from ...reports import load_audit_report

router = APIRouter(prefix="/fixtures", tags=["fixtures"])

_REPORTS = repo_root() / "fixtures" / "reports"
_PROTOCOLS = repo_root() / "protocols"


@router.get("/reports/sample")
def get_sample_report() -> dict:
    """Pinned AuditReport for default demo landing."""
    return load_audit_report(_REPORTS / "sample_audit_report.json").model_dump(mode="json")


@router.get("/reports/partial-coverage")
def get_partial_coverage_report() -> dict:
    """AuditReport exercising partial ancestry coverage UI state."""
    return load_audit_report(
        _REPORTS / "sample_partial_coverage_report.json"
    ).model_dump(mode="json")


@router.get("/protocols/demo")
def get_demo_protocol() -> dict:
    """Pinned demo protocol JSON for one-click audit."""
    import json

    return json.loads((_PROTOCOLS / "demo.json").read_text(encoding="utf-8"))
