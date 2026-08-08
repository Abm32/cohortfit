"""Population-level coverage reporting.

`blend_allele_frequencies` renormalises away ancestry groups with no pinned
data. The resulting distribution still sums to 1.0, so the omission is
invisible unless the report says so explicitly. These tests pin that it does.
"""

import pytest

from cohortfit.audit import audit_protocol
from cohortfit.cohort import population_coverage
from cohortfit.frequencies import known_discrepancies
from cohortfit.models import DoseRegimen, Protocol, Site


def _protocol(sites: list[Site], *, title: str = "T") -> Protocol:
    return Protocol(
        title=title,
        drugs=[DoseRegimen(drug="capecitabine")],
        exclusion_criteria=["Known hypersensitivity to capecitabine"],
        sites=sites,
        target_n=sum(s.planned_n for s in sites) or 100,
    )


def _coverage_warnings(report) -> list[str]:
    """Warnings about ancestry coverage, excluding provenance/discrepancy notes."""
    return [
        w
        for w in report.warnings
        if "ancestry" in w.lower()
        or "enrolment" in w.lower()
        or "no sites" in w.lower()
    ]


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
        # Provenance warnings (e.g. known frequency discrepancies) may still be
        # present; what must be absent is any *coverage* warning.
        assert not _coverage_warnings(report)
        assert report.findings[0].coverage.is_complete is True


class TestUncomputableAncestryWarns:
    """An empty report must not read as 'no risk found'."""

    def test_country_prior_fills_missing_mix(self):
        report = audit_protocol(
            _protocol([Site(name="X", country="IN", planned_n=100, ancestry_mix={})])
        )
        assert len(report.findings) == 1
        assert not _coverage_warnings(report)

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


class TestKnownDiscrepanciesSurface:
    """A fixture whose cross-checks contradict its pinned value must say so."""

    def test_dpyd_records_the_2a_sas_conflict(self):
        discs = known_discrepancies("DPYD")
        assert discs, "DPYD fixture should record the *2A SAS exome/genome conflict"
        entry = discs[0]
        assert entry["allele"] == "*2A"
        assert entry["population"] == "SAS"
        assert entry["status"].startswith("UNRESOLVED")

    def test_audit_report_warns_about_unresolved_discrepancy(self):
        report = audit_protocol(
            _protocol(
                [Site(name="Kochi", country="IN", planned_n=100, ancestry_mix={"SAS": 1.0})]
            )
        )
        assert any("*2A" in w and "conflicts" in w for w in report.warnings)

    def test_data_sources_name_the_callset(self):
        report = audit_protocol(
            _protocol(
                [Site(name="Kochi", country="IN", planned_n=100, ancestry_mix={"SAS": 1.0})]
            )
        )
        assert any("exomes" in s for s in report.data_sources), (
            "exome vs genome callset must be explicit — they disagree for "
            "splice-region variants like *2A"
        )
