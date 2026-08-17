"""Tests for table-direct diplotype → phenotype adapter."""

from __future__ import annotations

import pytest
from anukriti_pgx_core import PhenotypeEngine

from cohortfit.cohort import diplotype_frequencies
from cohortfit.frequencies import load_gene_frequencies, load_ground_truth
from cohortfit.pgx import (
    cohort_phenotype_distribution,
    load_diplotype_table,
    lookup_phenotype,
    phenotype_map_for_alleles,
    table_citation,
)

CPIC_PANEL_ALLELES = ["*1", "*2A", "*13", "c.2846A>T", "HapB3"]


class TestLoadDiplotypeTable:
    def test_load_dpyd_table_metadata(self):
        table = load_diplotype_table("DPYD")
        assert table.gene == "DPYD"
        assert table.table_id == "DPYD_diplotypes_anukriti_v2024.01"
        assert "CPIC" in table.source
        # pgx-core 0.7.2 regenerates this table from api.cpicpgx.org and stamps
        # the CPIC guideline version rather than a bare table date.
        assert "CPIC 2017 guideline" in table.version
        # The table is the full unordered cross-product of *1 plus every
        # callable panel allele, so its size tracks the panel: 16 -> 105 at
        # pgx-core 0.7.2 (13 alleles), 105 -> 190 at 0.9.0 (18 alleles, adding
        # the causal HapB3 variant c.1129-5923C>G, its tag SNP as a separate
        # label, and c.2279C>T / c.2639G>T / c.1475C>T).
        #
        # Asserted as a floor rather than an exact count: the property that
        # matters is that no callable diplotype is missing (a gap returns
        # "Indeterminate", indistinguishable downstream from a genuinely
        # unresolvable genotype), and a growing panel is not a regression.
        # A hardcoded equality here just has to be edited on every engine bump,
        # which is how a test starts asserting the wrong thing confidently.
        assert len(table.diplotype_phenotypes) >= 105

    def test_table_citation_includes_source(self):
        table = load_diplotype_table("DPYD")
        cite = table_citation(table)
        assert "DPYD_diplotypes_anukriti_v2024.01" in cite
        assert "CPIC" in cite


class TestLookupPhenotype:
    @pytest.fixture
    def table(self):
        return load_diplotype_table("DPYD")

    def test_lookup_both_key_orders(self, table):
        assert lookup_phenotype(table, "*1", "*2A") == "Intermediate Metabolizer"
        assert lookup_phenotype(table, "*2A", "*1") == "Intermediate Metabolizer"

    def test_lookup_known_poor_metabolizer(self, table):
        assert lookup_phenotype(table, "*2A", "*2A") == "Poor Metabolizer"

    def test_lookup_normal_function_allele_is_now_resolved(self, table):
        """*9A is a CPIC *normal function* allele and must resolve as such.

        Before pgx-core 0.7.2 this returned "Indeterminate" purely because the
        diplotype table covered only 5 alleles. That mattered clinically for
        Indian cohorts specifically: *9A sits at 25.5% allele frequency in
        CPIC's Central/South Asian population — the single most common DPYD
        allele there — so the most frequent Indian genotypes were the ones
        landing in the unresolvable bucket.
        """
        assert lookup_phenotype(table, "*1", "*9A") == "Normal Metabolizer"

    def test_lookup_genuinely_unknown_diplotype_is_indeterminate(self, table):
        """A real absence must still be Indeterminate, not silently Normal."""
        assert lookup_phenotype(table, "*1", "*NOT_A_REAL_ALLELE") == "Indeterminate"

    def test_c2846_homozygote_is_intermediate_not_poor(self, table):
        """CPIC gives c.2846A>T/c.2846A>T activity score 1.0 -> Intermediate.

        Corrected in pgx-core 0.7.2; the table previously said Poor Metabolizer.
        """
        assert lookup_phenotype(table, "c.2846A>T", "c.2846A>T") == (
            "Intermediate Metabolizer"
        )


class TestPhenotypeMap:
    @pytest.fixture
    def table(self):
        return load_diplotype_table("DPYD")

    def test_phenotype_map_covers_hwe_keys(self, table):
        pheno_map = phenotype_map_for_alleles(table, CPIC_PANEL_ALLELES)
        diplo_keys = set(diplotype_frequencies(dict.fromkeys(CPIC_PANEL_ALLELES, 0.2)))
        assert set(pheno_map.keys()) == diplo_keys

    def test_no_indeterminate_for_cpic_panel(self, table):
        pheno_map = phenotype_map_for_alleles(table, CPIC_PANEL_ALLELES)
        assert all(p != "Indeterminate" for p in pheno_map.values())


class TestParityWithPhenotypeEngine:
    """Regression guard only — production path does not use PhenotypeEngine."""

    def test_parity_with_phenotype_engine(self):
        table = load_diplotype_table("DPYD")
        engine = PhenotypeEngine()
        for key, expected in table.diplotype_phenotypes.items():
            a, b = key.split("/")
            got = lookup_phenotype(table, a, b)
            engine_pheno = engine.infer("DPYD", a, b).phenotype or "Indeterminate"
            assert got == expected == engine_pheno


class TestCohortPhenotypeDistribution:
    GT = load_ground_truth("DPYD")

    @pytest.mark.parametrize("population", ["SAS", "EUR"])
    def test_cohort_phenotype_matches_fixture_ground_truth(self, population: str):
        allele_freqs = load_gene_frequencies("DPYD")[population]
        dist, table = cohort_phenotype_distribution("DPYD", allele_freqs, self.GT["planned_n"])

        by_name = {d.phenotype: d.fraction for d in dist}
        expected = self.GT[population]

        for pheno in ("Normal Metabolizer", "Intermediate Metabolizer", "Poor Metabolizer"):
            assert by_name[pheno] == pytest.approx(expected[pheno], abs=1e-4)

        assert "CPIC" in table.source
        assert "DPYD_diplotypes" in table.table_id
