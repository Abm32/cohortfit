"""FastAPI application — API routes + optional static web UI."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError

from ..extract import ExtractionError
from ..frequencies import FixtureError, repo_root
from .errors import (
    extraction_error_handler,
    fixture_error_handler,
    pydantic_validation_handler,
    request_validation_handler,
)
from .routes import audit, extract, fixtures, provenance
from .schemas import HealthResponse

_DESCRIPTION = """
Genomic feasibility auditing for clinical trial protocols — **presentation layer only**.

`cohortfit` reads a structured trial protocol and computes the pharmacogenomic
phenotype distribution of the cohort it will actually recruit, given the ancestry
mix of its planned sites.

**The boundary is the whole point.** Claude (via `POST /extract`) converts protocol
prose into a structured `Protocol`. Everything downstream — every fraction, every
verdict — is computed deterministically from pinned gnomAD allele frequencies and
CPIC tables by `POST /audit`. No LLM estimates a number.

### Output contract
- **Tiers** — Tier 0 is arithmetic on pinned tables (fully defensible); Tier 1
  needs a cited literature multiplier; Tier 2 is a labelled scenario, never a prediction.
- **Verdicts** — `ACTIONABLE` (CPIC Level A gap), `CONTESTED` (real literature
  disagreement, shown not resolved), `NO_SIGNAL` (no actionable interaction).

Offline by default: the engine runs entirely against pinned fixtures, no network.
"""

_TAGS_METADATA = [
    {
        "name": "audit",
        "description": "Run the deterministic engine on a structured protocol.",
    },
    {
        "name": "extract",
        "description": "Claude-powered prose → `Protocol` structuring. Requires an API key.",
    },
    {
        "name": "fixtures",
        "description": "Read-only pinned demo protocols and sample reports for the UI.",
    },
    {
        "name": "provenance",
        "description": "Auditable source metadata behind each gene's pinned frequencies.",
    },
    {"name": "health", "description": "Liveness probe."},
]

app = FastAPI(
    title="cohortfit",
    description=_DESCRIPTION,
    version="0.1.0",
    summary="Deterministic pharmacogenomic feasibility auditing for clinical trials.",
    license_info={"name": "Apache-2.0", "url": "https://www.apache.org/licenses/LICENSE-2.0"},
    contact={"name": "cohortfit", "url": "https://github.com/Abm32/cohortfit"},
    openapi_tags=_TAGS_METADATA,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(ValidationError, pydantic_validation_handler)
app.add_exception_handler(RequestValidationError, request_validation_handler)
app.add_exception_handler(ExtractionError, extraction_error_handler)
app.add_exception_handler(FixtureError, fixture_error_handler)

app.include_router(fixtures.router)
app.include_router(audit.router)
app.include_router(provenance.router)
app.include_router(extract.router)


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["health"],
    summary="Liveness probe",
    response_description="Service status; `{\"status\": \"ok\"}` when up.",
)
def health() -> dict[str, str]:
    """Return service liveness."""
    return {"status": "ok"}


_web_dist = repo_root() / "web" / "dist"
if _web_dist.is_dir():
    app.mount("/assets", StaticFiles(directory=_web_dist / "assets"), name="assets")

    # SPA fallback: client-side routes like /app must serve index.html.
    # Registered after all API routers, so /audit, /fixtures, etc. win first.
    @app.get("/{path:path}", include_in_schema=False)
    def spa_fallback(path: str) -> FileResponse:
        candidate = _web_dist / path
        if path and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(_web_dist / "index.html")
