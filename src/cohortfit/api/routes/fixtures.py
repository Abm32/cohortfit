"""Read-only fixture endpoints for demo and UI development."""

from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException

from ...frequencies import repo_root
from ...reports import load_audit_report

router = APIRouter(prefix="/fixtures", tags=["fixtures"])

_REPORTS = repo_root() / "fixtures" / "reports"
_PROTOCOLS = repo_root() / "protocols"

# The demo catalogue. Each entry exists to exercise a *different* path through
# the engine — see docs/DATASETS.md. `demonstrates` is the reason the fixture is
# in the set, and it is what the UI cards show, so the narrative lives with the
# data rather than being duplicated in TypeScript.
_CATALOGUE: tuple[dict, ...] = (
    {
        "slug": "demo",
        "file": "demo.json",
        "title": "Vinflunine + Capecitabine, Advanced Breast Cancer",
        "trial_id": "NCT01095003",
        "cohort": "230 patients · 2 Indian sites + Munich",
        "demonstrates": "Site selection changes expected burden",
        "detail": (
            "Munich sits at 6.40% at-risk against 3.55% in Mumbai and Kochi — a "
            "1.80x rate ratio driven by ancestry, not headcount."
        ),
        "expect": "ACTIONABLE + CONTESTED",
    },
    {
        "slug": "capecitabine-india",
        "file": "capecitabine_india.json",
        "title": "Adjuvant Capecitabine, Stage III Colon Adenocarcinoma",
        "trial_id": "CFIT-CRC-2026-01",
        "cohort": "150 patients · 100% South Asian",
        "demonstrates": "One allele carries the whole risk",
        "detail": (
            "HapB3 holds 94.2% of this cohort's actionable burden, and CPIC's "
            "dose action for HapB3 is disputed — so this raises a second, "
            "CONTESTED finding."
        ),
        "expect": "ACTIONABLE + CONTESTED",
    },
    {
        "slug": "us-multiancestry",
        "file": "us_multiancestry.json",
        "title": "Adjuvant Capecitabine, Resected Pancreatic Adenocarcinoma",
        "trial_id": "NCT02688712",
        "cohort": "200 patients · Houston + Chicago",
        "demonstrates": "The tool reports what it cannot compute",
        "detail": (
            "Only SAS and EUR frequencies are pinned, so 35% of declared "
            "enrolment (AFR, AMR) is excluded — and the report says so instead "
            "of quietly returning European numbers."
        ),
        "expect": "ACTIONABLE + CONTESTED + coverage warning",
    },
    {
        "slug": "dpyd-screened",
        "file": "dpyd_screened_compliant.json",
        "title": "Capecitabine Maintenance, Metastatic Colorectal (DPYD-screened)",
        "trial_id": "NCT04138641",
        "cohort": "150 patients · Kerala + Heidelberg",
        "demonstrates": "It does not simply always accuse",
        "detail": (
            "Same drug and ancestry as the India protocol, but the criteria "
            "screen DPYD per EMA 2020 — so the screening verdict flips to "
            "NO_SIGNAL. CONTESTED still stands: screening closes the gap, it "
            "does not settle the dose."
        ),
        "expect": "NO_SIGNAL + CONTESTED",
    },
)

_BY_SLUG = {entry["slug"]: entry for entry in _CATALOGUE}


@router.get("/protocols")
def list_protocols() -> list[dict]:
    """Catalogue of pinned demo protocols, for the UI's selection cards."""
    return [{k: v for k, v in entry.items() if k != "file"} for entry in _CATALOGUE]


@router.get("/protocols/{slug}")
def get_protocol(slug: str) -> dict:
    """One pinned protocol by catalogue slug."""
    entry = _BY_SLUG.get(slug)
    if entry is None:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown protocol {slug!r}. Known: {', '.join(sorted(_BY_SLUG))}.",
        )
    return json.loads((_PROTOCOLS / entry["file"]).read_text(encoding="utf-8"))


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
