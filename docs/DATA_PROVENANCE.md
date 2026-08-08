# Data provenance — pinned allele frequencies

This document records the **source, version, and assumptions** behind every
population allele frequency shipped in `fixtures/frequencies/`. Judges and
reviewers should treat this as the audit trail for Tier 0 numbers.

## Why fixtures exist

A prior platform shipped a hand-written "27% South Asian DPYD carrier frequency"
that cited real papers but was **never derived from the cited data**. It ran in
production for 52 days. cohortfit's fix is structural: frequencies live in pinned
JSON with mandatory provenance fields; the loader rejects incomplete entries.

Same principle as [`anukriti-pgx-core`](https://pypi.org/project/anukriti-pgx-core/)
pinning CPIC tables to `v2024.01` instead of calling `api.cpicpgx.org` at runtime.

## DPYD — `fixtures/frequencies/dpyd.json`

**Pinned:** 2026-08-08  
**Primary source:** gnomAD v4.0 via [ClinPGx](https://www.clinpgx.org/)  
**Populations:** `SAS` (South Asian), `EUR` (Non-Finnish European)

### Alleles included (CPIC fluoropyrimidine screening panel)

| pgx-core label | rsID | CPIC function | In fixture? |
|---|---|---|---|
| `*1` | — | reference | Yes (computed remainder) |
| `*2A` | rs3918290 | No function | Yes |
| `*13` | rs55886062 | No function | Yes |
| `c.2846A>T` | rs67376798 | Decreased | Yes |
| `HapB3` | rs75017182 (causal) | Decreased | Yes |

### Alleles explicitly excluded from Tier 0

| Label | rsID | Why excluded |
|---|---|---|
| `*9A` / M166V | rs1801265 / rs2297595 | CPIC **Normal function** — not poor-metabolizer drivers. Including them would reproduce the overclaim our DPYD audit caught. Report as `CONTESTED` separately, not in frequency fixtures. |

### Pinned frequencies

| Allele | SAS | EUR | gnomAD v4 evidence |
|---|---:|---:|---|
| `*2A` | 0.000500 | 0.005080 | rs3918290 alt counts in ClinPGx |
| `*13` | 0.000000 | 0.000100 | rs55886062 |
| `c.2846A>T` | 0.000527 | 0.006430 | rs67376798 — [PA166153895](https://www.clinpgx.org/variant/PA166153895) |
| `HapB3` | 0.016870 | 0.020910 | rs75017182 causal variant — [CTS 2024 Table 1](https://doi.org/10.1111/cts.13699) |
| `*1` | 0.982103 | 0.967480 | `1 − sum(variants)` |

### HapB3 label vs frequency rsID

pgx-core's diplotype table keys the decreased-function haplotype as **`HapB3`**
(tag SNP rs56038477 / c.1236G>A). Literature identifies **rs75017182**
(c.1129-5923C>G) as the causal splice variant ([JMolDiag 2024](https://doi.org/10.1016/j.jmoldx.2024.05.015), [CTS 2024](https://doi.org/10.1111/cts.13699)).

The fixture pins **frequency from rs75017182** and documents the label/frequency
rsID split in each `HapB3` record's `notes` field.

### Literature cross-checks (secondary, not primary)

| Paper | Use |
|---|---|
| Atasilp 2025 — [doi:10.1016/j.clinme.2025.100443](https://doi.org/10.1016/j.clinme.2025.100443) | Indian/SAS *2A 0.05%, HapB3 tag 1.4%, *13 absent |
| JMolDiag 2024 — [doi:10.1016/j.jmoldx.2024.05.015](https://doi.org/10.1016/j.jmoldx.2024.05.015) | Population-specific CPIC variant frequencies |
| Hariprakash 2018 — [doi:10.2217/pgs-2017-0101](https://doi.org/10.2217/pgs-2017-0101) | SAS landscape; CONTESTED context only |
| Naushad 2021 — [doi:10.1002/jgm.3289](https://doi.org/10.1002/jgm.3289) | Indian GSA; do **not** use C29R 24.91% (CPIC Normal) |

### Assumptions (stated, not hidden)

1. **Hardy-Weinberg equilibrium** for diplotype expansion.
2. **Independence** among low-frequency CPIC-panel alleles (no LD correction).
3. **Single gnomAD version** (v4.0) — no mixing v2/v3/v4 rows.
4. **Population codes** `SAS` / `EUR` match `Site.ancestry_mix` keys in protocol JSON.

### Pre-computed Tier 0 ground truth (n = 1000)

Computed via HWE + `DPYD_diplotypes_anukriti_v2024.01.json` (pgx-core 0.7.1):

| Population | Normal | Intermediate | Poor | At-risk (IM+PM) |
|---|---:|---:|---:|---:|
| SAS | 964.5 | 35.4 | 0.04 | **3.55%** |
| EUR | 936.0 | 63.4 | 0.62 | **6.40%** |

**Honest direction:** For the CPIC-panel allele set, **EUR > SAS** at-risk burden.
Demo narrative should lead with missing DPYD screening and non-zero Indian-site
enrollee counts — not a reversed SAS/EUR ratio unless CONTESTED variants are added
(Tier 1+, never Tier 0 without citation).

### CPIC guideline citation

Fluoropyrimidine / DPYD screening: PMID [29152729](https://pubmed.ncbi.nlm.nih.gov/29152729/)

## Phenotype mapping (Tier 0)

**Module:** `cohortfit.pgx`  
**Source table:** `DPYD_diplotypes_anukriti_v2024.01.json` shipped inside
[`anukriti-pgx-core==0.7.1`](https://pypi.org/project/anukriti-pgx-core/)  
**CPIC citation:** `_source` field — *CPIC Guideline for Fluoropyrimidines and DPYD (2017, 2024 update)*  
**PMID:** [29152729](https://pubmed.ncbi.nlm.nih.gov/29152729/)

### How lookup works

1. Hardy-Weinberg produces sorted diplotype tuples: `("*1", "*2A")`.
2. `lookup_phenotype()` tries slash keys `"*1/*2A"` and `"*2A/*1"` against the pinned table.
3. Unmapped diplotypes → `"Indeterminate"` (never dropped — see `test_cohort.py`).

**Production path does not use `PhenotypeEngine`.** The cohort path already has
star alleles from statistics; reading the named-diplotype JSON directly is fewer
moving parts and surfaces the table `_source` as an audit citation.

A parity test in `tests/test_pgx.py` asserts adapter output matches
`PhenotypeEngine.infer()` for every table row — regression guard on pgx-core pin
upgrades only.

### CPIC panel coverage

For the five alleles in `fixtures/frequencies/dpyd.json`, all 15 HWE diplotypes
map to Normal / Intermediate / Poor Metabolizer — zero Indeterminate under the
current panel. Indeterminate appears only if the allele panel grows beyond the
table (e.g. adding `*9A`, which is CPIC Normal and excluded from Tier 0).

## Updating frequencies

1. Query gnomAD v4 via ClinPGx for all four rsIDs × both populations.
2. Record alt_observed, total_alleles, query_date.
3. Recompute `*1` remainder; assert sum = 1.0.
4. Re-run HWE + pgx-core; update `_ground_truth` in the fixture.
5. Run `pytest tests/test_frequencies.py`.
6. Update this document in the same commit.

Never edit frequencies in place without updating provenance counts and ground truth.

## Audit pipeline (Tier 0)

**Module:** `cohortfit.audit`  
**Entry points:** `load_protocol(path)`, `audit_protocol(protocol, offline=True)`  
**Demo fixture:** `protocols/demo.json` (NCT01095003, capecitabine, Mumbai/Kochi/Munich)

### Pipeline steps (deterministic, no LLM)

1. **Drug → gene** — `cohortfit.rules.resolve_gene()` maps fluoropyrimidines to `DPYD`.
2. **Allele frequencies** — `cohortfit.frequencies.load_gene_frequencies()` loads pinned gnomAD fixtures.
3. **Ancestry blend** — `cohortfit.cohort.blend_allele_frequencies()` weights by site `ancestry_mix`.
4. **Hardy–Weinberg + phenotype** — `cohortfit.pgx.cohort_phenotype_distribution()` expands diplotypes and maps via CPIC table.
5. **Screening gap** — `cohortfit.rules.screening_gap()` flags CPIC Level A pairs with no DPYD/DPD exclusion in protocol text.
6. **Per-site burden** — `SiteFinding` records IM+PM fraction and expected count per site.

### Screening-gap rule scope

| Check | Detail |
|---|---|
| Gene-drug | Fluoropyrimidines → DPYD only (`capecitabine`, `fluorouracil`, `5-FU` aliases) |
| CPIC level | Level A required (`level_for` from pgx-core) |
| Protocol text | Inclusion + exclusion criteria scanned for `dpyd`, `dpd`, genotype/testing terms |
| Citation | PMID [29152729](https://pubmed.ncbi.nlm.nih.gov/29152729/) when actionable |

Unsupported drugs or gene mismatches return `NO_SIGNAL` — the demo path does not generalise to all CPIC pairs.

### Demo protocol ground truth (`protocols/demo.json`)

| Site | Ancestry | planned_n | At-risk (IM+PM) |
|---|---|---:|---:|
| Mumbai | SAS 100% | 100 | ~3.55% |
| Kochi | SAS 100% | 50 | ~3.55% |
| Munich | EUR 100% | 80 | ~6.40% |
| Cohort (weighted) | 150/230 SAS + 80/230 EUR | 230 | ~4.5% |

**Verdict on demo:** `ACTIONABLE` — capecitabine + DPYD Level A, no DPYD/DPD exclusion in criteria.

Integration tests in `tests/test_audit.py` pin these numbers against the orchestrator output.

## Per-site findings (Tier 0)

**Module:** `cohortfit.sites`  
**Output:** `SiteFinding(site_name, gene, at_risk_fraction, expected_at_risk_n)`  
**Tests:** `tests/test_sites.py`

### Two numbers, two stories

| Field | Driven by | Demo meaning |
|---|---|---|
| `at_risk_fraction` | Site `ancestry_mix` only | Munich ~6.40% vs Mumbai/Kochi ~3.55% — ancestry delta |
| `expected_at_risk_n` | Rate × `planned_n` | Mumbai ~3.55 vs Kochi ~1.77 — same rate, 2× headcount |

Mumbai and Kochi are both `{"SAS": 1.0}`, so their **rates are identical**; the
only difference is enrolment volume (`planned_n` 100 vs 50). Munich (`{"EUR": 1.0}`)
shows a **~1.8× higher at-risk rate** before headcount is considered.

Say this in the demo — do not let a judge discover the SAS-site sameness unaided.

### Pinned per-site ground truth (DPYD, demo protocol)

| Site | Ancestry | planned_n | at_risk_fraction | expected_at_risk_n |
|---|---|---:|---:|---:|
| Mumbai | SAS 100% | 100 | 0.035474 | 3.55 |
| Kochi | SAS 100% | 50 | 0.035474 | 1.77 |
| Munich | EUR 100% | 80 | 0.063982 | 5.12 |

Helpers: `rank_sites_by_burden()`, `burden_rate_ratio()` — for CLI site-selection table (Track B).

## CLI (Track B)

**Command:** `cohortfit audit protocols/demo.json`  
**Default:** `--offline` (pinned fixtures, no network)  
**Renderer:** Rich stdout via `cohortfit.render.render_audit_report()`

The CLI wires `load_protocol` → `audit_protocol(offline=True)` → Rich output.
No LLM, no live gnomAD fetch. Reproducible demo for judges: same command, same numbers.
