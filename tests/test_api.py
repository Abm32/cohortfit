"""Smoke tests for FastAPI routes."""

from __future__ import annotations

import json
import os

import pytest
from fastapi.testclient import TestClient

from cohortfit.api.app import app
from cohortfit.frequencies import repo_root

client = TestClient(app)

DEMO_PROTOCOL = repo_root() / "protocols" / "demo.json"


class TestHealth:
    def test_health(self):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


class TestFixtures:
    def test_sample_report(self):
        r = client.get("/fixtures/reports/sample")
        assert r.status_code == 200
        data = r.json()
        assert data["trial_id"] == "NCT01095003"
        assert "warnings" in data
        assert len(data["warnings"]) >= 1

    def test_demo_protocol(self):
        r = client.get("/fixtures/protocols/demo")
        assert r.status_code == 200
        assert "title" in r.json()


class TestAudit:
    def test_demo_audit_offline(self):
        protocol = json.loads(DEMO_PROTOCOL.read_text(encoding="utf-8"))
        r = client.post("/audit", json=protocol)
        assert r.status_code == 200
        report = r.json()
        assert report["offline"] is True
        assert len(report["findings"]) >= 1

    def test_validation_422(self):
        r = client.post("/audit", json={"title": "missing drugs"})
        assert r.status_code == 422


class TestProvenance:
    def test_dpyd(self):
        r = client.get("/provenance/DPYD")
        assert r.status_code == 200
        assert "populations" in r.json()


class TestExtract:
    def test_extract_503_without_key(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        r = client.post("/extract", json={"prose": "Trial of capecitabine."})
        assert r.status_code == 503

    @pytest.mark.skipif(
        not os.environ.get("ANTHROPIC_API_KEY"),
        reason="ANTHROPIC_API_KEY not set",
    )
    def test_extract_live(self):
        r = client.post(
            "/extract",
            json={"prose": "Phase 2 trial of capecitabine 1000mg/m2 BID."},
        )
        assert r.status_code == 200
        assert "drugs" in r.json()
