# cohortfit

**Every trial protocol has an implicit genome it was written for. Nobody checks whether the patients you're enrolling actually have it.**

`cohortfit` reads a clinical trial protocol and computes the pharmacogenomic
phenotype distribution of the cohort that protocol will *actually* recruit, given
the ancestry mix of its planned sites.

A protocol's dose regimen and exclusion criteria are typically calibrated on a
largely European reference population. Run the same protocol at Indian sites and
a computable fraction of enrollees are metabolically mismatched to that dose.
They have adverse events, they drop out, the safety signal muddies, and the trial
slips — or fails.

Anthropic's own clinical-trial partner ICON puts it plainly: enrolment delays
hold up **up to 80% of trials**, and *"the barrier to getting medicines to
patients faster is operational, not scientific."*

## What it does

```
protocol ──▶ Claude (extraction only) ──▶ {drugs, dose regimen,
             (PDF / registry text)          inclusion/exclusion, sites, target N}
                                                      │
                                                      ▼
                              deterministic engine (no LLM past this line)
                              ├─ drug ──▶ PGx-actionable genes   (CPIC)
                              ├─ site ancestry mix ──▶ allele frequencies
                              │                        (gnomAD / IndiGenomes / 1000G, pinned)
                              ├─ Hardy–Weinberg ──▶ diplotype frequencies
                              └─ cohortfit.pgx ──▶ diplotype → phenotype
                                 (reads pgx-core CPIC JSON; no PhenotypeEngine)
                                                      │
                                                      ▼
                              expected cohort phenotype distribution
                              + missing exclusion criteria
                              + per-site metabolic burden deltas
```

**Claude never estimates a frequency or a phenotype.** It converts unstructured
protocol prose into structured claims. Every number in the output comes from a
pinned, citable table via [`anukriti-pgx-core`](https://github.com/AnukritiAi-hq/anukriti-pgx-core)
— 13 genes, canonical CPIC tables, zero runtime dependencies.

## Output tiers

Findings are tiered by what actually supports them. This is the contract:

| Tier | Claim | Basis |
|---|---|---|
| **0** | Expected phenotype distribution of the cohort | Arithmetic on pinned allele frequencies + CPIC tables. Fully defensible. |
| **1** | Expected excess toxicity burden | Requires a literature effect multiplier. Cited per claim. |
| **2** | Trial-outcome impact | Labelled **scenario**, never prediction. |

Verdicts carry the same discipline:

- `ACTIONABLE` — CPIC Level A gene-drug pair, clear guideline
- `CONTESTED` — real literature disagreement, shown rather than resolved
- `NO SIGNAL` — no PGx-actionable interaction found

`CONTESTED` is not a hedge. For DPYD `*9A`/`M166V` in South Asian cohorts,
Hariprakash 2018, Naushad 2021 and Atasilp 2025 give three incompatible answers.
A tool that picks one and reports a number is lying. This one reports the
disagreement.

## Why this gap exists

The money in AI-for-pharma is chasing the molecule — Isomorphic Labs raised
$2.1B in May 2026 for AI-first drug *design*. Very little is chasing the eighteen
months a trial loses waiting for the right patients.

And the mismatch is invisible after the fact: in FAERS adverse-event data,
South Asia reports at roughly **1% of its population-proportional rate**
(representation ratio 0.010, measured over 1,311,022 deduplicated cases). If the
dose is wrong for the population, postmarket surveillance will not tell you.

Meanwhile the requirement is hardening. Japan and China mandate local testing or
foreign-data ethnic-sensitivity analysis; India's waiver of local trials is
[actively contested](https://www.thelancet.com/journals/lansea/article/PIIS2772-3682(24)00151-3/fulltext)
on exactly these grounds. "Does this dose hold in a South Asian cohort" is
becoming a regulatory deliverable, not a nice-to-have.

## Status

Built at **Push to Prod: Building at the Frontier** (Anthropic × Elevation
Capital × Mesa School of Business), Bengaluru, 2026-08-08.

Prototype. Tier 0 engine is the load-bearing part; treat Tier 1/2 as directional.

## Usage

```bash
pip install -e .
cohortfit audit protocols/<protocol>.json --offline
```

`--offline` runs entirely against pinned fixtures — no network. This is the
default for reproducibility, and it means the numbers in a report can be
re-derived exactly.

## Built on

- [`anukriti-pgx-core`](https://github.com/AnukritiAi-hq/anukriti-pgx-core) — the
  deterministic CPIC star-allele/phenotype engine (v0.7.1, 13 genes)
- Anthropic Claude — protocol extraction
- Pinned population frequency data: gnomAD v4.0 (see [docs/DATA_PROVENANCE.md](docs/DATA_PROVENANCE.md))

## Pinned data (Track A — offline by default)

Population allele frequencies live in `fixtures/frequencies/` with mandatory
provenance (rsID, gnomAD alt/total counts, query date). The loader in
`cohortfit.frequencies` rejects entries without source metadata — no hand-written
overrides.

| Fixture | Gene | Populations | Status |
|---|---|---|---|
| [`fixtures/frequencies/dpyd.json`](fixtures/frequencies/dpyd.json) | DPYD | SAS, EUR | pinned 2026-08-08 |

Full audit trail: [docs/DATA_PROVENANCE.md](docs/DATA_PROVENANCE.md)

## Audit orchestrator (Track A — Tier 0)

`cohortfit.audit` wires frequencies → cohort → pgx → rules into an `AuditReport`.
Claude fills `Protocol`; everything after that is pinned arithmetic.

```python
from cohortfit.audit import audit_protocol, load_protocol

report = audit_protocol(load_protocol("protocols/demo.json"), offline=True)
# report.findings[0].verdict → ACTIONABLE (missing DPYD screening)
# report.site_findings → per-site IM+PM burden
```

| Module | Role |
|---|---|
| [`cohortfit.audit`](src/cohortfit/audit.py) | Orchestrator — only module loading fixtures end-to-end |
| [`cohortfit.rules`](src/cohortfit/rules.py) | Drug→gene map, CPIC Level A screening-gap check |
| [`protocols/demo.json`](protocols/demo.json) | Pinned NCT01095003 capecitabine demo (no DPYD exclusion) |

Run integration tests: `pytest tests/test_audit.py tests/test_rules.py`

## Design principle

> The deterministic layer decides. The model explains. Never the reverse.

## License

Apache-2.0
