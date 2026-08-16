"""Tests for panel coverage concentration (FINDINGS.md Findings 1 and 2)."""

from __future__ import annotations

import pytest

from cohortfit.frequencies import load_gene_frequencies
from cohortfit.panel import (
    at_risk_fraction,
    burden_shares,
    coverage_note,
    panel_concentration,
)
from cohortfit.pgx import cohort_phenotype_distribution

_FREQS = load_gene_frequencies("DPYD")
_SAS = _FREQS["SAS"]
_EUR = _FREQS["EUR"]

# FINDINGS.md rounds to 3 significant figures; match that, not float equality.
_DOC = 0.005


class TestPanelConcentration:
    def test_sas_is_effectively_a_single_allele_panel(self):
        c = panel_concentration(_SAS)
        assert c.effective_alleles == pytest.approx(1.5407, abs=_DOC)
        assert c.hhi == pytest.approx(0.6490, abs=_DOC)
        assert c.total_variant_load == pytest.approx(0.020732, abs=1e-5)

    def test_sas_dominant_allele_is_hapb3(self):
        c = panel_concentration(_SAS)
        assert c.dominant_allele == "HapB3"
        assert c.dominant_share == pytest.approx(0.7818, abs=_DOC)

    def test_sas_star13_is_silent(self):
        assert panel_concentration(_SAS).silent_alleles == ("*13",)

    def test_eur_is_a_genuine_multi_allele_panel(self):
        c = panel_concentration(_EUR)
        assert c.effective_alleles == pytest.approx(2.1457, abs=_DOC)
        assert c.hhi == pytest.approx(0.4660, abs=_DOC)

    def test_eur_dominant_allele_is_hapb3_but_less_dominant(self):
        c = panel_concentration(_EUR)
        assert c.dominant_allele == "HapB3"
        assert c.dominant_share == pytest.approx(0.6386, abs=_DOC)

    def test_eur_has_no_silent_alleles(self):
        assert panel_concentration(_EUR).silent_alleles == ()

    def test_effective_alleles_is_reciprocal_of_hhi(self):
        c = panel_concentration(_EUR)
        assert c.effective_alleles == pytest.approx(1 / c.hhi, abs=1e-12)

    def test_all_reference_population_has_no_variant_pool(self):
        c = panel_concentration({"*1": 1.0})
        assert c.total_variant_load == 0.0
        assert c.hhi == 0.0
        assert c.effective_alleles == 0.0
        assert c.dominant_allele is None
        assert c.silent_alleles == ()


class TestBurdenShares:
    def test_sas_burden_rests_on_hapb3(self):
        shares = burden_shares("DPYD", _SAS)
        assert shares["HapB3"] == pytest.approx(0.7800, abs=_DOC)

    def test_sas_minor_alleles_contribute_almost_nothing(self):
        shares = burden_shares("DPYD", _SAS)
        assert shares["c.2846A>T"] == pytest.approx(0.0252, abs=_DOC)
        assert shares["*2A"] == pytest.approx(0.1911, abs=_DOC)

    def test_sas_silent_allele_contributes_exactly_zero(self):
        assert burden_shares("DPYD", _SAS)["*13"] == 0.0

    def test_eur_burden_is_spread_across_three_alleles(self):
        shares = burden_shares("DPYD", _EUR)
        assert shares["HapB3"] == pytest.approx(0.6346, abs=_DOC)
        assert shares["c.2846A>T"] == pytest.approx(0.1893, abs=_DOC)
        assert shares["*2A"] == pytest.approx(0.1422, abs=_DOC)

    def test_reference_allele_is_not_ablated(self):
        assert "*1" not in burden_shares("DPYD", _SAS)

    def test_ablation_preserves_sum_to_one_invariant(self):
        # diplotype_frequencies() is only valid on a complete allele space, so
        # every ablated table must still sum to 1.0.
        for allele, freq in _SAS.items():
            if allele == "*1":
                continue
            ablated = {a: f for a, f in _SAS.items() if a != allele}
            ablated["*1"] += freq
            assert sum(ablated.values()) == pytest.approx(1.0, abs=1e-12)
            assert len(ablated) == len(_SAS) - 1

    def test_all_reference_cohort_gives_empty_shares(self):
        assert burden_shares("DPYD", {"*1": 1.0}) == {}


class TestAtRiskFraction:
    def test_sas_matches_pinned_ground_truth(self):
        distribution, _ = cohort_phenotype_distribution("DPYD", _SAS, 1000)
        assert at_risk_fraction(distribution) == pytest.approx(0.041036, abs=1e-6)

    def test_eur_matches_pinned_ground_truth(self):
        distribution, _ = cohort_phenotype_distribution("DPYD", _EUR, 1000)
        assert at_risk_fraction(distribution) == pytest.approx(0.065859, abs=1e-6)


class TestCoverageNote:
    def test_sas_note_names_dominant_and_silent_alleles(self):
        note = coverage_note(panel_concentration(_SAS), burden_shares("DPYD", _SAS))
        assert note == (
            "Panel concentration: 1.54 effective alleles; "
            "HapB3 carries 78.0% of actionable burden; "
            "*13 never fires (pinned frequency 0.0)."
        )

    def test_eur_note_omits_never_fires_clause(self):
        note = coverage_note(panel_concentration(_EUR), burden_shares("DPYD", _EUR))
        assert "never fires" not in note
        assert note == (
            "Panel concentration: 2.15 effective alleles; "
            "HapB3 carries 63.5% of actionable burden."
        )
