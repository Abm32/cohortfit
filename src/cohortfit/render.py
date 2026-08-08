"""Rich renderer for AuditReport — tier-aware terminal output."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .models import AuditReport, GeneDrugFinding, Tier, Verdict
from .sites import rank_sites_by_burden

_VERDICT_STYLE = {
    Verdict.ACTIONABLE: "bold red",
    Verdict.CONTESTED: "bold magenta",
    Verdict.NO_SIGNAL: "dim green",
}

# badge label, badge style, panel border, subtitle
_TIER_META: dict[Tier, tuple[str, str, str, str]] = {
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


def _verdict_text(verdict: Verdict) -> Text:
    return Text(verdict.value, style=_VERDICT_STYLE.get(verdict, ""))


def _tier_badge(tier: Tier) -> Text:
    label, style, _, _ = _TIER_META[tier]
    return Text(label, style=style)


def _tier_border(tier: Tier) -> str:
    return _TIER_META[tier][2]


def _tier_subtitle(tier: Tier) -> str:
    return _TIER_META[tier][3]


def _format_citations(citations: list[str], *, required: bool = False) -> str:
    if not citations:
        if required:
            return "[bold yellow]Citation: MISSING — Tier 1 requires a source[/bold yellow]"
        return ""
    cites = ", ".join(f"PMID {c}" if c.isdigit() else c for c in citations)
    prefix = "Citation" if not required else "Citation (required)"
    return f"[bold]{prefix}:[/bold] {cites}"


def _render_header(report: AuditReport) -> Panel:
    trial = report.trial_id or "—"
    mode = "offline" if report.offline else "live"
    body = (
        f"[bold]{report.protocol_title}[/bold]\n"
        f"Trial ID: {trial}   Cohort n={report.total_planned_n}   \\[{mode}\\]"
    )
    return Panel(body, title="cohortfit", border_style="blue")


def _format_fraction(fraction: float) -> str:
    """Render a phenotype fraction without collapsing rare classes to zero.

    Poor Metabolizer frequencies are ~1e-4 under Hardy-Weinberg for rare
    no-function alleles. At one decimal place that prints "0.0%", which reads
    as absent — and PM is the class with the severe, potentially fatal
    outcome. METHOD.md argues the PM estimate is a floor rather than a point
    estimate, so the renderer must not round it out of existence.
    """
    pct = fraction * 100
    if pct == 0:
        return "0%"
    if pct < 0.01:
        return f"{pct:.3f}%"
    if pct < 1:
        return f"{pct:.2f}%"
    return f"{pct:.1f}%"


def _format_expected_n(expected_n: float) -> str:
    """Expected patient counts below 0.1 keep two decimals rather than showing 0.0."""
    if expected_n == 0:
        return "0"
    if expected_n < 0.1:
        return f"{expected_n:.2f}"
    return f"{expected_n:.1f}"


def _render_distribution(console: Console, finding: GeneDrugFinding) -> None:
    if not finding.distribution:
        return
    console.print(
        f"\n[bold]COHORT PHENOTYPE[/bold]  ",
        end="",
    )
    console.print(_tier_badge(Tier.DISTRIBUTION))
    table = Table(show_header=True, header_style="bold", box=None, padding=(0, 2))
    table.add_column("Phenotype")
    table.add_column("Fraction", justify="right")
    table.add_column("Expected n", justify="right")
    for row in sorted(finding.distribution, key=lambda d: -d.fraction):
        table.add_row(
            row.phenotype,
            _format_fraction(row.fraction),
            _format_expected_n(row.expected_n),
        )
    console.print(table)


def _render_tier0_finding(console: Console, finding: GeneDrugFinding) -> None:
    subtitle = _tier_subtitle(finding.tier)
    cpic = f"  CPIC Level {finding.cpic_level}" if finding.cpic_level else ""
    header = Text.assemble(
        ("FINDING  ", "bold"),
        (f"{finding.gene} × {finding.drug}  →  ", ""),
        _verdict_text(finding.verdict),
        (cpic, ""),
    )
    console.print(
        Panel(
            header,
            title=_tier_badge(finding.tier),
            subtitle=subtitle,
            border_style=_tier_border(finding.tier),
        )
    )
    if finding.missing_exclusion:
        console.print(f"  {finding.missing_exclusion}")
    if finding.citations:
        console.print(f"  [dim]{_format_citations(finding.citations)}[/dim]")
    _render_distribution(console, finding)


def _render_tier1_finding(console: Console, finding: GeneDrugFinding) -> None:
    subtitle = _tier_subtitle(finding.tier)
    lines = [
        Text.assemble(
            (f"{finding.gene} × {finding.drug}  →  ", "bold"),
            _verdict_text(finding.verdict),
        )
    ]
    for note in finding.notes:
        lines.append(Text(note))
    cite_line = _format_citations(finding.citations, required=True)
    if cite_line:
        lines.append(Text.from_markup(cite_line))

    body = Text("\n").join(lines)
    console.print(
        Panel(
            body,
            title=_tier_badge(finding.tier),
            subtitle=subtitle,
            border_style=_tier_border(finding.tier),
        )
    )
    if finding.tier == Tier.BURDEN and not finding.citations:
        console.print("[yellow]Warning: Tier 1 finding missing citation[/yellow]")


def _render_tier2_finding(console: Console, finding: GeneDrugFinding) -> None:
    subtitle = _tier_subtitle(finding.tier)
    lines = [Text("Not a prediction — labelled scenario only.", style="dim italic")]
    for note in finding.notes:
        lines.append(Text(note, style="dim"))
    if finding.citations:
        lines.append(Text.from_markup(_format_citations(finding.citations)))

    body = Text("\n").join(lines)
    console.print(
        Panel(
            body,
            title=_tier_badge(finding.tier),
            subtitle=subtitle,
            border_style=_tier_border(finding.tier),
        )
    )


def _render_finding(console: Console, finding: GeneDrugFinding) -> None:
    if finding.tier == Tier.DISTRIBUTION:
        _render_tier0_finding(console, finding)
    elif finding.tier == Tier.BURDEN:
        _render_tier1_finding(console, finding)
    else:
        _render_tier2_finding(console, finding)


def _render_site_burden(console: Console, report: AuditReport, gene: str) -> None:
    ranked = rank_sites_by_burden(report.site_findings, gene=gene)
    if not ranked:
        return

    console.print("\n[bold]SITE BURDEN[/bold]  ", end="")
    console.print(_tier_badge(Tier.DISTRIBUTION))
    console.print("[dim](IM+PM rate × planned_n)[/dim]")

    table = Table(show_header=True, header_style="bold")
    table.add_column("Site")
    table.add_column("At-risk rate", justify="right")
    table.add_column("Expected at-risk", justify="right")

    baseline = ranked[-1]
    for site in ranked:
        planned_n = (
            round(site.expected_at_risk_n / site.at_risk_fraction)
            if site.at_risk_fraction
            else 0
        )
        note = ""
        if site.site_name != baseline.site_name:
            ratio = site.at_risk_fraction / baseline.at_risk_fraction
            if abs(ratio - 1.0) > 1e-6:
                note = f"  [dim]({ratio:.2f}× rate vs {baseline.site_name})[/dim]"
        table.add_row(
            site.site_name,
            f"{site.at_risk_fraction * 100:.2f}%",
            f"{site.expected_at_risk_n:.1f} / {planned_n}{note}",
        )
    console.print(table)

    rates = {s.site_name: s.at_risk_fraction for s in ranked}
    if len({round(r, 6) for r in rates.values()}) < len(ranked):
        console.print(
            "\n[dim]Note: sites with identical ancestry share the same at-risk rate; "
            "differences in expected count reflect planned_n only.[/dim]"
        )


def _render_warnings(console: Console, report: AuditReport) -> None:
    """Print data-coverage warnings.

    These are deliberately loud: a renormalised-away population produces a
    distribution that still sums to 1.0 and looks complete. Silence here would
    reproduce the failure mode this tool exists to catch.
    """
    if not report.warnings:
        return
    console.print("\n[bold yellow]COVERAGE WARNINGS[/bold yellow]")
    for warning in report.warnings:
        console.print(f"  [yellow]![/yellow] {warning}")


def _render_sources(console: Console, report: AuditReport) -> None:
    if not report.data_sources:
        return
    console.print("\n[bold]DATA SOURCES[/bold]")
    for source in report.data_sources:
        console.print(f"  • {source}")


def render_audit_report(report: AuditReport, *, console: Console | None = None) -> None:
    """Print a tier-aware human-readable audit report to the console."""
    out = console or Console()
    out.print(_render_header(report))

    if not report.findings:
        if report.warnings:
            # Not the same as "no risk": we could not compute one.
            out.print(
                "\n[yellow]No distribution computed — see coverage warnings "
                "below.[/yellow]"
            )
        else:
            out.print("\n[yellow]No PGx-actionable drugs found in protocol.[/yellow]")
        _render_warnings(out, report)
        _render_sources(out, report)
        return

    site_genes_rendered: set[str] = set()
    for finding in report.findings:
        _render_finding(out, finding)
        if finding.tier == Tier.DISTRIBUTION and finding.gene not in site_genes_rendered:
            _render_site_burden(out, report, finding.gene)
            site_genes_rendered.add(finding.gene)

    _render_warnings(out, report)
    _render_sources(out, report)
    out.print()
