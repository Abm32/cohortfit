"""Rich renderer for AuditReport — tier-aware terminal output."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .display import (
    TIER_META,
    VERDICT_RICH_STYLE,
    format_citations_rich,
    format_expected_n,
    format_fraction,
    infer_planned_n,
    tier_border_token,
    tier_rich_style,
    tier_subtitle,
)
from .models import AuditReport, GeneDrugFinding, PhenotypeCount, Tier, Verdict
from .sites import rank_sites_by_burden


def _verdict_text(verdict: Verdict) -> Text:
    return Text(verdict.value, style=VERDICT_RICH_STYLE.get(verdict, ""))


def _tier_badge(tier: Tier) -> Text:
    return Text(TIER_META[tier][0], style=tier_rich_style(tier))


def _render_header(report: AuditReport) -> Panel:
    trial = report.trial_id or "—"
    mode = "offline" if report.offline else "live"
    body = (
        f"[bold]{report.protocol_title}[/bold]\n"
        f"Trial ID: {trial}   Cohort n={report.total_planned_n}   \\[{mode}\\]"
    )
    return Panel(body, title="cohortfit", border_style="blue")


def _format_range(row: PhenotypeCount) -> str:
    """Render the provenance sensitivity range for one phenotype class."""
    if not row.is_range:
        return ""
    low, high = row.fraction_low, row.fraction_high
    if low is None or high is None:
        return ""
    span = f"{format_fraction(low)} – {format_fraction(high)}"
    if low > 0:
        span += f"  ({high / low:.1f}×)"
    return span


def _render_distribution(console: Console, finding: GeneDrugFinding) -> None:
    if not finding.distribution:
        return
    console.print("\n[bold]COHORT PHENOTYPE[/bold]  ", end="")
    console.print(_tier_badge(Tier.DISTRIBUTION))
    rows = sorted(finding.distribution, key=lambda d: -d.fraction)
    show_range = any(row.is_range for row in rows)

    table = Table(show_header=True, header_style="bold", box=None, padding=(0, 2))
    table.add_column("Phenotype")
    table.add_column("Fraction", justify="right")
    table.add_column("Expected n", justify="right")
    if show_range:
        table.add_column("Range (provenance)", justify="right")

    for row in rows:
        cells = [
            row.phenotype,
            format_fraction(row.fraction),
            format_expected_n(row.expected_n),
        ]
        if show_range:
            cells.append(_format_range(row))
        table.add_row(*cells)
    console.print(table)

    if show_range:
        console.print(
            "[dim]Range spans every candidate value for the disputed allele "
            "frequency recorded in the fixture's known_discrepancies. Read the "
            "wider ranges as provenance uncertainty, not as a prediction "
            "interval.[/dim]"
        )


def _render_tier0_finding(console: Console, finding: GeneDrugFinding) -> None:
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
            subtitle=tier_subtitle(finding.tier),
            border_style=tier_border_token(finding.tier),
        )
    )
    if finding.missing_exclusion:
        console.print(f"  {finding.missing_exclusion}")
    # Tier 0 notes carry the panel-coverage and partial-ancestry caveats. They
    # were being stored on the finding and never printed, which is the same
    # failure the coverage warnings exist to prevent.
    for note in finding.notes:
        console.print(f"  [dim]{note}[/dim]")
    if finding.citations:
        console.print(f"  [dim]{format_citations_rich(finding.citations)}[/dim]")
    _render_distribution(console, finding)


def _render_tier1_finding(console: Console, finding: GeneDrugFinding) -> None:
    lines = [
        Text.assemble(
            (f"{finding.gene} × {finding.drug}  →  ", "bold"),
            _verdict_text(finding.verdict),
        )
    ]
    for note in finding.notes:
        lines.append(Text(note))
    cite_line = format_citations_rich(finding.citations, required=True)
    if cite_line:
        lines.append(Text.from_markup(cite_line))

    body = Text("\n").join(lines)
    console.print(
        Panel(
            body,
            title=_tier_badge(finding.tier),
            subtitle=tier_subtitle(finding.tier),
            border_style=tier_border_token(finding.tier),
        )
    )
    if finding.tier == Tier.BURDEN and not finding.citations:
        console.print("[yellow]Warning: Tier 1 finding missing citation[/yellow]")


def _render_tier2_finding(console: Console, finding: GeneDrugFinding) -> None:
    lines = [Text("Not a prediction — labelled scenario only.", style="dim italic")]
    for note in finding.notes:
        lines.append(Text(note, style="dim"))
    if finding.citations:
        lines.append(Text.from_markup(format_citations_rich(finding.citations)))

    body = Text("\n").join(lines)
    console.print(
        Panel(
            body,
            title=_tier_badge(finding.tier),
            subtitle=tier_subtitle(finding.tier),
            border_style=tier_border_token(finding.tier),
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
        planned_n = infer_planned_n(site.expected_at_risk_n, site.at_risk_fraction)
        note = ""
        if site.site_name != baseline.site_name and baseline.at_risk_fraction:
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
            out.print(
                "\n[yellow]No distribution computed — see coverage warnings below.[/yellow]"
            )
        else:
            out.print("\n[yellow]No PGx-actionable drugs found in protocol.[/yellow]")
        _render_warnings(out, report)
        _render_sources(out, report)
        return

    # All findings, then the site tables. Interleaving them stranded the second
    # finding for a gene below that gene's site-burden table, where it reads as
    # a footnote to the table rather than as a verdict in its own right.
    for finding in report.findings:
        _render_finding(out, finding)

    for gene in dict.fromkeys(
        f.gene for f in report.findings if f.tier == Tier.DISTRIBUTION
    ):
        _render_site_burden(out, report, gene)

    _render_warnings(out, report)
    _render_sources(out, report)
    out.print()
