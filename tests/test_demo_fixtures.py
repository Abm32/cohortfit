"""Demo fixtures must keep demonstrating what the demo says they demonstrate.

Each protocol in `protocols/` was chosen to exercise a different path. If a
refactor collapses two of those paths, the demo narrative silently stops being
true — these tests fail instead. See docs/DATASETS.md.
"""

from __future__ import annotations

import pytest

from cohortfit.audit import audit_protocol, load_protocol
from cohortfit.frequencies import repo_root
from cohortfit.models import Verdict


def _audit(name: str):
    return audit_protocol(load_protocol(repo_root() / "protocols" / name))


def _verdicts(report) -> set[Verdict]:
    return {f.verdict for f in report.findings}


def _coverage_warnings(report) -> list[str]:
    return [w for w in report.warnings if "enrolment" in w.lower()]


class TestDemoProtocolShowsSiteDelta:
    """Fixture 1: the site-selection argument."""

    def test_eur_site_has_higher_rate_than_sas_sites(self):
        report = _audit("demo.json")
        rates = {s.site_name: s.at_risk_fraction for s in report.site_findings}
        assert rates["Munich"] > rates["Mumbai"]
        assert rates["Mumbai"] == pytest.approx(rates["Kochi"]), (
            "same ancestry must give the same rate; only expected_n differs"
        )
        assert rates["Munich"] / rates["Mumbai"] == pytest.approx(1.80, abs=0.01)


class TestIndiaProtocolIsActionableAndContested:
    """Fixture 2: the HapB3 concentration story."""

    def test_raises_both_actionable_and_contested(self):
        report = _audit("capecitabine_india.json")
        assert _verdicts(report) == {Verdict.ACTIONABLE, Verdict.CONTESTED}

    def test_has_no_coverage_gap(self):
        assert not _coverage_warnings(_audit("capecitabine_india.json"))


class TestUsProtocolSurfacesCoverageGap:
    """Fixture 3: the honesty demonstration."""

    def test_drops_afr_and_amr_and_says_so(self):
        report = _audit("us_multiancestry.json")
        finding = report.findings[0]
        assert set(finding.coverage.dropped) == {"AFR", "AMR"}
        assert finding.coverage.dropped_weight == pytest.approx(0.348, abs=0.01)
        warnings = _coverage_warnings(report)
        assert warnings, "a dropped third of enrolment must be reported"
        assert "35%" in warnings[0]

    def test_still_reaches_a_verdict_on_the_covered_fraction(self):
        assert Verdict.ACTIONABLE in _verdicts(_audit("us_multiancestry.json"))


class TestScreenedProtocolIsNoSignal:
    """Fixture 4: proves the screening-gap rule discriminates."""

    def test_dpyd_screening_present_yields_no_signal(self):
        report = _audit("dpyd_screened_compliant.json")
        screening = [f for f in report.findings if f.verdict != Verdict.CONTESTED]
        assert screening, "expected a screening-gap finding"
        assert all(f.verdict == Verdict.NO_SIGNAL for f in screening)
        assert all(f.missing_exclusion is None for f in screening)

    def test_contested_still_fires_because_hapb3_action_is_disputed(self):
        """Screening closes the gap; it does not settle the dose question."""
        assert Verdict.CONTESTED in _verdicts(_audit("dpyd_screened_compliant.json"))

    def test_actionable_and_screened_protocols_differ_only_in_verdict(self):
        """Same drug and ancestry, opposite verdict — the rule is the variable."""
        gap = _audit("capecitabine_india.json")
        screened = _audit("dpyd_screened_compliant.json")
        assert Verdict.ACTIONABLE in _verdicts(gap)
        assert Verdict.ACTIONABLE not in _verdicts(screened)


class TestExtractionSourceIsUsable:
    """Fixture 5: the prose the live extraction demo reads."""

    @pytest.fixture(scope="class")
    @classmethod
    def prose(cls):
        path = repo_root() / "protocols" / "sources" / "gastric_adj_2026.txt"
        return path.read_text(encoding="utf-8")

    def test_contains_every_field_the_extractor_must_find(self, prose):
        assert "capecitabine" in prose.lower()
        assert "1250 mg/m2" in prose
        assert "Inclusion criteria" in prose
        assert "Exclusion criteria" in prose
        assert "360" in prose

    def test_names_a_country_with_no_ancestry_prior(self, prose):
        """Dhaka is deliberate: BD has no country prior, so the gap is reported."""
        from cohortfit.ancestry import default_ancestry_mix

        assert "Dhaka" in prose
        assert default_ancestry_mix("BD") is None
