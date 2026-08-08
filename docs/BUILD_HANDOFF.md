# cohortfit — Build Handoff

> Written 2026-08-08 during **Push to Prod: Building at the Frontier** (Anthropic ×
> Elevation Capital × Mesa School of Business), Bengaluru.
> **Hacking started 11:30. Submission due 16:30 IST.**
>
> This document is self-contained: an agent picking it up should be able to
> continue the build without re-deriving anything. Every number below was
> verified from source files or live pages, not recalled.

---

## 1. What we are building

**Every trial protocol has an implicit genome it was written for. Nobody checks
whether the patients being enrolled actually have it.**

`cohortfit` reads a clinical trial protocol and computes the pharmacogenomic
phenotype distribution of the cohort that protocol will *actually* recruit, given
the ancestry mix of its planned sites.

### The problem in plain terms

DPYD is a gene whose enzyme clears fluoropyrimidine chemotherapy (capecitabine,
5-FU). Broken copies → the drug accumulates → severe, sometimes fatal toxicity.
CPIC guideline says screen DPYD before prescribing. How often broken copies occur
**depends on ancestry**.

A protocol says "capecitabine 1250 mg/m² twice daily." That dose was calibrated
on largely European populations. Run the same protocol at Indian sites and a
*computable* fraction of enrollees cannot metabolise it safely — computable
because the allele frequencies are published.

Consequences: adverse events, dropouts, muddied safety signal, protocol
amendments, trial delay or failure. A failed Phase III costs $100M–$1B.

It is also invisible after the fact: in FAERS, **South Asia reports adverse
events at ~1% of its population-proportional rate** (representation ratio 0.010,
measured over 1,311,022 deduplicated cases). If a dose is wrong for a population,
postmarket surveillance will not surface it.

### The solution, three steps

1. **Claude extracts** — protocol prose/PDF → structured `Protocol` (drugs, dose,
   inclusion/exclusion criteria, sites, target N). Nothing else.
2. **Deterministic math adjudicates** — site ancestry mix → pinned allele
   frequencies → Hardy-Weinberg → diplotype frequencies → CPIC phenotype tables →
   expected cohort phenotype distribution.
3. **Guideline gap check** — CPIC says screen DPYD; this protocol's exclusion
   criteria do not mention it → `ACTIONABLE`, with the expected number of at-risk
   patients about to be enrolled unscreened.

### The one structural idea

> **The model converts unstructured text into typed claims. Deterministic code
> does everything after that.**

Claude must never compute a frequency, phenotype, or verdict. `models.py`
encodes this as types (extraction side vs verdict side) so it is enforceable
rather than aspirational.

---

## 2. Why this wins in this specific room

Judges: 4 Anthropic staff (GTM, Applied AI Architect, Solutions Architect,
Startup Partnerships APAC) + Elevation Capital's AI Operations Partner.
Needs real technical substance **and** a scale story.

Theme is "Build the Next Audacious" with 5 framings. We target **#1 frontier
capability** and **#5 infrastructure everyone else builds on**.

**The four dots, in pitch order:**

1. **Anthropic said what it wants out loud.** On 2026-07-28 Anthropic signed a
   multi-year deal with ICON plc (CRO, 40,200 staff, 99 locations). Their
   Ireland/UK head Pip White: *"Far too often, the barrier to getting medicines to
   patients faster is operational, not scientific."* Enrolment delays hold up
   **up to 80% of trials**. ICON's four capabilities: site intelligence, study
   planning/feasibility, predictive enrolment risk, protocol design.
2. **DeepMind is going the other way with $2.1B.** Isomorphic Labs raised a $2.1B
   Series B (May 2026) chasing *the molecule*; first AI-designed drugs enter
   trials end-2026 (slipped from 2025). Anthropic paid $400M for Coefficient Bio
   and hired John Jumper away from DeepMind — then pointed its first big pharma
   deal at operations. **The molecule lane is funded and closed. The trial-ops
   lane is where Anthropic is actually placing money.**
3. **India is the regulatory pressure point.** Japan and China mandate local
   testing or foreign-data ethnic-sensitivity analysis. India's waiver of local
   trials is contested on exactly these grounds (Lancet SEA). "Does this dose hold
   in a South Asian cohort" is becoming a **filing**, i.e. a recurring compliance
   budget line.
4. **We already own the hard part.** `anukriti-pgx-core` 0.7.1: 13 genes, 22
   pinned CPIC tables, zero runtime deps. Plus audited SAS/EUR frequency data and
   80,679 FAERS real-world signals.

**Closing line:** *Isomorphic raised $2.1B to design the molecule. Anthropic's own
partner says 80% of trials are held up by operations, not science. We built the
layer that tells you whether the population you're enrolling can metabolise the
molecule you already have.*

---

## 3. Repo state as of 12:05

**GitHub:** https://github.com/Abm32/cohortfit (public, Apache-2.0)
**Local:** `/home/abhimanyu/Desktop/SynthaTrial-repo/cohortfit`
Created under `Abm32` because `AnukritiAi-hq` is not accessible with the current
token scopes (`gist, read:org, repo, workflow`). Transfer to the org later.

```
78f9787  feat(protocol): hand-author capecitabine/India fixture, add AGENTS.md   <-- UNPUSHED
dabc4fa  feat(cohort): Tier 0 Hardy-Weinberg cohort engine
84229e5  feat(models): define the extraction/adjudication boundary
94dd3a3  chore: scaffold packaging against pinned pgx-core 0.7.1
2deace9  docs: state the problem cohortfit exists to solve
```

**`78f9787` is one commit ahead of `origin/main` — push it.**

### Exists and verified working
- `README.md`, `LICENSE` (Apache-2.0), `AGENTS.md`, `.gitignore`, `pyproject.toml`
- `src/cohortfit/models.py` — `Protocol`/`Site`/`DoseRegimen` (extraction side);
  `AuditReport`/`GeneDrugFinding`/`SiteFinding`/`PhenotypeCount`/`Verdict`/`Tier`
  (verdict side)
- `src/cohortfit/cohort.py` — Tier 0 engine: `diplotype_frequencies`,
  `cohort_ancestry_mix`, `blend_allele_frequencies`, `phenotype_distribution`
- `tests/test_cohort.py` — **18 tests, all passing** (`.venv/bin/python -m pytest tests/ -q`)
- `protocols/capecitabine_india.json` — pinned fixture, 2 Indian sites
  (Kerala n=100, Chennai n=50), target_n=150, `ancestry_mix: {"SAS": 1.0}`

### Does not exist yet
`cli.py` (declared in `pyproject.toml` as `cohortfit.cli:app` — **entry point is
currently broken**), frequency fixtures, phenotype adapter, screening-gap rule,
audit orchestrator, per-site findings, Claude extractor.

---

## 4. Verified technical facts (do not re-derive)

### pgx-core is on PyPI
`anukriti-pgx-core` available: 0.7.1, 0.7.0, 0.6.0, 0.5.0, 0.4.1, 0.4.0, 0.3.0,
0.2.1, 0.2.0. The `==0.7.1` pin resolves fine. (An earlier `--no-deps` install in
the local venv was unnecessary.)

### Use the pinned table, not `PhenotypeEngine`
pgx-core's `__all__` exports `PhenotypeEngine`, gene callers,
`ingest_sv_diplotype`, `normalize_diplotype`, `phenotype_from_activity_score` —
**there is no public diplotype→phenotype function.**

`PhenotypeEngine` is built for the VCF path (variants in → diplotype → phenotype).
We already *have* diplotypes; we synthesised them statistically. Using the engine
would mean fabricating `VCFVariant` objects to get back a diplotype we already
know.

**Read the table directly:**
`anukriti-pgx-core/anukriti_pgx_core/phenotype/tables/DPYD_diplotypes_anukriti_v2024.01.json`
is a flat map, which is exactly the shape `phenotype_distribution()` expects:

```json
{
  "_source": "CPIC Guideline for Fluoropyrimidines and DPYD (2017, 2024 update)",
  "_version": "2024-01",
  "*1/*1": "Normal Metabolizer",
  "*1/*2A": "Intermediate Metabolizer",
  "*1/*13": "...", "*1/c.2846A>T": "...", "*1/HapB3": "...",
  "*2A/*2A": "...", "*2A/*13": "...", "*2A/c.2846A>T": "..."
}
```

`_source` goes straight into the report as a citation.

### Key format mismatch — real gotcha
`diplotype_frequencies()` emits **sorted tuples** `("*1", "*2A")`.
Table keys are **slash-joined strings** `"*1/*2A"`.
CPIC ordering ≠ lexicographic sort order. The adapter must try `f"{a}/{b}"`,
then `f"{b}/{a}"`, then fall back to `"Indeterminate"`.

### Citation for the screening-gap rule
`DPYD_CLINICAL_ACTIONS_v2024.01.json` carries `_guideline_pmid: "29152729"`
(also `_source`: CPIC Fluoropyrimidines/DPYD 2017 + Nov 2018 update,
`_snapshot_date: 2026-06-13`).

### 22 pinned tables available
DPYD, CYP2C9, CYP2C19 (+PPI clinical actions), CYP2D6, CYP1A2, CYP2B6, CYP3A4,
CYP3A5, G6PD, NAT2, TPMT, SLCO1B1, VKORC1, plus `CPIC_RECOMMENDATION_LEVELS_v2024.01.json`
and `CPIC_PROVENANCE.json`.

### ⚠️ Do NOT build the rule around `*9A` / `M166V`
**CPIC classifies both as Normal function.** They do not cause poor metabolism.
The alleles that drive the ACTIONABLE finding are **`*2A`, `*13`, `c.2846A>T`,
HapB3** — all present in the pinned diplotype table.

Building on `*9A` would reproduce the exact overclaim our own audit caught
(see §7) and destroy the credibility story mid-demo.

### Ground-truth frequencies (live-queried gnomAD v2.1.1, 2026-07-28)
For testing the blend/HWE path — these are the *audited* numbers:

| Allele | SAS | EUR | Note |
|---|---|---|---|
| DPYD `*9A` | 0.2550 | 0.2226 | ratio 1.15, **not** SAS-enriched; AFR 0.4131 is the population max |
| DPYD `M166V` | 0.0906 | 0.1004 | **SAS below EUR** — direction inverted |

Both Normal function. Useful as regression fixtures proving the tool does not
overclaim; **not** the alleles for the ACTIONABLE finding.

---

## 5. Remaining build, split 2 ways

**Track A owns every number. Track B owns everything a judge sees.**

| # | Component | Track | Est |
|---|---|---|---|
| 1 | **Frequency fixtures** — SAS/EUR for DPYD `*2A`/`*13`/`c.2846A>T`/HapB3 + `*1` remainder, with provenance fields | A | 30m |
| 2 | **Phenotype adapter** — load pinned DPYD table, handle `a/b` vs `b/a` | A | 30m |
| 3 | **Screening-gap rule** — CPIC says screen, protocol doesn't → `ACTIONABLE`, cite PMID 29152729 | A | 30m |
| 4 | **Audit orchestrator** — `Protocol` + fixtures → `AuditReport` | A | 40m |
| 5 | **Per-site findings** — `SiteFinding` per site, site-selection delta | A | 20m |
| 6 | **`cli.py`** — Typer, `audit <protocol> --offline` | B | 40m |
| 7 | **Report renderer** — rich tables, **tier labels visibly distinct** | B | 50m |
| 8 | **Claude extractor** — prose → `Protocol`, fixture fallback | B | 40m |
| 9 | **Pitch script** — four dots above, rehearsed | B | 40m |
| 10 | **Devfolio submission** — writeup, repo link, screenshots | B | 20m |

### The single sync point
`AuditReport` is **already defined** in `models.py`. Track A's first action is to
emit one fake-but-schema-valid `AuditReport` JSON and hand it to Track B. That one
file unblocks items 6, 7, 9, 10. Final integration is a one-line swap.

Track B must **never** wait for real numbers.

### Why this build order (not extractor-first)
- The extractor is the part most likely to work; the engine is the part most
  likely to break. Build the risky thing first.
- The pinned fixture is *how you test the extractor* — hand-verified expected
  output to diff against. Extractor-first means validating one unverified
  component with another.
- The extractor is a live API call. If it is on the critical path at 16:25 and
  wifi drops, there is no demo. Show it working once early, then run offline.
- It is not the moat. Every team can wire Claude to a PDF. Nobody else has
  pgx-core with 22 pinned CPIC tables and audited SAS frequency data.

---

## 6. Component reference

### Track A

**1. Frequency fixtures** — JSON: `population → allele → frequency`, input to
`blend_allele_frequencies()`. **Must include a `*1` reference allele carrying the
remainder so frequencies sum to 1.0** — Hardy-Weinberg is only valid over a
complete allele space; omit the wildtype and every downstream diplotype frequency
is wrong by a constant factor. Each record carries source, population, sample
count, query date. Pinned rather than API-called for the same reason pgx-core
pins CPIC tables: reproducibility requires inputs that cannot move.

**2. Phenotype adapter** — builds the
`phenotype_of: dict[tuple[str,str], str]` argument that
`phenotype_distribution()` takes. Unmapped diplotypes → `"Indeterminate"`, never
dropped: dropping silently renormalises the rest and inflates apparent
confidence, producing a distribution that sums to 1.0 while being wrong. Already
tested.

**3. Screening-gap rule** — resolve drug → PGx-actionable gene, check whether any
criterion references genotype screening, emit
`GeneDrugFinding(verdict=ACTIONABLE, missing_exclusion=...)`. Hardcoded for one
gene-drug pair on purpose; generalising to a rules engine at hour two is how you
reach 16:30 with a framework and no findings. Scaling story: one rule per CPIC
Level A pair, of which there are dozens. Detection is string matching over
criteria text — fragile in general, fine here because the protocol is pinned.
**Comment that honestly rather than implying generality.**

**4. Audit orchestrator** — the only module that knows the full pipeline.
Everything else stays a pure function over explicit inputs, which is why
`cohort.py` has 18 tests and no mocks. If `cohort.py` starts loading files, the
Tier 0 defensibility claim is gone. This is also the enforcement point for
"nothing above this line is an LLM."

**5. Per-site findings** — same math per `Site` instead of pooled. Most
commercially legible output (site selection is a real CRO decision) but just a
loop over existing machinery, hence last. **Caveat to state aloud in the demo:**
both fixture sites are `{"SAS": 1.0}`, so deltas are driven only by `planned_n`
(100 vs 50). Say "add a European site and it diverges" before a judge notices.

### Track B

**6. `cli.py`** — `pyproject.toml` already declares the entry point and the module
is missing, so `pip install -e .` currently yields a broken script. `--offline`
defaults true: demo insurance, not a feature flag.

**7. Report renderer** — **tier labels are not decoration.** If Tier 0/1/2 print
in identical styling, the contract collapses exactly where it matters: the reader
can no longer distinguish a defensible number from a modelled one. The type
system carries `Tier`; the renderer must *show* it.

**8. Claude extractor** — prose → strict JSON →
`Protocol.model_validate_json()`. Pydantic validation is the boundary: malformed
output raises instead of propagating garbage into the math. Mandatory (Claude is
a hackathon requirement, and without it this is a calculator that reads JSON) but
demonstrated once early, then bypassed for the offline run.

---

## 7. Output contract — tiers and verdicts

| Tier | Claim | Basis |
|---|---|---|
| **0** `DISTRIBUTION` | Expected cohort phenotype distribution | Arithmetic on pinned tables. Defensible without qualification. |
| **1** `BURDEN` | Expected excess toxicity | Needs a literature multiplier. **Must carry a citation.** |
| **2** `SCENARIO` | Trial-outcome impact | Labelled scenario. **Never** a prediction. |

| Verdict | Meaning |
|---|---|
| `ACTIONABLE` | CPIC Level A pair, clear guideline |
| `CONTESTED` | Genuine literature disagreement, shown not resolved |
| `NO_SIGNAL` | No PGx-actionable interaction found |

**`CONTESTED` is a real answer, not a hedge.** For DPYD `*9A`/`M166V` in South
Asian cohorts: Hariprakash 2018 found an M166V→hand-foot-syndrome association
(OR 5.22, n=110) but its `*9A` assay failed; Naushad 2021 found no association
for either (n=2000 healthy Indians); Atasilp 2025 reported `*9A`→neutropenia on
n=2 homozygotes, not surviving multivariate. A tool that picks one and prints a
number is lying.

### Why this discipline exists — the 52-day incident
`anukriti-swarm` shipped `U4_SAS_DPYD_OVERRIDE` on 2026-06-06, blocking clinical
synthesis for South Asian patients on a *"27% carrier frequency"* claim citing
Hariprakash 2018. The paper is real. **The frequency was hand-written** — the
pinned `gnomad_v2_1_1_frequencies.jsonl` had no rows for either allele. Real
gnomAD inverts the direction for `M166V`. It ran live, unchallenged, for 52 days
until a manual audit
(`anukriti_docs/DPYD_SAS_OVERRIDE_AUDIT_2026-07-28.md`) caught it.

This is the failure class the whole design prevents: **confident numbers with no
traceable source.** In a room of Anthropic engineers, calibrated refusal reads as
engineering maturity.

---

## 8. Non-negotiables

1. **`--offline` is the default.** Pin every external response to fixtures. Venue
   wifi kills more demos than bugs do.
2. **Claude never produces a number.** Extraction only.
3. **Tier labels visible on every claim.**
4. **Do not build the rule on `*9A`/`M166V`** (Normal function — see §4).
5. **Commit convention:** Conventional Commits, imperative subject, body explains
   *why* with concrete bullets, **no trailers** (no `Co-authored-by`).
6. **Do not commit into `SynthaTrial-repo/.git`** — vestigial original monorepo,
   no remote, 521 phantom deletions. `git add -A` there produces a mess.
7. **Leave the three dirty platform repos alone today** — `anukriti-swarm` (DPYD
   safety-behaviour correction), `project_astra` (FAERS gap scoring),
   `anukriti_docs` (the audit doc). Committing a safety change under time
   pressure is how something that matters breaks.

---

## 9. Checkpoints

| Time | Gate |
|---|---|
| **13:30** | A: real phenotype numbers printing (ugly is fine). B: renderer working on fake data. |
| **14:30** | Swap fake → real. **Demo works end-to-end from here.** Everything after is polish. |
| **15:00** | B locks the extractor, stops touching code, rehearses. |
| **15:45** | Code freeze. Submission written. Rehearse twice. |
| **16:15** | **Submit.** Not 16:29. |

### Cut order if behind
CYP2C9 (DPYD alone carries the demo) → per-site deltas → Tier 1 burden →
extractor becomes "shown working once, then offline."

**Never cut:** the Tier 0 distribution, the screening-gap finding, the tier
labels. Those three *are* the product.

---

## 10. Immediate next actions

1. `git push` — `78f9787` is unpushed.
2. Emit a fake schema-valid `AuditReport` JSON → hand to Track B. **Unblocks most
   of his track.**
3. Track A item 1: frequency fixtures for DPYD `*2A`/`*13`/`c.2846A>T`/HapB3 + `*1`.
4. Track A item 2: phenotype adapter reading the pinned table (mind the `a/b` vs
   `b/a` key order).

---

## Appendix — verified sources

- Devfolio: https://pushtoprod-india.devfolio.co/ — theme, 5 framings, Claude
  requirement, judges, 1–3 team, $10K, schedule (11:30 start / 16:30 submission)
- ICON × Anthropic, 2026-07-28: https://thenextweb.com/news/icon-anthropic-claude-clinical-trials-enrolment-bottleneck
  — "operational, not scientific"; up to 80% of trials delayed by enrolment;
  40,200 staff; $400M Coefficient Bio; John Jumper hire
- Isomorphic Labs $2.1B Series B (May 2026), first AI-designed drugs to trials
  end-2026
- Lancet SEA on India local-trial waivers: https://www.thelancet.com/journals/lansea/article/PIIS2772-3682(24)00151-3/fulltext
  — Japan/China ethnic-sensitivity mandates
- `anukriti_docs/DPYD_SAS_OVERRIDE_AUDIT_2026-07-28.md` — the 52-day incident,
  real gnomAD frequencies, three-way literature contradiction, 3 unfixed pgx-core
  DPYD table errors
- `project_astra/docs/19-faers-real-world-corroboration-2026-07-25.md` — 80,679
  signals / 1,311,022 cases; SAS representation ratio 0.010
- `/home/abhimanyu/Desktop/SynthaTrial-repo/.anukriti-context-refresh-2026-08-08.md`
  — full cross-repo platform context
