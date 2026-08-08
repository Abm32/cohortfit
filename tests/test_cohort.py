"""Tests for the Tier 0 cohort engine.

These pin the arithmetic that every downstream number depends on.
"""

from typing import ClassVar

import pytest

from cohortfit.cohort import (
    blend_allele_frequencies,
    cohort_ancestry_mix,
    diplotype_frequencies,
    phenotype_distribution,
)
from cohortfit.models import Site


class TestDiplotypeFrequencies:
    def test_hardy_weinberg_sums_to_one(self):
        freqs = diplotype_frequencies({"*1": 0.9, "*2": 0.1})
        assert sum(freqs.values()) == pytest.approx(1.0)

    def test_homozygote_is_p_squared(self):
        freqs = diplotype_frequencies({"*1": 0.9, "*2": 0.1})
        assert freqs[("*2", "*2")] == pytest.approx(0.01)

    def test_heterozygote_is_two_pq(self):
        freqs = diplotype_frequencies({"*1": 0.9, "*2": 0.1})
        assert freqs[("*1", "*2")] == pytest.approx(0.18)

    def test_three_alleles_sum_to_one(self):
        freqs = diplotype_frequencies({"*1": 0.8, "*2": 0.15, "*3": 0.05})
        assert sum(freqs.values()) == pytest.approx(1.0)
        assert len(freqs) == 6  # 3 homozygous + 3 heterozygous

    def test_diplotype_keys_are_sorted(self):
        freqs = diplotype_frequencies({"*2": 0.1, "*1": 0.9})
        assert ("*1", "*2") in freqs
        assert ("*2", "*1") not in freqs


class TestCohortAncestryMix:
    def test_single_site_passes_through(self):
        sites = [Site(name="A", country="IN", planned_n=100, ancestry_mix={"SAS": 1.0})]
        assert cohort_ancestry_mix(sites) == {"SAS": 1.0}

    def test_weighted_by_planned_n(self):
        sites = [
            Site(name="A", country="IN", planned_n=300, ancestry_mix={"SAS": 1.0}),
            Site(name="B", country="DE", planned_n=100, ancestry_mix={"EUR": 1.0}),
        ]
        mix = cohort_ancestry_mix(sites)
        assert mix["SAS"] == pytest.approx(0.75)
        assert mix["EUR"] == pytest.approx(0.25)

    def test_mixed_site_contributes_to_both(self):
        sites = [
            Site(name="A", country="IN", planned_n=100, ancestry_mix={"SAS": 0.7, "EUR": 0.3}),
        ]
        mix = cohort_ancestry_mix(sites)
        assert mix["SAS"] == pytest.approx(0.7)
        assert mix["EUR"] == pytest.approx(0.3)

    def test_empty_sites_returns_empty(self):
        assert cohort_ancestry_mix([]) == {}

    def test_zero_planned_n_does_not_divide_by_zero(self):
        sites = [Site(name="A", country="IN", planned_n=0, ancestry_mix={"SAS": 1.0})]
        assert cohort_ancestry_mix(sites) == {}


class TestBlendAlleleFrequencies:
    PER_POP: ClassVar[dict[str, dict[str, float]]] = {
        "SAS": {"*1": 0.9, "*2": 0.1},
        "EUR": {"*1": 0.8, "*2": 0.2},
    }

    def test_single_population_passes_through(self):
        out = blend_allele_frequencies(self.PER_POP, {"SAS": 1.0})
        assert out["*2"] == pytest.approx(0.1)

    def test_even_blend_is_midpoint(self):
        out = blend_allele_frequencies(self.PER_POP, {"SAS": 0.5, "EUR": 0.5})
        assert out["*2"] == pytest.approx(0.15)

    def test_missing_population_is_skipped_and_renormalised(self):
        # AFR has no pinned data; SAS should absorb the full weight rather than
        # the result silently summing to less than 1.
        out = blend_allele_frequencies(self.PER_POP, {"SAS": 0.5, "AFR": 0.5})
        assert out["*2"] == pytest.approx(0.1)
        assert sum(out.values()) == pytest.approx(1.0)

    def test_no_usable_population_returns_empty(self):
        assert blend_allele_frequencies(self.PER_POP, {"AFR": 1.0}) == {}


class TestPhenotypeDistribution:
    def test_expected_n_scales_with_cohort_size(self):
        diplo = {("*1", "*1"): 0.81, ("*1", "*2"): 0.18, ("*2", "*2"): 0.01}
        mapping = {
            ("*1", "*1"): "Normal Metabolizer",
            ("*1", "*2"): "Intermediate Metabolizer",
            ("*2", "*2"): "Poor Metabolizer",
        }
        dist = phenotype_distribution(diplo, mapping, planned_n=1000)
        pm = next(d for d in dist if d.phenotype == "Poor Metabolizer")
        assert pm.expected_n == pytest.approx(10.0)

    def test_unmapped_diplotype_becomes_indeterminate_not_dropped(self):
        diplo = {("*1", "*1"): 0.5, ("*1", "*99"): 0.5}
        mapping = {("*1", "*1"): "Normal Metabolizer"}
        dist = phenotype_distribution(diplo, mapping, planned_n=100)
        phenos = {d.phenotype: d.fraction for d in dist}
        assert phenos["Indeterminate"] == pytest.approx(0.5)
        assert sum(phenos.values()) == pytest.approx(1.0)

    def test_sorted_by_descending_fraction(self):
        diplo = {("*1", "*1"): 0.2, ("*1", "*2"): 0.8}
        mapping = {("*1", "*1"): "Poor Metabolizer", ("*1", "*2"): "Normal Metabolizer"}
        dist = phenotype_distribution(diplo, mapping, planned_n=100)
        assert dist[0].phenotype == "Normal Metabolizer"

    def test_fractions_preserved_through_aggregation(self):
        diplo = {("*1", "*1"): 0.81, ("*1", "*2"): 0.18, ("*2", "*2"): 0.01}
        mapping = dict.fromkeys(diplo, "Normal Metabolizer")
        dist = phenotype_distribution(diplo, mapping, planned_n=500)
        assert len(dist) == 1
        assert dist[0].fraction == pytest.approx(1.0)
        assert dist[0].expected_n == pytest.approx(500.0)
