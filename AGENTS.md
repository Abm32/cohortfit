# Repository Guidelines

## Project Structure & Module Organization

`cohortfit` audits clinical trial protocols for pharmacogenomic (PGx) cohort
mismatch. The pipeline has a hard boundary: [src/cohortfit/models.py](src/cohortfit/models.py)
splits it into an *extraction side* (`Protocol`, `Site`, `DoseRegimen` —
Claude's only allowed output surface) and a *verdict side* (`AuditReport`,
`GeneDrugFinding`, `Verdict`, `Tier` — produced only by deterministic code).
[src/cohortfit/cohort.py](src/cohortfit/cohort.py) is the Tier 0 engine: pure
arithmetic (Hardy-Weinberg diplotype expansion, ancestry-weighted allele
blending) with no LLM or network calls past its inputs. Findings carry a
`Tier` (0 = arithmetic, defensible; 1 = needs a cited literature multiplier;
2 = labelled scenario, never a prediction) — preserve this distinction when
adding new computation. The `cohortfit` CLI lives in
[src/cohortfit/cli.py](src/cohortfit/cli.py) (`audit`, `render`, `extract`,
`serve`). The FastAPI backend is in [src/cohortfit/api/](src/cohortfit/api/).
The React UI is in [web/](web/). `protocols/` holds hand-authored
`Protocol`-schema JSON fixtures (e.g. `protocols/demo.json`) and source
prose under `protocols/sources/`.

[src/cohortfit/audit.py](src/cohortfit/audit.py) is the entry point that
wires the pipeline end to end: `audit_protocol(Protocol) -> AuditReport`.
It is currently scoped to one gene-drug pair, DPYD x fluoropyrimidines —
[src/cohortfit/allele_frequencies.py](src/cohortfit/allele_frequencies.py)
holds the pinned gnomAD v2.1.1 allele frequencies,
[src/cohortfit/phenotype.py](src/cohortfit/phenotype.py) is the only module
that calls into `anukriti-pgx-core` for diplotype→phenotype, and
[src/cohortfit/rules.py](src/cohortfit/rules.py) hardcodes the DPYD
screening-gap check (not a general rule engine — extend only when a second
gene-drug pair is in scope).

## Build, Test, and Development Commands

- `pip install -e ".[dev]"` — install with test/lint dependencies.
- `pip install -e ".[web,dev]"` — add FastAPI/uvicorn for `cohortfit serve`.
- `cohortfit serve --port 8000` — API + built `web/dist` static UI.
- `pytest` — run the test suite (`testpaths = ["tests"]`, strict markers).
- `pytest tests/test_cohort.py::TestDiplotypeFrequencies::test_hardy_weinberg_sums_to_one` — run a single test.
- `pytest tests/test_audit.py` — pipeline + ground-truth tests for the wired DPYD engine.
- `ruff check .` — lint (line-length 100, target py311, config in `pyproject.toml`).

## Coding Style & Naming Conventions

Python 3.11+, 4-space indent, `from __future__ import annotations` in new
modules. Pydantic v2 `BaseModel` for all data models. Ruff line-length 100.
Docstrings on modules and non-trivial functions explain *why* an arithmetic
or aggregation choice was made (e.g. why unmapped diplotypes become
`"Indeterminate"` instead of being dropped) — follow that pattern rather than
restating what the code does.

## Testing Guidelines

Framework: `pytest`. Tests live in `tests/`, one `Test<ThingBeingTested>`
class per function under test, methods named `test_<behavior>`. Tests pin
exact arithmetic (Hardy-Weinberg sums, weighted blends) with
`pytest.approx` — new arithmetic in `cohort.py` should get the same
treatment, including edge cases (empty input, zero denominator, missing
population data).

## Commit & Pull Request Guidelines

Commits follow Conventional Commits (`feat(scope): ...`, `chore: ...`,
`docs: ...`), imperative mood, scoped to one logical change (e.g.
`feat(cohort): Tier 0 Hardy-Weinberg cohort engine`).

## Design principle

Deterministic code decides; the model (Claude) only extracts structured
claims from protocol text. Never let generated code compute a frequency,
phenotype, or verdict — route it through pinned CPIC tables via
`anukriti-pgx-core` instead.
