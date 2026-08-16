"""Integration tests for the audit orchestrator."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

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
        # Missing required fields must fail Pydantic validation, not merely
        # "raise something" — a blind Exception would also pass on a typo.
        with pytest.raises(ValidationError):
            load_protocol(bad)


class TestAuditDemoProtocol:
    @pytest.fixture
    def report(self):
        return audit_protocol(load_protocol(DEMO_PROTOCOL), offline=True)

    def test_offline_audit_runs(self, report):
        assert report.offline is True
        assert report.total_planned_n == 230
        # Two distinct findings on the same gene-drug pair: the protocol does
        # not screen (ACTIONABLE), and the allele carrying most of the burden
        # has no settled dose action (CONTESTED). Neither subsumes the other.
        assert [f.verdict for f in report.findings] == [
            Verdict.ACTIONABLE,
            Verdict.CONTESTED,
        ]

    def test_hapb3_dominance_emits_contested_finding(self, report):
        contested = next(f for f in report.findings if f.verdict is Verdict.CONTESTED)
        assert contested.gene == "DPYD"
        assert "HapB3" in contested.notes[0]
        # CPIC's own dosing caveat — a CONTESTED verdict without its source is
        # indistinguishable from a hedge.
        assert "37639651" in contested.citations

    def test_panel_coverage_note_on_actionable_finding(self, report):
        finding = report.findings[0]
        note = " ".join(finding.notes)
        assert "effective alleles" in note
        assert "HapB3" in note

    def test_poor_metabolizer_reported_as_a_range(self, report):
        by_pheno = {d.phenotype: d for d in report.findings[0].distribution}
        pm = by_pheno["Poor Metabolizer"]
        im = by_pheno["Intermediate Metabolizer"]
        assert pm.is_range and im.is_range
        # FINDINGS.md Finding 4: the provenance conflict moves PM by an order
        # of magnitude while IM stays plannable. If that contrast ever
        # collapses, the reason to show a range at all has gone.
        assert pm.fraction_high / pm.fraction_low > im.fraction_high / im.fraction_low

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
        assert im.expected_n == pytest.approx(11.36, abs=0.5)

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
