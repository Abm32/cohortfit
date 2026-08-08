"""AuditReport fixture loader — renderer dev without the audit engine."""

from __future__ import annotations

import json
from pathlib import Path

from .models import AuditReport


def load_audit_report(path: Path | str) -> AuditReport:
    """Load and validate a pinned AuditReport JSON file."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return AuditReport.model_validate(data)
