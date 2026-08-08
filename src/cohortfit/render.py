"""Rich renderer for AuditReport — what judges see on stdout."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .models import AuditReport, GeneDrugFinding, Verdict
from .sites import rank_sites_by_burden

_VERDICT_STYLE = {
    Verdict.ACTIONABLE: "bold red",
    Verdict.CONTESTED: "bold magenta",
    Verdict.NO_SIGNAL: "dim green",
}


def _verdict_text(verdict: Verdict) -> Text:
    return Text(verdict.value, style=_VERDICT_STYLE.get(verdict, ""))


def _render_header(report: AuditReport) -> Panel:
    trial = report.trial_id or "—"
    mode = "offline" if report.offline else "live"
    body = (
        f"[bold]{report.protocol_title}[/bold]\n"
        f"Trial ID: {trial}   Cohort n={report.total_planned_n}   \\[{mode}\\]"
    )
    return Panel(body, title="cohortfit", border_style="blue")


def _render_finding(console: Console, finding: GeneDrugFinding) -> None:
    cpic = f"  CPIC Level {finding.cpic_level}" if finding.cpic_level else ""
    console.print(
        f"\n[bold]FINDING[/bold]  {finding.gene} × {finding.drug}  →  ",
        end="",
    )
    console.print(_verdict_text(finding.verdict), end="")
    console.print(cpic)

    if finding.missing_exclusion:
        console.print(f"         {finding.missing_exclusion}")
    if finding.citations:
        cites = ", ".join(f"PMID {c}" if c.isdigit() else c for c in finding.citations)
        console.print(f"         [dim]Citation: {cites}[/dim]")

    if finding.distribution:
        console.print("\n[bold]COHORT PHENOTYPE[/bold]  [dim](Tier 0)[/dim]")
        table = Table(show_header=True, header_style="bold", box=None, padding=(0, 2))
        table.add_column("Phenotype")
        table.add_column("Fraction", justify="right")
        table.add_column("Expected n", justify="right")
        for row in sorted(finding.distribution, key=lambda d: -d.fraction):
            table.add_row(
                row.phenotype,
                f"{row.fraction * 100:.1f}%",
                f"{row.expected_n:.1f}",
            )
        console.print(table)


def _render_site_burden(console: Console, report: AuditReport, gene: str) -> None:
    ranked = rank_sites_by_burden(report.site_findings, gene=gene)
    if not ranked:
        return

    console.print("\n[bold]SITE BURDEN[/bold]  [dim](IM+PM rate × planned_n)[/dim]")
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


def _render_sources(console: Console, report: AuditReport) -> None:
    if not report.data_sources:
        return
    console.print("\n[bold]DATA SOURCES[/bold]")
    for source in report.data_sources:
        console.print(f"  • {source}")


def render_audit_report(report: AuditReport, *, console: Console | None = None) -> None:
    """Print a human-readable audit report to the console."""
    out = console or Console()
    out.print(_render_header(report))

    if not report.findings:
        out.print("\n[yellow]No PGx-actionable drugs found in protocol.[/yellow]")
        _render_sources(out, report)
        return

    for finding in report.findings:
        _render_finding(out, finding)
        _render_site_burden(out, report, finding.gene)

    _render_sources(out, report)
    out.print()
