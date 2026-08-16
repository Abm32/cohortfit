"""Tests for pinned DPYD frequency fixtures and the offline loader."""

from __future__ import annotations

import pytest

from cohortfit.cohort import diplotype_frequencies, phenotype_distribution
from cohortfit.frequencies import (
    FixtureError,
    load_fixture,
    load_gene_frequencies,
    load_gene_provenance,
    load_ground_truth,
    validate_fixture,
)
from cohortfit.pgx import load_diplotype_table, phenotype_map_for_alleles


def _phenotype_map_for_fixture_alleles() -> dict[tuple[str, str], str]:
    """Build diplotype→phenotype map via table-direct adapter (not PhenotypeEngine)."""
    table = load_diplotype_table("DPYD")
    freqs = load_gene_frequencies("DPYD")
    alleles = sorted({a for pop in freqs.values() for a in pop})
    return phenotype_map_for_alleles(table, alleles)


class TestFixtureIntegrity:
    def test_dpyd_fixture_loads_and_validates(self):
        data = load_fixture("DPYD")
        validate_fixture(data)  # does not raise

    def test_dpyd_frequencies_sum_to_one(self):
        freqs = load_gene_frequencies("DPYD")
        for alleles in freqs.values():
            assert sum(alleles.values()) == pytest.approx(1.0)

    def test_dpyd_provenance_complete(self):
        prov = load_gene_provenance("DPYD")
        for alleles in prov["populations"].values():
            for name, record in alleles.items():
                assert record.get("source")
                if name != "*1":
                    assert record.get("rsid")
                    assert "alt_observed" in record
                    assert "total_alleles" in record

    def test_dpyd_star1_is_remainder(self):
        data = load_fixture("DPYD")
        for pop_data in data["populations"].values():
            alleles = pop_data["alleles"]
            variant_sum = sum(
                rec["frequency"] for name, rec in alleles.items() if name != "*1"
            )
            assert alleles["*1"]["frequency"] == pytest.approx(1.0 - variant_sum)
            assert alleles["*1"]["source"].startswith("computed remainder")

    def test_offline_guard_rejects_live_mode(self):
        with pytest.raises(FixtureError, match="offline=True"):
            load_gene_frequencies("DPYD", offline=False)

    def test_missing_gene_raises(self):
        with pytest.raises(FixtureError, match="No frequency fixture"):
            load_gene_frequencies("NOTREAL")


class TestGroundTruthPhenotypes:
    """Tier 0 ground truth: HWE + pgx-core DPYD table must match fixture pin."""

    PHENO_MAP = _phenotype_map_for_fixture_alleles()
    GT = load_ground_truth("DPYD")
    PLANNED_N = GT["planned_n"]

    @pytest.mark.parametrize("population", ["SAS", "EUR"])
    def test_phenotype_fractions_match_ground_truth(self, population: str):
        allele_freqs = load_gene_frequencies("DPYD")[population]
        diplo = diplotype_frequencies(allele_freqs)
        dist = phenotype_distribution(diplo, self.PHENO_MAP, planned_n=self.PLANNED_N)

        by_name = {d.phenotype: d.fraction for d in dist}
        expected = self.GT[population]

        for pheno in ("Normal Metabolizer", "Intermediate Metabolizer", "Poor Metabolizer"):
            assert by_name[pheno] == pytest.approx(expected[pheno], abs=1e-4)

    @pytest.mark.parametrize("population", ["SAS", "EUR"])
    def test_at_risk_fraction_matches_ground_truth(self, population: str):
        allele_freqs = load_gene_frequencies("DPYD")[population]
        diplo = diplotype_frequencies(allele_freqs)
        dist = phenotype_distribution(diplo, self.PHENO_MAP, planned_n=self.PLANNED_N)

        at_risk = sum(
            d.fraction
            for d in dist
            if d.phenotype in ("Poor Metabolizer", "Intermediate Metabolizer")
        )
        assert at_risk == pytest.approx(self.GT[population]["at_risk_fraction"], abs=1e-4)

    def test_sas_at_risk_expected_n_at_1000(self):
        """Demo-scale: ~35 IM + ~0 PM per 1000 SAS enrollees under CPIC panel."""
        allele_freqs = load_gene_frequencies("DPYD")["SAS"]
        diplo = diplotype_frequencies(allele_freqs)
        dist = phenotype_distribution(diplo, self.PHENO_MAP, planned_n=1000)
        im = next(d for d in dist if d.phenotype == "Intermediate Metabolizer")
        pm = next(d for d in dist if d.phenotype == "Poor Metabolizer")
        assert im.expected_n == pytest.approx(40.87, abs=0.1)
        assert pm.expected_n == pytest.approx(0.167, abs=0.05)

    def test_eur_higher_at_risk_than_sas(self):
        """CPIC-panel alleles: NFE carries higher IM+PM burden than SAS — honest pin."""
        sas = self.GT["SAS"]["at_risk_fraction"]
        eur = self.GT["EUR"]["at_risk_fraction"]
        assert eur > sas
