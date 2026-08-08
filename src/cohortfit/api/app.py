"""FastAPI application — API routes + optional static web UI."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
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

app = FastAPI(
    title="cohortfit",
    description="Genomic feasibility auditing API — presentation layer only.",
    version="0.1.0",
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


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


_web_dist = repo_root() / "web" / "dist"
if _web_dist.is_dir():
    app.mount("/", StaticFiles(directory=_web_dist, html=True), name="web")
