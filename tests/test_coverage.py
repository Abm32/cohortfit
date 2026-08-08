"""Population-level coverage reporting.

`blend_allele_frequencies` renormalises away ancestry groups with no pinned
data. The resulting distribution still sums to 1.0, so the omission is
invisible unless the report says so explicitly. These tests pin that it does.
"""

import pytest

from cohortfit.audit import audit_protocol
from cohortfit.cohort import population_coverage
from cohortfit.models import DoseRegimen, Protocol, Site


def _protocol(sites: list[Site], *, title: str = "T") -> Protocol:
    return Protocol(
        title=title,
        drugs=[DoseRegimen(drug="capecitabine")],
        exclusion_criteria=["Known hypersensitivity to capecitabine"],
        sites=sites,
        target_n=sum(s.planned_n for s in sites) or 100,
    )


class TestPopulationCoverage:
    def test_splits_covered_and_dropped(self):
        per_pop = {"SAS": {"*1": 1.0}, "EUR": {"*1": 1.0}}
        coverage = population_coverage(per_pop, {"EUR": 0.68, "AFR": 0.13, "AMR": 0.19})
        assert coverage.covered == {"EUR": 0.68}
        assert coverage.dropped == {"AFR": 0.13, "AMR": 0.19}
        assert coverage.dropped_weight == pytest.approx(0.32)
        assert coverage.is_complete is False

    def test_full_coverage_is_complete(self):
        per_pop = {"SAS": {"*1": 1.0}}
        coverage = population_coverage(per_pop, {"SAS": 1.0})
        assert coverage.is_complete is True
        assert coverage.dropped_weight == pytest.approx(0.0)


class TestPartialCoverageIsSurfaced:
    """A US cohort must not silently report European numbers."""

    def _us_report(self):
        return audit_protocol(
            _protocol(
                [
                    Site(
                        name="Houston",
                        country="US",
                        planned_n=100,
                        ancestry_mix={"EUR": 0.68, "AFR": 0.13, "AMR": 0.19},
                    )
                ]
            )
        )

    def test_dropped_populations_recorded_on_finding(self):
        finding = self._us_report().findings[0]
        assert finding.coverage is not None
        assert set(finding.coverage.dropped) == {"AFR", "AMR"}
        assert finding.coverage.dropped_weight == pytest.approx(0.32)

    def test_finding_carries_explanatory_note(self):
        finding = self._us_report().findings[0]
        assert finding.notes, "partial coverage must produce a note"
        note = finding.notes[0].lower()
        assert "afr" in note and "amr" in note
        assert "renormalised" in note

    def test_report_carries_coverage_warning(self):
        report = self._us_report()
        assert report.warnings
        assert any("32%" in w for w in report.warnings)

    def test_fully_covered_cohort_has_no_warning(self):
        report = audit_protocol(
            _protocol(
                [Site(name="Kochi", country="IN", planned_n=100, ancestry_mix={"SAS": 1.0})]
            )
        )
        assert report.warnings == []
        assert report.findings[0].coverage.is_complete is True


class TestUncomputableAncestryWarns:
    """An empty report must not read as 'no risk found'."""

    def test_country_prior_fills_missing_mix(self):
        report = audit_protocol(
            _protocol([Site(name="X", country="IN", planned_n=100, ancestry_mix={})])
        )
        assert len(report.findings) == 1
        assert report.warnings == []

    def test_unknown_country_without_mix_warns_instead_of_silence(self):
        report = audit_protocol(
            _protocol([Site(name="Y", country="ZZ", planned_n=100, ancestry_mix={})])
        )
        assert report.findings == []
        assert report.warnings
        joined = " ".join(report.warnings).lower()
        assert "not a finding of no risk" in joined

    def test_no_sites_warns(self):
        protocol = Protocol(
            title="No sites",
            drugs=[DoseRegimen(drug="capecitabine")],
            target_n=100,
        )
        report = audit_protocol(protocol)
        assert report.findings == []
        assert any("no sites" in w.lower() for w in report.warnings)
