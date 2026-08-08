"""Typer CLI — the command judges type on stage."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from pydantic import ValidationError
from rich.console import Console

from .audit import audit_protocol, load_protocol
from .extract import ExtractionError, extract_protocol_from_file
from .frequencies import FixtureError
from .render import render_audit_report
from .reports import load_audit_report

app = typer.Typer(
    name="cohortfit",
    help="Genomic feasibility auditing for clinical trial protocols.",
    no_args_is_help=True,
    invoke_without_command=True,
)


@app.callback()
def main() -> None:
    """Genomic feasibility auditing for clinical trial protocols."""


@app.command()
def audit(
    protocol_path: Path = typer.Argument(
        ...,
        exists=True,
        readable=True,
        dir_okay=False,
        help="Structured protocol JSON (Claude extraction output or pinned fixture).",
    ),
    offline: bool = typer.Option(
        True,
        "--offline/--no-offline",
        help="Run against pinned fixtures only. Default on — demo insurance.",
    ),
) -> None:
    """Audit a trial protocol for genomic feasibility (Tier 0)."""
    err = Console(stderr=True)
    try:
        protocol = load_protocol(protocol_path)
        report = audit_protocol(protocol, offline=offline)
    except FixtureError as exc:
        err.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from exc
    except ValidationError as exc:
        err.print("[red]Error:[/red] Protocol JSON failed validation.")
        err.print(str(exc))
        raise typer.Exit(code=1) from exc
    except json.JSONDecodeError as exc:
        err.print(f"[red]Error:[/red] Invalid JSON in {protocol_path}: {exc}")
        raise typer.Exit(code=1) from exc

    render_audit_report(report, console=Console())


@app.command()
def render(
    report_path: Path = typer.Argument(
        ...,
        exists=True,
        readable=True,
        dir_okay=False,
        help="Pinned AuditReport JSON (fixtures/reports/sample_audit_report.json).",
    ),
) -> None:
    """Render a pinned AuditReport to the terminal (no audit engine)."""
    err = Console(stderr=True)
    try:
        report = load_audit_report(report_path)
    except ValidationError as exc:
        err.print("[red]Error:[/red] AuditReport JSON failed validation.")
        err.print(str(exc))
        raise typer.Exit(code=1) from exc
    except json.JSONDecodeError as exc:
        err.print(f"[red]Error:[/red] Invalid JSON in {report_path}: {exc}")
        raise typer.Exit(code=1) from exc

    render_audit_report(report, console=Console())


@app.command()
def extract(
    source_path: Path = typer.Argument(
        ...,
        exists=True,
        readable=True,
        dir_okay=False,
        help="Protocol source document (plain text or CT.gov export).",
    ),
    output: Path = typer.Option(
        ...,
        "-o",
        "--output",
        help="Write validated Protocol JSON to this path.",
    ),
    model: str = typer.Option(
        "claude-sonnet-4-20250514",
        "--model",
        help="Anthropic model ID for extraction.",
    ),
    infer_ancestry: bool = typer.Option(
        True,
        "--infer-ancestry/--no-infer-ancestry",
        help="Apply country-default ancestry_mix when sites omit it.",
    ),
) -> None:
    """Extract structured Protocol JSON from protocol prose via Claude."""
    err = Console(stderr=True)
    try:
        protocol = extract_protocol_from_file(
            source_path,
            model=model,
            infer_ancestry=infer_ancestry,
        )
    except ExtractionError as exc:
        err.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(protocol.model_dump_json(indent=2), encoding="utf-8")
    Console().print(f"[green]Wrote validated Protocol[/green] → {output}")


if __name__ == "__main__":
    app()
