"""Sampling precision — Wilson intervals and the observed-zero distinction.

Pins FINDINGS.md Findings 9 and 11: the fixture's own ``alt_observed`` /
``total_alleles`` counts are enough to state how precisely each frequency was
measured, and a frequency pinned at 0.0 on zero observations means "not
detected", not "absent".
"""

from __future__ import annotations

import pytest

from cohortfit.audit import audit_protocol
from cohortfit.frequencies import load_gene_provenance
from cohortfit.models import DoseRegimen, Protocol, Site
from cohortfit.precision import (
    allele_precision,
    detection_floor,
    population_precision,
    precision_notes,
    wilson_interval,
)


class TestWilsonInterval:
    def test_brackets_the_point_estimate(self):
        low, high = wilson_interval(45, 91074)
        assert low < 45 / 91074 < high

    def test_never_returns_a_negative_lower_bound(self):
        """The normal approximation would go negative here; Wilson must not.

        A negative frequency reaching Hardy-Weinberg would break the
        sum-to-one invariant, so this is a correctness property, not cosmetics.
        """
        low, _ = wilson_interval(1, 100000)
        assert low >= 0.0

    def test_zero_observations_start_at_zero(self):
        low, high = wilson_interval(0, 91074)
        assert low == 0.0
        assert high > 0.0

    def test_bounds_stay_within_unit_interval(self):
        low, high = wilson_interval(10, 10)
        assert low >= 0.0
        assert high <= 1.0

    def test_larger_samples_give_tighter_intervals(self):
        narrow = wilson_interval(500, 1_000_000)
        wide = wilson_interval(5, 10_000)
        assert (narrow[1] - narrow[0]) < (wide[1] - wide[0])

    @pytest.mark.parametrize(
        ("successes", "trials"),
        [(-1, 100), (101, 100)],
    )
    def test_rejects_impossible_counts(self, successes, trials):
        with pytest.raises(ValueError):
            wilson_interval(successes, trials)

    def test_rejects_zero_trials(self):
        with pytest.raises(ValueError):
            wilson_interval(0, 0)


class TestDetectionFloor:
    def test_rule_of_three(self):
        assert detection_floor(91074) == pytest.approx(3.0 / 91074)

    def test_sas_floor_matches_finding_11(self):
        """0/91,074 is consistent with a frequency up to ~0.0033%."""
        assert detection_floor(91074) * 100 == pytest.approx(0.0033, abs=1e-4)

    def test_larger_sample_lowers_the_floor(self):
        assert detection_floor(1_179_718) < detection_floor(91_074)

    def test_rejects_zero_trials(self):
        with pytest.raises(ValueError):
            detection_floor(0)


class TestAllelePrecision:
    def test_record_without_counts_has_no_precision(self):
        """The reference allele is a computed remainder, not an observation."""
        assert allele_precision("*1", "SAS", {"frequency": 0.98}) is None

    def test_unobserved_allele_flagged_not_absent(self):
        entry = allele_precision(
            "*13", "SAS", {"frequency": 0.0, "alt_observed": 0, "total_alleles": 91074}
        )
        assert entry is not None
        assert entry.observed is False
        assert entry.relative_width is None
        assert "not detected, not absent" in entry.describe()

    def test_rare_allele_is_imprecise(self):
        entry = allele_precision(
            "*2A", "SAS", {"frequency": 0.0005, "alt_observed": 45, "total_alleles": 91074}
        )
        assert entry.imprecise is True
        assert entry.relative_width == pytest.approx(0.583, abs=0.02)

    def test_well_measured_allele_is_precise(self):
        entry = allele_precision(
            "*2A",
            "EUR",
            {"frequency": 0.00508, "alt_observed": 5992, "total_alleles": 1179520},
        )
        assert entry.imprecise is False
        assert entry.relative_width == pytest.approx(0.051, abs=0.01)


class TestPinnedFixturePrecision:
    """Ground truth from FINDINGS.md Finding 9."""

    @pytest.fixture(scope="class")
    @classmethod
    def precision(cls):
        return population_precision(load_gene_provenance("DPYD"))

    def test_covers_both_populations(self, precision):
        assert set(precision) == {"SAS", "EUR"}

    @pytest.mark.parametrize(
        ("population", "allele", "low", "high"),
        [
            ("SAS", "*2A", 0.000369, 0.000661),
            ("SAS", "c.2846A>T", 0.000398, 0.000699),
            ("SAS", "HapB3", 0.016071, 0.017745),
            ("EUR", "*2A", 0.004953, 0.005210),
            ("EUR", "HapB3", 0.020653, 0.021170),
        ],
    )
    def test_pinned_confidence_intervals(self, precision, population, allele, low, high):
        entry = next(e for e in precision[population] if e.allele == allele)
        assert entry.ci_low == pytest.approx(low, abs=1e-6)
        assert entry.ci_high == pytest.approx(high, abs=1e-6)

    def test_sas_rare_alleles_are_an_order_less_precise_than_eur(self, precision):
        """Finding 11: ~13x fewer SAS alleles sequenced shows up as CI width."""
        sas = next(e for e in precision["SAS"] if e.allele == "*2A")
        eur = next(e for e in precision["EUR"] if e.allele == "*2A")
        assert sas.relative_width > 10 * eur.relative_width

    def test_notes_are_scoped_to_cohort_populations(self, precision):
        sas_only = precision_notes(precision, {"SAS"})
        assert sas_only
        assert all("EUR" not in note for note in sas_only)

    def test_precise_observed_alleles_produce_no_note(self, precision):
        """EUR is well measured, so only *13 (36% width) should be flagged."""
        notes = precision_notes(precision, {"EUR"})
        assert all("HapB3" not in note for note in notes)


class TestPrecisionReachesTheReport:
    def test_sas_audit_carries_the_observed_zero_caveat(self):
        protocol = Protocol(
            title="SAS cohort",
            drugs=[DoseRegimen(drug="capecitabine")],
            exclusion_criteria=["Known hypersensitivity to capecitabine"],
            sites=[Site(name="Kochi", country="IN", planned_n=100, ancestry_mix={"SAS": 1.0})],
            target_n=100,
        )
        notes = " ".join(audit_protocol(protocol).findings[0].notes)
        assert "not detected, not absent" in notes
        assert "91,074" in notes
