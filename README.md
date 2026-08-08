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

`CONTESTED` is not a hedge, and it is not decorative. `cohortfit.rules.contested_burden()`
raises it when an allele whose CPIC dose action is disputed carries **≥60%** of a cohort's
actionable burden — the threshold is a judgement call and the code says so. On the demo
cohort (Mumbai 100 + Kochi 50 + Munich 80) that is `HapB3` at **79.3%**, citing
[PMID 37639651](https://pubmed.ncbi.nlm.nih.gov/37639651/): carriers dosed at the standard
25% reduction showed reduced treatment effectiveness and increased toxicity. The finding
sits alongside the `ACTIONABLE` one rather than replacing it, because the two say different
things — the protocol should screen, *and* for most screen-positives here a positive test
has no settled clinical response. The same discipline governs DPYD `*9A`/`M166V` in South
Asian cohorts, where Hariprakash 2018, Naushad 2021 and Atasilp 2025 give three
incompatible answers: a tool that picks one and reports a number is lying.

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

**Pitch & demo:** [docs/PITCH.md](docs/PITCH.md) (four-dot narrative) · [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md) (stage cues)

## Usage

```bash
pip install -e .
cohortfit audit protocols/demo.json
```

`--offline` defaults to **on** — the command runs entirely against pinned fixtures
with no network. That is demo insurance, not a feature flag; venue wifi kills
more demos than bugs do.

```bash
cohortfit audit protocols/demo.json --offline   # explicit, same as default
cohortfit audit protocols/demo.json --no-offline  # rejected (live audit not supported)
cohortfit extract protocols/sources/nct01095003.txt -o /tmp/out.json  # needs ANTHROPIC_API_KEY
cohortfit --help
cohortfit audit --help
cohortfit extract --help
```

**Extraction** (optional, needs network + API key):

```bash
pip install -e ".[llm]"
export ANTHROPIC_API_KEY=...
cohortfit extract protocols/sources/nct01095003.txt -o protocols/extracted.json
cohortfit audit protocols/demo.json   # demo-safe: use hand-verified pinned JSON
```

Show extraction once on stage; run the audit from `protocols/demo.json` for the numbers demo.

Additional hand-authored fixture from parallel work:
[`protocols/capecitabine_india.json`](protocols/capecitabine_india.json) (two SAS sites, no DPYD screening).

Entry point: `cohortfit = cohortfit.cli:app` in `pyproject.toml`.
Renderer: `cohortfit.render` (Rich tables for verdict, cohort phenotype, site burden).

See also: [docs/FINDINGS.md](docs/FINDINGS.md) · [docs/EVIDENCE.md](docs/EVIDENCE.md) · [docs/METHOD.md](docs/METHOD.md) · [AGENTS.md](AGENTS.md)

## What the pinned data says

[docs/FINDINGS.md](docs/FINDINGS.md) derives eight results from the pinned
fixture by leave-one-out allele ablation and sensitivity analysis. Every figure
reproduces from `fixtures/frequencies/dpyd.json` plus pgx-core 0.7.1 — no new
data, no model. The load-bearing ones:

**The South Asian panel is effectively single-allele.** `HapB3` carries **94.2%**
of the CPIC-panel actionable burden in SAS (against 63.9% in EUR); `*13` never
fires at all (pinned SAS frequency 0.0). Effective allele count: **1.12** for
SAS versus 2.10 for EUR.

**That concentration lands on the one allele CPIC contests.** CPIC's guideline
page flags [PMID 37639651](https://pubmed.ncbi.nlm.nih.gov/37639651/): HapB3
carriers dosed at a 25% reduction showed possible *reduced effectiveness* and
increased toxicity. Set HapB3 aside as contested and the number needed to screen
for one confidently actionable finding rises **28 → 487** in SAS, versus 16 → 43
in EUR. The population with the most concentrated risk is concentrated on the
allele with the weakest dosing evidence.

**Screening yield is 1.80× worse in South Asians** (NNS 28.2 vs 15.6). This is a
property of a European-derived panel, *not* evidence of lower risk — so published
European cost-effectiveness results should not be assumed to transfer.

**Poor Metabolizer is a range, not a point estimate.** Across candidate `*2A`
sources the at-risk fraction moves a manageable 1.41×, but PM spans **10.1×**.
At trial scale it is sub-integer anyway: ~5,000 SAS enrollees before one expected
PM, so the Intermediate Metabolizer count is the only plannable quantity.

**Every known bias makes our number too low.** Three floors stack in the same
direction — consanguinity (~2.3× homozygotes), the `*2A` exome undercount (up to
1.41×), and ~8.8% of biochemically DPD-deficient patients carrying no panel
variant at all ([PMID 36918744](https://pubmed.ncbi.nlm.nih.gov/36918744/),
n=712). None push the other way.

> ⚠️ Findings 1–6 and 8 are **our derivations**, reproducible but not externally
> confirmed. Marked as such in the document.

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
# report.findings[1].verdict → CONTESTED (HapB3 at 79.3% of this cohort's burden)
# report.findings[0].notes   → panel coverage note, ancestry caveats
# report.site_findings → per-site IM+PM burden
```

| Module | Role |
|---|---|
| [`cohortfit.audit`](src/cohortfit/audit.py) | Orchestrator — only module loading fixtures end-to-end |
| [`cohortfit.cli`](src/cohortfit/cli.py) | Typer CLI — `cohortfit audit`, `extract`, `render` |
| [`cohortfit.extract`](src/cohortfit/extract.py) | Claude prose → validated `Protocol` JSON |
| [`cohortfit.ancestry`](src/cohortfit/ancestry.py) | Country-default `ancestry_mix` inference |
| [`cohortfit.render`](src/cohortfit/render.py) | Tier-aware Rich report renderer |
| [`cohortfit.reports`](src/cohortfit/reports.py) | AuditReport JSON loader for renderer dev |
| [`cohortfit.sites`](src/cohortfit/sites.py) | Per-site metabolic burden and site-selection ranking |
| [`cohortfit.rules`](src/cohortfit/rules.py) | Drug→gene map, CPIC Level A screening-gap check, contested-burden check |
| [`cohortfit.panel`](src/cohortfit/panel.py) | How many alleles the panel really tests — Herfindahl concentration, leave-one-out burden shares |
| [`cohortfit.sensitivity`](src/cohortfit/sensitivity.py) | Reruns Tier 0 at every disputed frequency the fixture records → per-phenotype bounds |
| [`protocols/demo.json`](protocols/demo.json) | Pinned NCT01095003 capecitabine demo (no DPYD exclusion) |

Run integration tests: `pytest tests/test_audit.py tests/test_rules.py tests/test_panel.py tests/test_sensitivity.py`

## Per-site findings (Track A — site selection)

`cohortfit.sites` reruns Tier 0 math per site — the commercially legible output
for CRO site-selection decisions.

```python
from cohortfit.sites import rank_sites_by_burden, burden_rate_ratio

ranked = rank_sites_by_burden(report.site_findings, gene="DPYD")
# Munich first (~6.4% at-risk rate), then Mumbai/Kochi (~3.5%, same ancestry)
```

| Module | Role |
|---|---|
| [`cohortfit.sites`](src/cohortfit/sites.py) | Per-site burden, ranking, rate-ratio helpers |

**Demo caveat:** Mumbai and Kochi share SAS ancestry — delta is headcount only.
Munich (EUR) diverges on ancestry (~1.8× higher at-risk rate). See
[docs/DATA_PROVENANCE.md](docs/DATA_PROVENANCE.md#per-site-findings-tier-0).

**The ranking is robust.** "Munich above Mumbai" holds at every candidate value
for the disputed SAS `*2A` frequency (1.80× down to 1.004× at the extreme upper
bound) and never inverts. And because EUR `*2A` comes from the same suspect exome
callset, correcting the undercount *symmetrically* widens the gap to **2.75×**
rather than narrowing it — so fixing the provenance strengthens the claim. Full
sensitivity table in [docs/FINDINGS.md](docs/FINDINGS.md) Finding 4.

Run site tests: `pytest tests/test_sites.py`

## CLI (Track B)

**Module:** `cohortfit.cli`  
**Renderer:** `cohortfit.render`  
**Entry point:** `cohortfit = cohortfit.cli:app`  
**Tests:** `tests/test_cli.py`

### Demo command

```bash
pip install -e .
cohortfit audit protocols/demo.json
```

`--offline` defaults to **true** (`--offline/--no-offline`). Live audit is not
implemented; `--no-offline` exits with an error.

### Output sections (what judges see)

1. **Header** — trial title, NCT ID, cohort n, `[offline]` mode
2. **Findings** — tier-labelled panels (see below), verdict colour, CPIC level, citations,
   and the Tier 0 notes: a partial-ancestry caveat when the blend dropped a population,
   then panel concentration — effective allele count, the dominant allele's share of
   actionable burden, and any allele that never fires. One gene can raise more than one
   finding: the demo raises `ACTIONABLE` (no DPYD screening) and then `CONTESTED` (HapB3
   at 79.3% of burden).
3. **Cohort phenotype** — Tier 0 distribution table, printed under the finding that carries
   it, with a `Range (provenance)` column giving each class's bounds and fold-change
4. **Site burden** — Tier 0 IM+PM table, ranked by rate. Every finding renders before it,
   so a second verdict is never stranded below a table.
5. **Data sources** — gnomAD fixture + CPIC diplotype table citations

Poor Metabolizer is printed as a range rather than a point because a point estimate would
overstate the input: on the demo cohort it spans 0.02% – 0.07% (**3.7×**) across the
candidate `*2A` frequencies the fixture records as disputed, against 1.4× for Intermediate
Metabolizer ([docs/FINDINGS.md](docs/FINDINGS.md) Finding 4). The range is provenance
uncertainty, not a prediction interval.

### Tier visual contract (renderer)

| Tier | Badge | Meaning |
|---|---|---|
| **0** | `TIER 0` (cyan) | Arithmetic on pinned tables — fully defensible |
| **1** | `TIER 1` (yellow) | Literature multiplier — **citation required** on every claim |
| **2** | `SCENARIO` (dim) | Directional modelling — **not a prediction** |

Render a pinned report without the audit engine (Tier 0/1/2 styling demo):

```bash
cohortfit render fixtures/reports/sample_audit_report.json
```

Loader: `cohortfit.reports.load_audit_report()`. Tests: `pytest tests/test_render.py`.

## Web UI

Marketing landing at `/` and audit demo at `/app`. See [docs/LANDING.md](docs/LANDING.md) and [docs/UI.md](docs/UI.md).

```powershell
pip install -e ".[web,dev]"
cd web
npm install
npm run dev
```

In a second terminal:

```powershell
cohortfit serve --port 8000
```

Open `http://localhost:5173/` for the landing page and `http://localhost:5173/app` for the
audit viewer. Production build:

```powershell
cd web
npm run build
```

The `/app` viewer loads the pinned sample report by default; **Live audit** runs the offline
engine on `protocols/demo.json`.

## Claude extraction (Track B)

**Module:** `cohortfit.extract`  
**Prompt:** `src/cohortfit/prompts/protocol_extract.txt`  
**Source fixture:** `protocols/sources/nct01095003.txt`  
**Golden output:** `protocols/demo.json` (hand-verified)  
**Tests:** `tests/test_extract.py` (mocked — no API key in CI)

### Boundary

```
protocol prose → Claude → JSON → Protocol.model_validate() → audit engine
```

Claude extracts drugs, criteria, sites, and enrolment only. It must **never**
estimate allele frequencies or phenotypes. Malformed JSON raises `ExtractionError`.

### Ancestry inference

When sites omit `ancestry_mix`, `cohortfit.ancestry.apply_ancestry_defaults()`
fills pinned country priors (e.g. `IN` → SAS, `DE` → EUR). Documented assumption,
not a gnomAD lookup.

### Demo strategy

1. **Once (optional live):** `cohortfit extract protocols/sources/nct01095003.txt -o /tmp/out.json`
2. **Main demo:** `cohortfit audit protocols/demo.json` — pinned hand-verified JSON, offline

Requires `pip install -e ".[llm]"` and `ANTHROPIC_API_KEY` for extract only.

## Design principle

> The deterministic layer decides. The model explains. Never the reverse.

## License

Apache-2.0
