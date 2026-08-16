"""Tests for per-site metabolic burden (site-selection deltas)."""

from __future__ import annotations

import pytest

from cohortfit.audit import audit_protocol, load_protocol
from cohortfit.frequencies import load_gene_frequencies, repo_root
from cohortfit.sites import (
    burden_rate_ratio,
    rank_sites_by_burden,
    site_metabolic_burden,
)

DEMO_PROTOCOL = repo_root() / "protocols" / "demo.json"

# Pinned from fixtures/frequencies/dpyd.json _ground_truth at-risk fractions.
_SAS_AT_RISK = 0.041036
_EUR_AT_RISK = 0.065859


@pytest.fixture
def dpyd_freqs():
    return load_gene_frequencies("DPYD", offline=True)


@pytest.fixture
def demo_sites():
    return load_protocol(DEMO_PROTOCOL).sites


@pytest.fixture
def site_findings(dpyd_freqs, demo_sites):
    return site_metabolic_burden("DPYD", dpyd_freqs, demo_sites)


class TestSiteMetabolicBurden:
    def test_three_sites_for_demo_protocol(self, site_findings):
        assert len(site_findings) == 3
        assert {f.site_name for f in site_findings} == {"Mumbai", "Kochi", "Munich"}

    def test_mumbai_sas_at_risk_fraction(self, site_findings):
        mumbai = next(f for f in site_findings if f.site_name == "Mumbai")
        assert mumbai.gene == "DPYD"
        assert mumbai.at_risk_fraction == pytest.approx(_SAS_AT_RISK, abs=1e-4)

    def test_mumbai_expected_at_risk_n_scales_by_planned_n(self, site_findings):
        mumbai = next(f for f in site_findings if f.site_name == "Mumbai")
        assert mumbai.expected_at_risk_n == pytest.approx(
            _SAS_AT_RISK * 100, abs=0.01
        )

    def test_kochi_same_rate_as_mumbai(self, site_findings):
        by_site = {f.site_name: f for f in site_findings}
        assert by_site["Kochi"].at_risk_fraction == pytest.approx(
            by_site["Mumbai"].at_risk_fraction, abs=1e-9
        )

    def test_kochi_half_mumbai_expected_count(self, site_findings):
        by_site = {f.site_name: f for f in site_findings}
        assert by_site["Kochi"].expected_at_risk_n == pytest.approx(
            0.5 * by_site["Mumbai"].expected_at_risk_n, abs=1e-9
        )

    def test_munich_eur_higher_rate_than_mumbai(self, site_findings):
        by_site = {f.site_name: f for f in site_findings}
        assert by_site["Munich"].at_risk_fraction == pytest.approx(
            _EUR_AT_RISK, abs=1e-4
        )
        assert by_site["Munich"].at_risk_fraction > by_site["Mumbai"].at_risk_fraction

    def test_munich_expected_at_risk_n(self, site_findings):
        munich = next(f for f in site_findings if f.site_name == "Munich")
        assert munich.expected_at_risk_n == pytest.approx(_EUR_AT_RISK * 80, abs=0.01)


class TestSiteRanking:
    def test_rank_by_rate_munich_first(self, site_findings):
        ranked = rank_sites_by_burden(site_findings, gene="DPYD")
        assert ranked[0].site_name == "Munich"
        assert ranked[-1].site_name in {"Mumbai", "Kochi"}

    def test_burden_rate_ratio_munich_over_mumbai(self, site_findings):
        by_site = {f.site_name: f for f in site_findings}
        ratio = burden_rate_ratio(by_site["Munich"], by_site["Mumbai"])
        assert ratio == pytest.approx(_EUR_AT_RISK / _SAS_AT_RISK, abs=1e-3)
        assert ratio == pytest.approx(1.605, abs=0.05)

    def test_same_ancestry_sites_rate_ratio_is_one(self, site_findings):
        by_site = {f.site_name: f for f in site_findings}
        ratio = burden_rate_ratio(by_site["Mumbai"], by_site["Kochi"])
        assert ratio == pytest.approx(1.0, abs=1e-9)


class TestAuditIntegration:
    def test_audit_site_findings_match_sites_module(self, site_findings):
        report = audit_protocol(load_protocol(DEMO_PROTOCOL), offline=True)
        assert len(report.site_findings) == len(site_findings)
        for audit_f, module_f in zip(report.site_findings, site_findings):
            assert audit_f.site_name == module_f.site_name
            assert audit_f.at_risk_fraction == pytest.approx(
                module_f.at_risk_fraction, abs=1e-9
            )
            assert audit_f.expected_at_risk_n == pytest.approx(
                module_f.expected_at_risk_n, abs=1e-9
            )
