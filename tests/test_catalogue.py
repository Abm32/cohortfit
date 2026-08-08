"""The fixture catalogue must describe what the fixtures actually do.

The UI cards render `demonstrates` / `expect` straight from this endpoint, so a
wrong string here is a wrong claim on screen. These tests run each catalogued
protocol through the real engine and check the promise against the result.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from cohortfit.api.app import app
from cohortfit.audit import audit_protocol
from cohortfit.models import Protocol

client = TestClient(app)


@pytest.fixture(scope="module")
def catalogue() -> list[dict]:
    response = client.get("/fixtures/protocols")
    assert response.status_code == 200
    return response.json()


class TestCatalogueShape:
    def test_lists_four_protocols(self, catalogue):
        assert len(catalogue) == 4

    def test_every_card_has_the_fields_the_ui_renders(self, catalogue):
        for card in catalogue:
            for field in ("slug", "title", "trial_id", "cohort", "demonstrates", "detail", "expect"):
                assert card.get(field), f"{card.get('slug')} missing {field}"

    def test_does_not_leak_filesystem_paths(self, catalogue):
        """`file` is an internal detail; the UI has no business with it."""
        assert all("file" not in card for card in catalogue)

    def test_slugs_are_unique(self, catalogue):
        slugs = [c["slug"] for c in catalogue]
        assert len(slugs) == len(set(slugs))


class TestCatalogueFetch:
    def test_each_slug_returns_a_valid_protocol(self, catalogue):
        for card in catalogue:
            response = client.get(f"/fixtures/protocols/{card['slug']}")
            assert response.status_code == 200
            Protocol.model_validate(response.json())

    def test_unknown_slug_404s_and_lists_the_known_ones(self):
        response = client.get("/fixtures/protocols/not-a-protocol")
        assert response.status_code == 404
        assert "demo" in response.json()["detail"]

    def test_demo_slug_still_resolves(self):
        """The pre-existing client called /fixtures/protocols/demo directly."""
        assert client.get("/fixtures/protocols/demo").status_code == 200


class TestCataloguePromisesAreTrue:
    """Each card's `expect` string is checked against a real audit."""

    def test_expected_verdicts_match_the_engine(self, catalogue):
        for card in catalogue:
            protocol = Protocol.model_validate(
                client.get(f"/fixtures/protocols/{card['slug']}").json()
            )
            verdicts = {f.verdict.value for f in audit_protocol(protocol).findings}
            promised = card["expect"]
            for verdict in ("ACTIONABLE", "CONTESTED", "NO_SIGNAL"):
                # Promises must be exact in both directions: a card that omits a
                # verdict the engine produces understates the result just as
                # badly as one that invents a verdict it does not.
                assert (verdict in promised) == (verdict in verdicts), (
                    f"{card['slug']} promises {promised!r} but produced {verdicts}"
                )

    def test_only_the_us_card_promises_a_coverage_warning(self, catalogue):
        for card in catalogue:
            protocol = Protocol.model_validate(
                client.get(f"/fixtures/protocols/{card['slug']}").json()
            )
            report = audit_protocol(protocol)
            has_gap = any("enrolment" in w.lower() for w in report.warnings)
            promises_gap = "coverage warning" in card["expect"].lower()
            assert has_gap == promises_gap, (
                f"{card['slug']}: coverage warning={has_gap}, card says {promises_gap}"
            )

    def test_no_signal_card_really_closes_the_screening_gap(self, catalogue):
        card = next(c for c in catalogue if "NO_SIGNAL" in c["expect"])
        protocol = Protocol.model_validate(
            client.get(f"/fixtures/protocols/{card['slug']}").json()
        )
        report = audit_protocol(protocol)
        assert all(
            f.missing_exclusion is None
            for f in report.findings
            if f.verdict.value == "NO_SIGNAL"
        )
