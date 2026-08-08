"""Integration tests for the audit orchestrator."""

from __future__ import annotations

from pathlib import Path

import pytest

from cohortfit.audit import audit_protocol, load_protocol
from cohortfit.frequencies import FixtureError, repo_root
from cohortfit.models import Verdict

DEMO_PROTOCOL = repo_root() / "protocols" / "demo.json"


class TestLoadProtocol:
    def test_load_demo_protocol(self):
        protocol = load_protocol(DEMO_PROTOCOL)
        assert protocol.trial_id == "NCT01095003"
        assert len(protocol.sites) == 3
        assert protocol.total_planned_n == 230

    def test_load_invalid_json_raises(self, tmp_path):
        bad = tmp_path / "bad.json"
        bad.write_text('{"title": "x"}', encoding="utf-8")
        with pytest.raises(Exception):
            load_protocol(bad)


class TestAuditDemoProtocol:
    @pytest.fixture
    def report(self):
        return audit_protocol(load_protocol(DEMO_PROTOCOL), offline=True)

    def test_offline_audit_runs(self, report):
        assert report.offline is True
        assert report.total_planned_n == 230
        assert len(report.findings) == 1

    def test_capecitabine_actionable_screening_gap(self, report):
        finding = report.findings[0]
        assert finding.gene == "DPYD"
        assert finding.drug == "capecitabine"
        assert finding.verdict == Verdict.ACTIONABLE
        assert finding.cpic_level == "A"
        assert finding.missing_exclusion is not None
        assert "29152729" in finding.citations

    def test_distribution_has_three_phenotype_classes(self, report):
        phenos = {d.phenotype for d in report.findings[0].distribution}
        assert "Normal Metabolizer" in phenos
        assert "Intermediate Metabolizer" in phenos
        assert "Poor Metabolizer" in phenos

    def test_cohort_im_expected_n_scales_to_230(self, report):
        dist = report.findings[0].distribution
        im = next(d for d in dist if d.phenotype == "Intermediate Metabolizer")
        # Enrolment-weighted SAS/EUR blend at n=230 (150 SAS + 80 EUR sites).
        assert im.expected_n == pytest.approx(10.41, abs=0.5)

    def test_site_findings_populated(self, report):
        assert len(report.site_findings) == 3

    def test_data_sources_include_gnomad_and_cpic(self, report):
        joined = " ".join(report.data_sources).lower()
        assert "gnomad" in joined
        assert "dpyd" in joined
        assert "cpic" in joined

    def test_offline_false_raises(self):
        protocol = load_protocol(DEMO_PROTOCOL)
        with pytest.raises(FixtureError, match="offline=True"):
            audit_protocol(protocol, offline=False)
