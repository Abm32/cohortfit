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
                              └─ anukriti-pgx-core ──▶ diplotype → phenotype
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
cohortfit audit protocols/capecitabine_india.json --offline
```

[`protocols/capecitabine_india.json`](protocols/capecitabine_india.json) is a
hand-authored fixture: an adjuvant capecitabine protocol across two Indian
(SAS-ancestry) sites, with no DPYD screening in its exclusion criteria — the
gap this tool is built to catch.

`--offline` runs entirely against pinned fixtures — no network. This is the
default for reproducibility, and it means the numbers in a report can be
re-derived exactly.

## Built on

- [`anukriti-pgx-core`](https://github.com/AnukritiAi-hq/anukriti-pgx-core) — the
  deterministic CPIC star-allele/phenotype engine (v0.7.1, 13 genes)
- Anthropic Claude — protocol extraction
- Pinned population frequency data: gnomAD v2.1.1/v3, IndiGenomes, 1000 Genomes

## Design principle

> The deterministic layer decides. The model explains. Never the reverse.

## License

Apache-2.0
