"""Tests for provenance sensitivity bounds (FINDINGS.md Findings 4 and 5)."""

from __future__ import annotations

import pytest

from cohortfit.frequencies import load_gene_frequencies, load_gene_provenance
from cohortfit.sensitivity import (
    discrepancy_candidates,
    phenotype_bounds,
    substitute_allele,
)

_AT_RISK = ("Intermediate Metabolizer", "Poor Metabolizer")

# FINDINGS.md Finding 4: pinned SAS at-risk, and the value at the Chan 2024
# upper bound (*2A = 0.015), the highest candidate in the fixture.
_SAS_AT_RISK_LOW = 0.038957
_SAS_AT_RISK_HIGH = 0.061721


@pytest.fixture
def dpyd_freqs():
    return load_gene_frequencies("DPYD", offline=True)


@pytest.fixture
def dpyd_provenance():
    return load_gene_provenance("DPYD")


@pytest.fixture
def sas_bounds(dpyd_freqs, dpyd_provenance):
    return phenotype_bounds("DPYD", dpyd_freqs, {"SAS": 1.0}, 1000, dpyd_provenance)


def _at_risk(bounds, index):
    return sum(v[index] for k, v in bounds.items() if k in _AT_RISK)


class TestDiscrepancyCandidates:
    def test_only_sas_2a_is_unresolved(self, dpyd_provenance):
        candidates = discrepancy_candidates(dpyd_provenance)
        assert candidates
        assert {(a, p) for a, p, _ in candidates} == {("*2A", "SAS")}

    def test_range_string_parsed_into_both_endpoints(self, dpyd_provenance):
        freqs = [f for _, _, f in discrepancy_candidates(dpyd_provenance)]
        assert 0.003 in freqs  # "0.003-0.015" low endpoint
        assert 0.015 in freqs  # ... and its high endpoint

    def test_sorted_and_deduplicated(self, dpyd_provenance):
        candidates = discrepancy_candidates(dpyd_provenance)
        assert candidates == sorted(set(candidates))

    def test_resolved_entries_skipped(self):
        provenance = {
            "known_discrepancies": [
                {
                    "allele": "*2A",
                    "population": "SAS",
                    "status": "RESOLVED - repinned 2026-01-01",
                    "conflicting_sources": {"somewhere": 0.009},
                }
            ]
        }
        assert discrepancy_candidates(provenance) == []

    def test_unparseable_source_skipped_not_guessed(self):
        provenance = {
            "known_discrepancies": [
                {
                    "allele": "*2A",
                    "population": "SAS",
                    "status": "UNRESOLVED",
                    "conflicting_sources": {"vague": "higher than pinned", "ok": 0.004},
                }
            ]
        }
        assert discrepancy_candidates(provenance) == [("*2A", "SAS", 0.004)]


class TestSubstituteAllele:
    def test_input_untouched(self, dpyd_freqs):
        before = dpyd_freqs["SAS"]["*2A"]
        substitute_allele(dpyd_freqs, "SAS", "*2A", 0.015)
        assert dpyd_freqs["SAS"]["*2A"] == before

    def test_output_population_still_sums_to_one(self, dpyd_freqs):
        out = substitute_allele(dpyd_freqs, "SAS", "*2A", 0.015)
        assert out["SAS"]["*2A"] == 0.015
        assert sum(out["SAS"].values()) == pytest.approx(1.0, abs=1e-12)

    def test_reference_allele_absorbs_the_change(self, dpyd_freqs):
        out = substitute_allele(dpyd_freqs, "SAS", "*2A", 0.015)
        delta = 0.015 - dpyd_freqs["SAS"]["*2A"]
        assert out["SAS"]["*1"] == pytest.approx(
            dpyd_freqs["SAS"]["*1"] - delta, abs=1e-12
        )

    def test_untouched_population_copied_unchanged(self, dpyd_freqs):
        out = substitute_allele(dpyd_freqs, "SAS", "*2A", 0.015)
        assert out["EUR"] == dpyd_freqs["EUR"]
        assert out["EUR"] is not dpyd_freqs["EUR"]


class TestPhenotypeBounds:
    def test_sas_at_risk_range(self, sas_bounds):
        assert _at_risk(sas_bounds, 0) == pytest.approx(_SAS_AT_RISK_LOW, abs=0.002)
        assert _at_risk(sas_bounds, 1) == pytest.approx(_SAS_AT_RISK_HIGH, abs=0.002)

    def test_at_risk_barely_moves_but_pm_moves_an_order_of_magnitude(self, sas_bounds):
        # Finding 4: this contrast is the whole point — the headline number is
        # robust, the Poor Metabolizer figure is not, so PM cannot be a point
        # estimate.
        im_low, im_high = sas_bounds["Intermediate Metabolizer"]
        pm_low, pm_high = sas_bounds["Poor Metabolizer"]
        assert im_high / im_low < 2
        assert pm_high / pm_low > 5

    def test_pm_stays_sub_patient_at_trial_scale(self, dpyd_freqs, dpyd_provenance):
        # Finding 5: even at the top of the range, a 230-person cohort expects
        # well under one Poor Metabolizer.
        bounds = phenotype_bounds(
            "DPYD", dpyd_freqs, {"SAS": 1.0}, 230, dpyd_provenance
        )
        assert bounds["Poor Metabolizer"][1] * 230 < 1.0

    def test_eur_bounds_collapse(self, dpyd_freqs, dpyd_provenance):
        # The only unresolved discrepancy is SAS-scoped, so a European cohort
        # has no provenance-driven movement at all.
        bounds = phenotype_bounds(
            "DPYD", dpyd_freqs, {"EUR": 1.0}, 1000, dpyd_provenance
        )
        assert bounds
        for low, high in bounds.values():
            assert low == high

    def test_no_unresolved_discrepancies_means_no_range(self, dpyd_freqs):
        assert phenotype_bounds("DPYD", dpyd_freqs, {"SAS": 1.0}, 1000, {}) == {}
