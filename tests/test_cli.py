"""Smoke tests for the cohortfit CLI."""

from __future__ import annotations

from typer.testing import CliRunner

from cohortfit.cli import app
from cohortfit.frequencies import repo_root

runner = CliRunner()
DEMO_PROTOCOL = repo_root() / "protocols" / "demo.json"


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "audit" in result.stdout


def test_audit_demo_offline_default():
    result = runner.invoke(app, ["audit", str(DEMO_PROTOCOL)])
    assert result.exit_code == 0
    assert "ACTIONABLE" in result.stdout
    assert "TIER 0" in result.stdout
    assert "DPYD" in result.stdout
    assert "capecitabine" in result.stdout
    assert "Munich" in result.stdout
    assert "offline" in result.stdout


def test_audit_demo_explicit_offline():
    result = runner.invoke(app, ["audit", str(DEMO_PROTOCOL), "--offline"])
    assert result.exit_code == 0
    assert "ACTIONABLE" in result.stdout


def test_audit_missing_file():
    result = runner.invoke(app, ["audit", "does-not-exist.json"])
    assert result.exit_code != 0


def test_no_offline_rejected():
    result = runner.invoke(app, ["audit", str(DEMO_PROTOCOL), "--no-offline"])
    assert result.exit_code == 1
    combined = result.stdout + result.stderr
    assert "offline" in combined.lower()
