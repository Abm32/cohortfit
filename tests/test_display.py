"""Golden tests for shared display formatters (CLI + web parity)."""

from cohortfit.display import (
    format_citation_list,
    format_expected_n,
    format_fraction,
    pubmed_url,
    tier_label,
    tier_subtitle,
)
from cohortfit.models import Tier

# Golden vectors — web/src/display.test.ts must match these strings.


class TestFormatFraction:
    def test_zero(self):
        assert format_fraction(0.0) == "0%"

    def test_poor_metabolizer_rare(self):
        assert format_fraction(0.000194) == "0.02%"

    def test_intermediate(self):
        assert format_fraction(0.0452) == "4.5%"

    def test_normal(self):
        assert format_fraction(0.9546) == "95.5%"


class TestFormatExpectedN:
    def test_zero(self):
        assert format_expected_n(0.0) == "0"

    def test_poor_metabolizer_small(self):
        assert format_expected_n(0.04) == "0.04"

    def test_intermediate(self):
        assert format_expected_n(10.4) == "10.4"


class TestTierMeta:
    def test_tier0(self):
        assert tier_label(Tier.DISTRIBUTION) == "TIER 0"
        assert "HWE" in tier_subtitle(Tier.DISTRIBUTION)

    def test_tier1(self):
        assert tier_label(Tier.BURDEN) == "TIER 1"

    def test_tier2(self):
        assert tier_label(Tier.SCENARIO) == "SCENARIO"


class TestCitations:
    def test_pubmed_url(self):
        assert pubmed_url("29152729") == "https://pubmed.ncbi.nlm.nih.gov/29152729/"

    def test_tier1_missing(self):
        assert "MISSING" in format_citation_list([], required=True)
