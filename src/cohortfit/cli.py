"""Typer CLI — the command judges type on stage."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from pydantic import ValidationError
from rich.console import Console

from .audit import audit_protocol, load_protocol
from .frequencies import FixtureError
from .render import render_audit_report

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


if __name__ == "__main__":
    app()
