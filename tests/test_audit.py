"""Ground-truth test for the wired pipeline: one hardcoded SAS site, DPYD.

The pinned SAS allele frequencies (gnomAD v2.1.1) are:
    *2A 0.006, c.2846A>T 0.006, HapB3 0.012, *1 0.976 (derived).
Hardy-Weinberg over those four alleles gives an exact, hand-checkable
Normal/Intermediate/Poor split — this test pins that split as ground truth
so a change to the engine or the pinned table shows up as a diff here.
"""

import pytest

from cohortfit.allele_frequencies import population_allele_frequencies
from cohortfit.audit import audit_protocol
from cohortfit.models import DoseRegimen, Protocol, Site, Verdict


def _protocol(*, exclusion_criteria=()):
    return Protocol(
        title="Ground-truth capecitabine protocol",
        drugs=[DoseRegimen(drug="capecitabine")],
        exclusion_criteria=list(exclusion_criteria),
        sites=[Site(name="Kerala", country="IN", planned_n=100, ancestry_mix={"SAS": 1.0})],
    )


class TestPinnedSASFrequencies:
    def test_dpyd_sas_frequencies_sum_to_one(self):
        freqs = population_allele_frequencies("DPYD", "SAS")
        assert sum(freqs.values()) == pytest.approx(1.0)

    def test_dpyd_sas_pinned_values(self):
        freqs = population_allele_frequencies("DPYD", "SAS")
        assert freqs["*2A"] == pytest.approx(0.006)
        assert freqs["c.2846A>T"] == pytest.approx(0.006)
        assert freqs["HapB3"] == pytest.approx(0.012)
        assert freqs["*1"] == pytest.approx(0.976)


class TestAuditGroundTruth:
    def test_single_sas_site_phenotype_distribution(self):
        report = audit_protocol(_protocol())
        finding = report.findings[0]
        by_phenotype = {d.phenotype: d.fraction for d in finding.distribution}

        # Hand-derived from HWE over the pinned SAS allele frequencies above.
        assert by_phenotype["Normal Metabolizer"] == pytest.approx(0.952576, abs=1e-6)
        assert by_phenotype["Intermediate Metabolizer"] == pytest.approx(0.046992, abs=1e-6)
        assert by_phenotype["Poor Metabolizer"] == pytest.approx(0.000432, abs=1e-6)

    def test_distribution_sums_to_one(self):
        report = audit_protocol(_protocol())
        total = sum(d.fraction for d in report.findings[0].distribution)
        assert total == pytest.approx(1.0)


class TestScreeningGapVerdict:
    def test_missing_dpyd_screening_is_actionable(self):
        report = audit_protocol(_protocol(exclusion_criteria=["Pregnant or breastfeeding"]))
        finding = report.findings[0]
        assert finding.verdict == Verdict.ACTIONABLE
        assert finding.missing_exclusion is not None

    def test_present_dpyd_screening_is_no_signal(self):
        report = audit_protocol(_protocol(exclusion_criteria=["Known DPYD poor metabolizer status"]))
        finding = report.findings[0]
        assert finding.verdict == Verdict.NO_SIGNAL
        assert finding.missing_exclusion is None

    def test_non_fluoropyrimidine_protocol_has_no_finding(self):
        protocol = Protocol(
            title="Unrelated protocol",
            drugs=[DoseRegimen(drug="pembrolizumab")],
            sites=[Site(name="Kerala", country="IN", planned_n=100, ancestry_mix={"SAS": 1.0})],
        )
        report = audit_protocol(protocol)
        assert report.findings == []
