"""Shared display helpers for CLI and web UI.

Pure formatting of values already present in AuditReport JSON — no audit math.
"""

from __future__ import annotations

from .models import Tier, Verdict

# label, rich_badge_style, border_token, subtitle
TIER_META: dict[Tier, tuple[str, str, str, str]] = {
    Tier.DISTRIBUTION: (
        "TIER 0",
        "bold cyan",
        "cyan",
        "Arithmetic on pinned tables + HWE",
    ),
    Tier.BURDEN: (
        "TIER 1",
        "bold yellow",
        "yellow",
        "Literature effect multiplier — citation required",
    ),
    Tier.SCENARIO: (
        "SCENARIO",
        "dim italic",
        "dim",
        "Directional only — not a prediction",
    ),
}

VERDICT_LABELS: dict[Verdict, str] = {
    Verdict.ACTIONABLE: "ACTIONABLE",
    Verdict.CONTESTED: "CONTESTED",
    Verdict.NO_SIGNAL: "NO_SIGNAL",
}

VERDICT_RICH_STYLE: dict[Verdict, str] = {
    Verdict.ACTIONABLE: "bold red",
    Verdict.CONTESTED: "bold magenta",
    Verdict.NO_SIGNAL: "dim green",
}


def tier_label(tier: Tier) -> str:
    return TIER_META[tier][0]


def tier_subtitle(tier: Tier) -> str:
    return TIER_META[tier][3]


def tier_border_token(tier: Tier) -> str:
    return TIER_META[tier][2]


def tier_rich_style(tier: Tier) -> str:
    return TIER_META[tier][1]


def format_fraction(fraction: float) -> str:
    """Render a phenotype fraction without collapsing rare classes to zero."""
    pct = fraction * 100
    if pct == 0:
        return "0%"
    if pct < 0.01:
        return f"{pct:.3f}%"
    if pct < 1:
        return f"{pct:.2f}%"
    return f"{pct:.1f}%"


def format_expected_n(expected_n: float) -> str:
    """Expected patient counts below 0.1 keep two decimals rather than showing 0.0."""
    if expected_n == 0:
        return "0"
    if expected_n < 0.1:
        return f"{expected_n:.2f}"
    return f"{expected_n:.1f}"


def format_at_risk_rate(fraction: float) -> str:
    """Site at-risk rate — two decimals (matches CLI site table)."""
    return f"{fraction * 100:.2f}%"


def pubmed_url(pmid: str) -> str:
    if pmid.isdigit():
        return f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
    return pmid


def format_citation_list(citations: list[str], *, required: bool = False) -> str:
    """Plain-text citation line for web UI."""
    if not citations:
        if required:
            return "Citation: MISSING — Tier 1 requires a source"
        return ""
    cites = ", ".join(f"PMID {c}" if c.isdigit() else c for c in citations)
    prefix = "Citation (required)" if required else "Citation"
    return f"{prefix}: {cites}"


def format_citations_rich(citations: list[str], *, required: bool = False) -> str:
    """Rich-markup citation line for terminal renderer."""
    if not citations:
        if required:
            return "[bold yellow]Citation: MISSING — Tier 1 requires a source[/bold yellow]"
        return ""
    cites = ", ".join(f"PMID {c}" if c.isdigit() else c for c in citations)
    prefix = "Citation" if not required else "Citation (required)"
    return f"[bold]{prefix}:[/bold] {cites}"


def infer_planned_n(expected_at_risk_n: float, at_risk_fraction: float) -> int:
    """Back-compute planned_n from site finding fields (same as CLI)."""
    if at_risk_fraction <= 0:
        return 0
    return round(expected_at_risk_n / at_risk_fraction)
