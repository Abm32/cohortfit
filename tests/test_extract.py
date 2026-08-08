"""Tests for Claude protocol extraction and ancestry inference."""

from __future__ import annotations

import json

import pytest
from typer.testing import CliRunner

from cohortfit.ancestry import apply_ancestry_defaults, default_ancestry_mix
from cohortfit.cli import app
from cohortfit.extract import (
    ExtractionError,
    extract_protocol,
    strip_json_fence,
    validate_protocol_json,
)
from cohortfit.frequencies import repo_root
from cohortfit.models import Protocol, Site

runner = CliRunner()
SOURCE = repo_root() / "protocols" / "sources" / "nct01095003.txt"
GOLDEN = repo_root() / "protocols" / "demo.json"


@pytest.fixture
def golden_protocol() -> Protocol:
    return Protocol.model_validate_json(GOLDEN.read_text(encoding="utf-8"))


@pytest.fixture
def source_text() -> str:
    return SOURCE.read_text(encoding="utf-8")


class TestStripJsonFence:
    def test_plain_json_unchanged(self):
        assert strip_json_fence('{"title": "x"}') == '{"title": "x"}'

    def test_strips_markdown_fence(self):
        raw = '```json\n{"title": "Trial"}\n```'
        assert strip_json_fence(raw) == '{"title": "Trial"}'


class TestValidateProtocolJson:
    def test_golden_demo_validates(self, golden_protocol):
        assert golden_protocol.trial_id == "NCT01095003"
        assert golden_protocol.drugs[0].drug == "capecitabine"

    def test_invalid_json_raises(self):
        with pytest.raises(ExtractionError):
            validate_protocol_json("{not json")

    def test_invalid_schema_raises(self):
        with pytest.raises(ExtractionError, match="Protocol validation"):
            validate_protocol_json('{"title": "x"}')  # missing drugs


class TestAncestryDefaults:
    def test_india_maps_to_sas(self):
        assert default_ancestry_mix("IN") == {"SAS": 1.0}

    def test_germany_maps_to_eur(self):
        assert default_ancestry_mix("DE") == {"EUR": 1.0}

    def test_apply_fills_empty_site_mix(self):
        protocol = Protocol(
            title="T",
            drugs=[{"drug": "capecitabine"}],
            sites=[
                Site(name="Mumbai", country="IN", planned_n=100, ancestry_mix={}),
            ],
        )
        updated = apply_ancestry_defaults(protocol)
        assert updated.sites[0].ancestry_mix == {"SAS": 1.0}

    def test_apply_preserves_existing_mix(self, golden_protocol):
        assert apply_ancestry_defaults(golden_protocol) == golden_protocol


class TestExtractProtocolMocked:
    def test_extract_matches_golden_with_mock(self, source_text, golden_protocol, monkeypatch):
        payload = golden_protocol.model_dump()
        for site in payload["sites"]:
            site["ancestry_mix"] = {}
        mock_json = json.dumps(payload)

        monkeypatch.setattr("cohortfit.extract._call_claude", lambda *a, **k: mock_json)
        extracted = extract_protocol(source_text, infer_ancestry=True)

        assert extracted.trial_id == golden_protocol.trial_id
        assert extracted.title == golden_protocol.title
        assert extracted.drugs[0].drug == "capecitabine"
        assert len(extracted.sites) == 3
        assert extracted.sites[0].ancestry_mix == {"SAS": 1.0}
        assert extracted.sites[2].ancestry_mix == {"EUR": 1.0}
        assert extracted.total_planned_n == 230

    def test_missing_anthropic_raises(self, source_text, monkeypatch):
        monkeypatch.setitem(__import__("sys").modules, "anthropic", None)
        with pytest.raises(ExtractionError, match="Anthropic SDK"):
            extract_protocol(source_text)


class TestExtractCli:
    def test_extract_help(self):
        result = runner.invoke(app, ["extract", "--help"])
        assert result.exit_code == 0

    def test_extract_cli_writes_output(self, tmp_path, golden_protocol, monkeypatch):
        payload = golden_protocol.model_dump()
        for site in payload["sites"]:
            site["ancestry_mix"] = {}
        monkeypatch.setattr(
            "cohortfit.extract._call_claude",
            lambda *a, **k: json.dumps(payload),
        )
        out = tmp_path / "out.json"
        result = runner.invoke(app, ["extract", str(SOURCE), "-o", str(out)])
        assert result.exit_code == 0
        written = Protocol.model_validate_json(out.read_text(encoding="utf-8"))
        assert written.trial_id == "NCT01095003"
