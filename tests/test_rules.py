"""Tests for CPIC screening-gap rules."""

import pytest

from cohortfit.models import Protocol, Verdict
from cohortfit.rules import (
    mentions_screening,
    normalize_drug,
    resolve_gene,
    screening_gap,
)


def _demo_protocol_without_screening() -> Protocol:
    return Protocol(
        trial_id="NCT01095003",
        title="Demo",
        drugs=[],
        exclusion_criteria=[
            "Known hypersensitivity to capecitabine",
            "Severe renal impairment",
        ],
    )


def _demo_protocol_with_dpyd_screening() -> Protocol:
    return Protocol(
        trial_id="NCT01095003",
        title="Demo",
        drugs=[],
        exclusion_criteria=[
            "Known DPYD deficiency or DPD enzyme deficiency",
            "Hypersensitivity to capecitabine",
        ],
    )


class TestDrugGeneResolution:
    def test_capecitabine_maps_to_dpyd(self):
        assert resolve_gene("capecitabine") == "DPYD"

    def test_fluorouracil_aliases(self):
        assert resolve_gene("5-FU") == "DPYD"
        assert resolve_gene("5_fluorouracil") == "DPYD"

    def test_unknown_drug_returns_none(self):
        assert resolve_gene("aspirin") is None

    def test_normalize_drug_unifies_separators(self):
        assert normalize_drug("5_fluorouracil") == "5-fluorouracil"


class TestScreeningGap:
    def test_demo_protocol_actionable_missing_dpyd_screening(self):
        protocol = _demo_protocol_without_screening()
        verdict, missing, citations = screening_gap(protocol, "capecitabine", "DPYD")
        assert verdict == Verdict.ACTIONABLE
        assert missing is not None
        assert "DPYD" in missing
        assert "29152729" in citations

    def test_protocol_with_dpyd_exclusion_not_actionable(self):
        protocol = _demo_protocol_with_dpyd_screening()
        verdict, missing, _ = screening_gap(protocol, "capecitabine", "DPYD")
        assert verdict == Verdict.NO_SIGNAL
        assert missing is None

    def test_mentions_screening_detects_dpd(self):
        protocol = Protocol(
            title="T",
            drugs=[],
            exclusion_criteria=["DPD deficiency"],
        )
        assert mentions_screening(protocol, "DPYD") is True

    def test_non_fluoropyrimidine_no_signal(self):
        protocol = _demo_protocol_without_screening()
        verdict, _, _ = screening_gap(protocol, "warfarin", "CYP2C9")
        assert verdict == Verdict.NO_SIGNAL


class TestScreeningIsGeneScoped:
    """Generic PGx wording about another gene must not mask the DPYD gap.

    Oncology protocols routinely genotype HER2, KRAS or EGFR. Counting those as
    DPYD screening produces a false NO_SIGNAL on the exact finding this tool
    exists to produce.
    """

    @pytest.mark.parametrize(
        "criterion",
        [
            "HER2 genotype negative by central testing",
            "Documented KRAS wild-type status by genetic testing",
            "EGFR mutation testing required prior to enrolment",
            "Pharmacogenomic analysis of CYP2D6 for the companion study",
        ],
    )
    def test_unrelated_marker_genotyping_is_not_dpyd_screening(self, criterion):
        protocol = Protocol(title="T", drugs=[], exclusion_criteria=[criterion])
        assert mentions_screening(protocol, "DPYD") is False

    def test_unrelated_genotyping_still_yields_actionable_verdict(self):
        protocol = Protocol(
            title="T",
            drugs=[],
            exclusion_criteria=[
                "HER2 genotype negative by central testing",
                "Known hypersensitivity to capecitabine",
            ],
        )
        verdict, missing, _ = screening_gap(protocol, "capecitabine", "DPYD")
        assert verdict == Verdict.ACTIONABLE
        assert missing is not None

    @pytest.mark.parametrize(
        "criterion",
        [
            "Known DPYD poor metabolizer status",
            "DPD enzyme deficiency",
            "Dihydropyrimidine dehydrogenase deficiency (complete or partial)",
            "DPYD genotype testing required before cycle 1",
            "Pharmacogenomic screening for dihydropyrimidine dehydrogenase",
        ],
    )
    def test_gene_specific_wording_counts_as_screening(self, criterion):
        protocol = Protocol(title="T", drugs=[], exclusion_criteria=[criterion])
        assert mentions_screening(protocol, "DPYD") is True

    def test_generic_and_specific_terms_in_separate_criteria_do_not_combine(self):
        """A DPYD mention in one criterion and 'genotype' in another is not proof.

        Only same-criterion co-occurrence counts, so an unrelated genotyping
        line cannot borrow credibility from a DPYD mention elsewhere.
        """
        protocol = Protocol(
            title="T",
            drugs=[],
            exclusion_criteria=["HER2 genotype negative"],
            inclusion_criteria=["Prior fluoropyrimidine exposure permitted"],
        )
        assert mentions_screening(protocol, "DPYD") is False
