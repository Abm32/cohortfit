"""Tests for tier-aware AuditReport rendering."""

from __future__ import annotations

from io import StringIO

import pytest
from rich.console import Console
from typer.testing import CliRunner

from cohortfit.cli import app
from cohortfit.frequencies import repo_root
from cohortfit.models import Tier
from cohortfit.render import render_audit_report
from cohortfit.reports import load_audit_report

SAMPLE_REPORT = repo_root() / "fixtures" / "reports" / "sample_audit_report.json"
runner = CliRunner()


@pytest.fixture
def sample_report():
    return load_audit_report(SAMPLE_REPORT)


def _render_to_string(report) -> str:
    buf = StringIO()
    render_audit_report(report, console=Console(file=buf, force_terminal=True, width=120))
    return buf.getvalue()


class TestLoadAuditReport:
    def test_sample_fixture_validates(self, sample_report):
        assert sample_report.trial_id == "NCT01095003"
        assert len(sample_report.findings) == 3
        assert {f.tier for f in sample_report.findings} == {
            Tier.DISTRIBUTION,
            Tier.BURDEN,
            Tier.SCENARIO,
        }


class TestTierStyling:
    def test_tier0_badge_and_actionable(self, sample_report):
        out = _render_to_string(sample_report)
        assert "TIER 0" in out
        assert "ACTIONABLE" in out
        assert "COHORT PHENOTYPE" in out

    def test_tier1_badge_and_citations(self, sample_report):
        out = _render_to_string(sample_report)
        assert "TIER 1" in out
        assert "CONTESTED" in out
        assert "38147293" in out
        assert "35034351" in out
        assert "Literature effect multiplier" in out

    def test_tier2_scenario_label(self, sample_report):
        out = _render_to_string(sample_report)
        assert "SCENARIO" in out
        assert "not a prediction" in out.lower()

    def test_tier_badges_are_distinct(self, sample_report):
        out = _render_to_string(sample_report)
        assert "TIER 0" in out
        assert "TIER 1" in out
        assert "SCENARIO" in out

    def test_site_burden_rendered_once_for_tier0(self, sample_report):
        out = _render_to_string(sample_report)
        assert out.count("SITE BURDEN") == 1
        assert "Munich" in out


class TestRenderCommand:
    def test_cli_render_sample_fixture(self):
        result = runner.invoke(app, ["render", str(SAMPLE_REPORT)])
        assert result.exit_code == 0
        assert "TIER 0" in result.stdout
        assert "TIER 1" in result.stdout
        assert "SCENARIO" in result.stdout

    def test_cli_render_help(self):
        result = runner.invoke(app, ["render", "--help"])
        assert result.exit_code == 0
