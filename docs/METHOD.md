# Method: from published allele frequencies to a cohort phenotype distribution

> Why the Tier 0 numbers are what they are, what they assume, and where they
> stop being trustworthy. If you only read one section, read
> [Limits and honest caveats](#limits-and-honest-caveats) — that is the part a
> reviewer will press on.

Implemented in [`src/cohortfit/cohort.py`](../src/cohortfit/cohort.py), with the
sensitivity range in
[`sensitivity.py`](../src/cohortfit/sensitivity.py) and the panel coverage
measures in [`panel.py`](../src/cohortfit/panel.py).

---

## The gap this bridges

Published population data gives **allele frequencies** — how common a variant is
among all gene copies in a population. For example, DPYD `*2A` at ~1% in a given
population means 1 in 100 *copies* carries it.

But drug toxicity does not depend on a single copy. Everyone inherits **two**
copies of DPYD, one from each parent, and what matters clinically is the **pair**:

- two working copies → Normal Metabolizer → standard dose
- one working, one broken → Intermediate Metabolizer → CPIC advises dose reduction
- two broken copies → Poor Metabolizer → severe, potentially fatal toxicity

CPIC's pinned tables are keyed on pairs — `"*1/*1"`, `"*1/*2A"`, `"*2A/*2A"` — not
on single alleles. So there is a gap between the shape of the published data
(single-allele frequencies) and the shape of the clinical lookup (pairs).

**Hardy-Weinberg is that bridge.**

---

## Hardy-Weinberg equilibrium

If an allele has frequency `p` and another has frequency `q`, then under random
mating the expected frequency of each pair is:

| Pair | Expected frequency | Why |
|---|---|---|
| both copies allele A | `p²` | one way to happen: A from each parent |
| one A, one B | `2pq` | **two** ways: A from mother + B from father, *or* the reverse |
| both copies allele B | `q²` | one way to happen: B from each parent |

These sum to `(p + q)² = 1.0`. That identity is the correctness check, and it is
asserted in the test suite.

### The factor of 2 is the whole point

The `2` in `2pq` is not a fudge factor. There are two distinct inheritance paths
to a heterozygote and only one path to each homozygote. Drop it and the
frequencies no longer sum to 1, which is exactly the bug the sum-to-one test
catches.

It is also why heterozygotes dominate for rare variants. Worked example with
DPYD `*2A` at `q = 0.01` and `*1` at `p = 0.99`:

```
*1/*1    = 0.99 × 0.99          = 0.9801   → 98.01 %
*1/*2A   = 2 × 0.99 × 0.01      = 0.0198   →  1.98 %
*2A/*2A  = 0.01 × 0.01          = 0.0001   →  0.01 %
                                  ------
                                  1.0000
```

**Read what that means for a 150-patient trial:**

- Poor Metabolizers: `0.0001 × 150` = **0.015 patients** — statistically less
  than one person
- Intermediate Metabolizers: `0.0198 × 150` = **~3 patients**

So the clinically actionable burden sits in the **intermediate** tier, not in the
rare homozygotes. A protocol with no DPYD screening is not primarily risking the
one-in-ten-thousand case; it is risking the handful of intermediate metabolizers
who will receive a full dose their enzyme cannot clear. That is the finding worth
reporting, and it is why the report must show the whole distribution rather than
only the worst class.

### Generalising past two alleles

Real genes have more than two relevant alleles. DPYD needs `*2A`, `*13`,
`c.2846A>T` and HapB3, plus a `*1` reference allele. The rule extends directly:
for every unordered pair of alleles *i*, *j*,

```
freq(i, j) = p_i²          if i == j
freq(i, j) = 2 · p_i · p_j if i != j
```

`diplotype_frequencies()` implements this with
`itertools.combinations_with_replacement` over the sorted allele labels, which
enumerates each unordered pair exactly once. Keying on **sorted tuples** is what
prevents counting `("*1","*2A")` and `("*2A","*1")` as separate outcomes — a
double-counting bug that would silently inflate every heterozygote class.

### The reference allele is mandatory

Hardy-Weinberg is only valid over a **complete** allele space — the input
frequencies must sum to 1.0. This means the `*1` (wildtype / reference) allele
must be present, carrying the remainder:

```
p(*1) = 1 − Σ p(variant alleles)
```

Omit it and every resulting diplotype frequency is wrong by a constant factor,
while still looking superficially plausible. This is a silent failure, which is
why it is called out here rather than left to the reader.

---

## The full Tier 0 pipeline

Six steps, all pure arithmetic, no network, no model. Steps 1–4 produce the
distribution; steps 5 and 6 say how much to trust it and what the panel behind
it actually covers.

### 1. `cohort_ancestry_mix(sites)` — who will actually enrol

Each site declares an expected ancestry mix. Collapse them into one
enrolment-weighted mix, **weighted by `planned_n`** so a large site dominates
expected composition as it should:

```
mix[pop] = Σ_sites (site.ancestry_mix[pop] × site.planned_n) / Σ_sites site.planned_n
```

Returns `{}` when total planned enrolment is zero rather than dividing by zero.

### 2. `blend_allele_frequencies(per_population, ancestry_mix)` — the cohort's allele pool

Blend population-specific frequencies by the ancestry weights.

**Populations with no pinned data are skipped and the remaining weights
renormalised.** If a cohort is 50% SAS / 50% AFR and only SAS frequencies are
pinned, the result is the SAS frequencies at full weight — an explicit partial
answer — rather than frequencies summing to 0.5, which would understate every
variant by half and still look like a valid distribution. Tested.

**That omission is reported, not left implicit.** Renormalising produces a
distribution that still sums to 1.0, so a partially-covered cohort would
otherwise be indistinguishable from a fully-covered one. A US cohort declared
68% EUR / 13% AFR / 19% AMR returns *exactly* the EUR-only numbers. Each finding
therefore carries a `PopulationCoverage` record (covered and dropped weights),
the finding gets an explanatory note, and the report emits a coverage warning
naming the dropped populations and the discarded enrolment fraction. This is the
population-level counterpart to the `Indeterminate` phenotype bucket below.

### 3. `diplotype_frequencies(allele_freqs)` — Hardy-Weinberg expansion

As above. Output sums to 1.0.

### 4. `phenotype_distribution(diplotype_freqs, phenotype_of, planned_n)` — CPIC lookup

Aggregate diplotype frequencies into phenotype classes using the pinned CPIC
table, then scale by cohort size to get expected patient counts.

**Unmapped diplotypes aggregate to `"Indeterminate"`, never dropped.** Dropping
them would silently renormalise the remainder: the distribution would still sum
to 1.0 and look correct while overstating confidence in every other class. An
`Indeterminate` bucket makes coverage gaps visible in the output instead of
hiding them. Tested.

### 5. `phenotype_bounds(...)` — the same pipeline rerun per candidate frequency

Some pinned frequencies are disputed. The SAS `*2A` value (0.0005, gnomAD v4
exomes) is contradicted by every genome-based source, all of them upward, and
the fixture records that disagreement in `_meta.known_discrepancies` rather than
quietly picking a winner. `phenotype_bounds()` reruns steps 2–4 once per
unresolved candidate value and returns `phenotype → (min, max)` fraction.
`substitute_allele()` swaps one frequency and re-derives `*1` as the remainder
so the allele space still sums to 1.0, and raises rather than feeding a negative
reference frequency into Hardy-Weinberg. A phenotype absent from one scenario
counts as 0.0 there.

Each `PhenotypeCount` then carries `fraction_low` / `fraction_high`, and the
distribution table grows a "Range (provenance)" column stating the fold-change.
**Poor Metabolizer is not reported as a point estimate**: across the candidate
`*2A` values it spans 35.7 to 765.0 per million — 21.4× — while the at-risk
fraction moves 1.80× ([FINDINGS.md](FINDINGS.md) Finding 4). A reader comparing
those two numbers needs to see which of them the pinned data supports.

The range is **provenance uncertainty**: the spread of published values for one
input, nothing more. It is not a confidence interval, not a prediction interval,
and it does not cover any of the model assumptions in the caveats below. When
the fixture records no unresolved conflict the map is empty and the column does
not appear.

### 6. `panel_concentration()` / `burden_shares()` — what the panel really covers

Two independent measures over the blended cohort, deliberately kept apart:

- `panel_concentration()` is a Herfindahl index over the non-reference alleles.
  It reports total variant load, HHI, effective allele count (`1 / HHI`), the
  dominant allele and its share of the variant pool, and `silent_alleles` for
  anything pinned at 0.0. Shares are of the variant pool rather than of the
  population, so a panel where one variant dominates scores the same whether
  that variant is common or rare. Cheap allele arithmetic; says nothing about
  phenotype.
- `burden_shares()` is leave-one-out ablation through steps 3–4: drop one
  variant allele, hand its frequency back to `*1` so the space still sums to
  1.0, and attribute the fall in at-risk fraction to the removed allele. More
  expensive, and the one that actually attributes IM + PM risk. This is the
  figure to quote.

`coverage_note()` renders both as one sentence on every Tier 0 finding, after
the partial-ancestry caveat from step 2 — a missing population is a bigger
problem than the shape of the panel that did apply. For a fully South Asian DPYD
cohort it reads 1.12 effective alleles, HapB3 carrying 94.2% of actionable
burden, and `*13` never firing ([FINDINGS.md](FINDINGS.md) Finding 1). A
four-variant panel is only a four-variant panel where all four fire.

The same share map drives a verdict. `rules.contested_burden()` raises a
separate `CONTESTED` finding when an allele whose CPIC dose action is disputed
holds at least 60% of the cohort's actionable burden. For DPYD that allele is
HapB3: carriers dosed at the standard 25% reduction showed reduced treatment
effectiveness *and* increased toxicity
([PMID 37639651](https://pubmed.ncbi.nlm.nih.gov/37639651/)). The screening-gap
finding says the protocol should test; the `CONTESTED` finding says that for
most positives in this cohort a positive test has no settled clinical response.
Those are two different claims, so they are two findings rather than one with a
note. The 0.60 threshold is a judgement call, not a derived constant, and EUR
clears it too at 63.9% — the verdict tracks the dosing dispute, not the
population.

---

## Why this is Tier 0

Every number above is multiplication and addition over two pinned inputs: a
frequency table with recorded provenance, and a CPIC diplotype→phenotype table
pinned at `v2024.01`. No model is involved. No network call is involved. Any
figure in a report can be re-derived by hand from the same fixtures.

That is what `Tier.DISTRIBUTION` asserts, and it is the reason `--offline` is the
default rather than a flag.

Claims that need a literature effect multiplier are **Tier 1** and must carry a
citation. Claims about trial outcomes are **Tier 2** and are labelled scenarios,
never predictions. The tiers exist so a reader can always tell which kind of
number they are looking at.

---

## Limits and honest caveats

Hardy-Weinberg assumes random mating, no selection on the locus, no recent
migration, and a large well-mixed population. Real populations violate these to
varying degrees. Consequences, stated plainly:

**1. Homozygotes are likely undercounted.** Consanguinity and endogamy — both
relevant in South Asian populations — increase homozygosity above the `q²`
prediction. Since homozygotes are the Poor Metabolizers, **the model's estimate
of the most severe class is likely conservative.** The direction of the error is
known even though its magnitude is not, and reporting an unadjusted `q²` should
be understood as a floor, not a point estimate.

*Magnitude, for scale.* Under inbreeding with coefficient `F`, homozygote
frequency becomes `q² + F·p·q` and heterozygotes `2pq·(1 − F)`. Measured `F` in
South Indian populations runs **0.0203–0.0339** (Karnataka; consanguineous
marriage 23% in the South region against 9.9% nationally per NFHS 2015–16).
Applying `F = 0.0231` to HapB3 at SAS `q = 0.0169` gives `q² + F·p·q ≈ 0.000669`
against `q² ≈ 0.000285` — roughly **2.3× the random-mating homozygote
frequency**.

This is *not* applied in the engine. `F` is an external parameter, so any
adjusted figure would be Tier 1 rather than Tier 0, and
`diplotype_frequencies()` deliberately stays pure Hardy-Weinberg with a
sum-to-one invariant. The number is given here so the caveat carries a scale
instead of only a direction. Note also that consanguinity varies *within*
India — Kerala is documented as having very low rates and effectively no
uncle-niece marriage, unlike the other southern states — so this is a genuine
per-site difference, not a national constant.

**2. `SAS` is a coarse bucket.** "South Asian" spans populations with materially
different allele frequencies. A re-scoring pilot against IndiGenomes (1,029 Indian
genomes) found the gnomAD-SAS proxy held closely for some alleles — SLCO1B1 `*5`
within 1.6%, CYP2C9 `*3` within 0.3% — but diverged by **34.2%** for CYP2C9 `*2`.
So proxy quality is allele-specific, not population-wide, and cannot be assumed.

*For DPYD specifically, the proxy has been checked.* Naushad et al. screened
**2,000 Indian subjects** for DPYD variants (*J Gene Med* 2021, PMID 33105068)
and concluded that "clustering analysis revealed the similarities in the DPYD
profiles of the Indian and South Asian populations", with their data matching
ALFA South Asian frequencies. Their Level 1A (non-functional) alleles —
`rs75017182`, `rs3918290`, `P633Qfs*5`, `D949V` — carry a combined MAF of
**1.889%**, the same order as this tool's pinned variant set. So the SAS proxy is
defensible *for this gene*; that finding does not transfer to other genes.

That paper also independently corroborates the platform's own DPYD override
audit: **M166V sits at 8.993% in 2,000 Indians with a null toxicity
association**, confirming it is common and not the actionable signal.

**Known gap it surfaces:** Naushad found **V732I** and **S534N** associated with
5-FU/capecitabine toxicity in pooled Indian data. Neither is in this tool's
pinned table, and neither is in the UK/EU four-variant panel. A South Asian
cohort audited here — or screened under the current UK/EU panel — would miss
both.

**3. Site ancestry mixes are estimates.** A site's actual recruited ancestry
composition is an assumption supplied in the protocol fixture, not a measurement.
Garbage in, garbage out — which is why the field is explicit and inspectable
rather than inferred.

**4. This is a distribution, not a diagnosis.** The output says "expect roughly
N intermediate metabolizers among 150 enrollees." It does not identify which
patients. It is a feasibility and screening-policy instrument, not a clinical
result for any individual. Per-patient calling is what
[`anukriti-pgx-core`](https://github.com/AnukritiAi-hq/anukriti-pgx-core) does
from an actual VCF; `cohortfit` never sees a genome.

**5. Genotype-based methods have a documented ceiling, and this inherits it.**
In a cohort of 712 patients given both DPD phenotyping and four-variant
genotyping, the two disagreed for 12.5%, and **8.8% were biochemically deficient
(uracil ≥ 16 µg/L) while carrying no panel variant**
([PMID 36918744](https://pubmed.ncbi.nlm.nih.gov/36918744/)). Sequencing extra
variants reduced discordance only from 12.5% to 12.1%. Part of the residual is
not genetic at all — liver dysfunction elevates uracil independently. So roughly
one in eleven DPD-deficient patients is invisible to *any* genotype-based
approach, including this one.

### The biases stack in one direction

Caveats 1, 2 and 5 are not independent uncertainties that might cancel:

| Source | Effect on reported burden | Magnitude |
|---|---|---|
| Consanguinity (`q² + Fpq`) | Poor Metabolizers undercounted | ~2.3× homozygotes |
| `*2A` exome undercount | IM + PM undercounted | up to 1.41× at-risk |
| Genotype-invisible deficiency | at-risk undercounted | ~8.8% of deficient patients |

**Every known bias in this pipeline makes the reported burden too low.** That is
the right direction for a safety instrument — the tool under-promises rather than
over-promising — but it should be stated rather than left for a reviewer to
discover. Quantified in [FINDINGS.md](FINDINGS.md) Finding 7.

---

## Why the caveats are in the repo

A tool that reports population-genetics numbers without stating its assumptions
is the failure mode this project exists to prevent.

The platform shipped a rule that blocked clinical synthesis for South Asian
patients on a *"27% carrier frequency"* claim citing a real paper. The paper was
real; the number was hand-written and never came from the pinned frequency data.
It ran live for 52 days before a manual audit caught it
(`anukriti_docs/DPYD_SAS_OVERRIDE_AUDIT_2026-07-28.md`).

The lesson was not "check harder." It was that a number with no traceable
provenance and no stated assumptions is indistinguishable from a correct one
until someone audits it. Hence: pinned inputs, provenance fields, tier labels,
an `Indeterminate` bucket, and this document.
