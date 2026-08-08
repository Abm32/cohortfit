"""Map engine exceptions to HTTP responses."""

from __future__ import annotations

import json

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from ..extract import ExtractionError
from ..frequencies import FixtureError


def validation_error_payload(exc: ValidationError) -> dict:
    return {"detail": json.loads(exc.json())}


async def pydantic_validation_handler(_request: Request, exc: ValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content=validation_error_payload(exc))


async def request_validation_handler(
    _request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


async def extraction_error_handler(_request: Request, exc: ExtractionError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


async def fixture_error_handler(_request: Request, exc: FixtureError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})
