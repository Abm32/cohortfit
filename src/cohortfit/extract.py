"""Claude protocol extractor — prose to validated Protocol JSON.

Claude fills ``Protocol``; Pydantic validation is the boundary. Malformed output
raises ``ExtractionError`` rather than propagating into Tier 0 math.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

from pydantic import ValidationError

from .ancestry import apply_ancestry_defaults
from .models import Protocol

_DEFAULT_MODEL = "claude-sonnet-4-20250514"
_PROMPT_PATH = Path(__file__).parent / "prompts" / "protocol_extract.txt"


class ExtractionError(ValueError):
    """Raised when Claude output cannot be validated as a Protocol."""


def load_source(path: Path | str) -> str:
    """Read protocol source text from a file."""
    return Path(path).read_text(encoding="utf-8")


def load_extraction_prompt() -> str:
    """Load the pinned extraction system prompt."""
    if not _PROMPT_PATH.is_file():
        raise ExtractionError(f"Extraction prompt missing: {_PROMPT_PATH}")
    return _PROMPT_PATH.read_text(encoding="utf-8")


def strip_json_fence(text: str) -> str:
    """Remove markdown code fences and surrounding whitespace from model output."""
    cleaned = text.strip()
    fence_match = re.search(r"```(?:json)?\s*(.*?)\s*```", cleaned, re.DOTALL | re.IGNORECASE)
    if fence_match:
        cleaned = fence_match.group(1).strip()
    return cleaned


def validate_protocol_json(raw_json: str) -> Protocol:
    """Parse and validate JSON against the Protocol schema."""
    try:
        return Protocol.model_validate_json(raw_json)
    except ValidationError as exc:
        raise ExtractionError(f"Claude output failed Protocol validation: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ExtractionError(f"Claude output is not valid JSON: {exc}") from exc


def _call_claude(source: str, *, model: str, system_prompt: str) -> str:
    try:
        import anthropic
    except ImportError as exc:
        raise ExtractionError(
            'Anthropic SDK not installed. Run: pip install -e ".[llm]"'
        ) from exc

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ExtractionError("ANTHROPIC_API_KEY environment variable is not set.")

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model=model,
        max_tokens=4096,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": source,
            }
        ],
    )
    parts: list[str] = []
    for block in message.content:
        if block.type == "text":
            parts.append(block.text)
    if not parts:
        raise ExtractionError("Claude returned empty response.")
    return "\n".join(parts)


def extract_protocol(
    source: str,
    *,
    model: str = _DEFAULT_MODEL,
    infer_ancestry: bool = True,
    system_prompt: str | None = None,
) -> Protocol:
    """Extract a validated Protocol from unstructured protocol prose via Claude."""
    prompt = system_prompt or load_extraction_prompt()
    raw = _call_claude(source, model=model, system_prompt=prompt)
    cleaned = strip_json_fence(raw)
    protocol = validate_protocol_json(cleaned)
    if infer_ancestry:
        protocol = apply_ancestry_defaults(protocol)
    return protocol


def extract_protocol_from_file(
    path: Path | str,
    *,
    model: str = _DEFAULT_MODEL,
    infer_ancestry: bool = True,
) -> Protocol:
    """Read source file and extract a validated Protocol."""
    return extract_protocol(
        load_source(path),
        model=model,
        infer_ancestry=infer_ancestry,
    )
