"""Tests for CPIC screening-gap rules."""

import pytest

from cohortfit.models import Protocol, Site, Verdict
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
