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
[fixtures/frequencies/dpyd.json](fixtures/frequencies/dpyd.json) holds the
pinned gnomAD v4.0 allele frequencies and is loaded through
[src/cohortfit/frequencies.py](src/cohortfit/frequencies.py), which rejects any
entry without source metadata,
[src/cohortfit/phenotype.py](src/cohortfit/phenotype.py) is the only module
that calls into `anukriti-pgx-core` for diplotype→phenotype, and
[src/cohortfit/rules.py](src/cohortfit/rules.py) hardcodes the DPYD
screening-gap check (not a general rule engine — extend only when a second
gene-drug pair is in scope).

[src/cohortfit/panel.py](src/cohortfit/panel.py) and
[src/cohortfit/sensitivity.py](src/cohortfit/sensitivity.py) compute two
results `docs/FINDINGS.md` had only asserted; neither adds data or a model.
`panel.panel_concentration()` is a Herfindahl index over the non-reference
allele pool — effective allele count, dominant allele's share, and the alleles
pinned at 0.0 that never fire — while `panel.burden_shares()` is leave-one-out
ablation through the real Tier 0 pipeline, giving each dropped allele's
frequency back to `*1` so the sum-to-one invariant `diplotype_frequencies()`
requires still holds. `at_risk_fraction` is re-exported from `sites` rather
than redefined. `sensitivity.phenotype_bounds()` reruns the blend + HWE path
once per candidate value recorded in the fixture's `_meta.known_discrepancies`
and returns phenotype → (min, max); `substitute_allele()` re-derives the
reference allele as the remainder and raises rather than feeding a negative
reference frequency into Hardy-Weinberg. Ablation and substitution both
preserve that invariant on purpose — a scenario that does not sum to 1.0 is a
silently wrong distribution, not an error.

[src/cohortfit/precision.py](src/cohortfit/precision.py) answers a different
question from `sensitivity.py`: not "which source do we believe" but "how well
did the panel measure this at all". `alt_observed` / `total_alleles` is a
binomial numerator and denominator, so `wilson_interval()` gives a 95% interval
per pinned frequency — Wilson rather than the normal approximation because these
frequencies are small enough that `p ± z·sqrt(p(1-p)/n)` yields negative lower
bounds, and a negative frequency reaching Hardy-Weinberg would break the
sum-to-one invariant. `detection_floor()` is the rule-of-three bound, which is
what makes an unobserved allele reportable as *not detected* rather than
*absent*. `precision_notes()` is scoped to the populations the cohort actually
blended, so a report carries no caveats about ancestry groups it never used, and
only flags alleles that are unobserved or exceed 25% relative width — a
threshold that is a judgement call the module states outright. Sampling
precision is reported **alongside** the provenance range on `PhenotypeCount`,
never compounded into it: provenance uncertainty is ~6× wider for SAS, so a
single merged interval would mean neither thing.

`Verdict.CONTESTED` is now reachable. `rules.contested_burden()` is a pure
function over an already-computed burden-share map and fires when an allele
whose CPIC dose action is disputed holds ≥60% of a cohort's actionable burden
(the threshold is a judgement call and the code says so). It raises a *second*
finding on the same gene rather than a note on the first, because "screen for
this" and "a positive screen has no settled response" are different claims.
`models.PhenotypeCount` carries `fraction_low`/`fraction_high` from
`sensitivity`, so `render` prints a "Range (provenance)" column with the
fold-change; Tier 0 `notes` (panel coverage, partial-ancestry caveats) are
printed rather than stored and dropped, and every finding renders before the
site-burden tables. `audit.py` wires all of this — it remains the only module
loading fixtures end to end.

The demo catalogue in
[src/cohortfit/api/routes/fixtures.py](src/cohortfit/api/routes/fixtures.py) is
the single source for what each pinned protocol demonstrates. `GET
/fixtures/protocols` serves it and `web/src/components/DatasetCards.tsx` renders
it verbatim — the strings are *not* duplicated in TypeScript, because a card
promising `NO_SIGNAL` on a protocol that returns `ACTIONABLE` is a false claim
rendered on screen, which is the defect class this project exists to catch.
`tests/test_catalogue.py` audits every catalogued protocol through the real
engine and asserts the promise against the result; adding a protocol means adding
a `_CATALOGUE` entry and letting that test check it, not editing a component. The
internal `file` key is stripped from the response, and `/fixtures/protocols/demo`
must keep resolving because clients predating the catalogue call it directly.

## Build, Test, and Development Commands
- `pip install -e ".[dev]"` — install with test/lint dependencies.
- `pip install -e ".[web,dev]"` — add FastAPI/uvicorn for `cohortfit serve`.
- `cohortfit serve --port 8000` — API + built `web/dist` static UI.
- `pytest` — run the test suite (`testpaths = ["tests"]`, strict markers).
- `pytest tests/test_cohort.py::TestDiplotypeFrequencies::test_hardy_weinberg_sums_to_one` — run a single test.
- `pytest tests/test_audit.py` — pipeline + ground-truth tests for the wired DPYD engine.
- `pytest tests/test_panel.py tests/test_sensitivity.py` — panel concentration, ablation shares, and provenance bounds; every figure is asserted against the pinned fixture.
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
