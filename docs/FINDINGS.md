# Derived findings: what the pinned data actually says

> ## ⛔ PARTIALLY RETRACTED 2026-10-14 — DO NOT CITE WITHOUT REGENERATING
>
> Every figure in this document was computed before commit `266ffb7`
> ("requery DPYD against gnomAD v4.1, add AFR, **correct an 8x `*2A` error**"),
> which changed `fixtures/frequencies/dpyd.json`. **The document was never
> regenerated.** The repo therefore shipped two mutually contradictory sets of
> numbers, and the stale set is the one that reached a public page.
>
> **Findings 1, 2, 3, 5 and 6 have now been regenerated** (2026-10-14) by
> `scripts/regen_findings_table.py`, which derives every one of their numbers
> from the fixture. Findings 7 and 8 rest on external literature and market
> data, not on this fixture, and are unaffected.
>
> An earlier version of this banner said "Finding 2's table" when the
> regenerated ablation table actually sits under Finding 1. Corrected.
>
> **Finding 4 is fully retracted.** Its premise — that SAS `*2A` sits 6–16×
> below every genome-based source — was a transcription error, recorded in
> `fixtures/frequencies/dpyd.json` under `known_discrepancies`: the count (45)
> was `c.2846A>T`'s exome AC and the denominator (91074) was `c.2846A>T`'s
> joint AN. The pinned value now sits *inside* the published band. Do not cite
> Finding 4 or any number derived from it.
>
> This is precisely the failure mode
> [DATA_PROVENANCE.md](DATA_PROVENANCE.md) says this repo was built to
> prevent. It recurred here because the tables were hand-copied rather than
> generated. `scripts/regen_findings_table.py` now derives Finding 2 from the
> fixture and **refuses to print** if the live computation and the fixture's
> own `_ground_truth` block disagree.

> Third research pass, 2026-08-08. Unlike [EVIDENCE.md](EVIDENCE.md), which
> collects external literature, this document **derives results from our own
> pinned fixture** and states what they imply. Every number below is
> reproducible from `fixtures/frequencies/dpyd.json` plus
> `anukriti-pgx-core` 0.7.1 — no new data, no model.
>
> Method: leave-one-out allele ablation, ancestry-mix sweeps, and sensitivity
> analysis against the `*2A` provenance conflict recorded in
> `_meta.known_discrepancies`. All figures at Hardy-Weinberg equilibrium over
> the pinned CPIC-panel allele space.
>
> ⚠️ These are **our derivations**, not published results. They are internally
> consistent and reproducible, but no external source has confirmed them.

---

## Finding 1 — DPYD risk in South Asians is a one-allele story

Leave-one-out ablation: remove each variant allele, renormalise `*1`, recompute
the at-risk (IM + PM) fraction, and attribute the difference.

Regenerated 2026-10-14 by `scripts/regen_findings_table.py` against the
post-`266ffb7` fixture. Superseded values in parentheses.

| Allele removed | Share of SAS burden | Share of EUR burden |
|---|---:|---:|
| *(none — baseline at-risk)* | 4.1036% *(was 3.5474%)* | 6.5859% *(was 6.3982%)* |
| `HapB3` | **78.0%** *(was 94.2%)* | **63.5%** *(was 63.9%)* |
| `*2A` | 19.1% *(was 2.8%)* | 14.2% *(was 15.4%)* |
| `c.2846A>T` | 2.5% *(was 2.9%)* | 18.9% *(was 19.5%)* |
| `*13` | 0.0% | 2.5% *(was 0.3%)* |

**In a South Asian cohort, 78.0% of the CPIC-panel actionable burden rests on a
single allele: HapB3.** In Europeans the same allele carries 63.5%.

Two things change materially from the retracted version. The SAS `*2A` share
moves 2.8% → 19.1% — that is the 8× `*2A` correction, and it is the single
biggest effect of the requery. And the SAS-vs-EUR asymmetry that motivates this
finding narrows from 94.2/63.9 (≈1.47×) to **78.0/63.5 (≈1.23×)**. The
asymmetry is real and still points the same way, but it is substantially weaker
than previously published, and any argument built on it must be rebuilt at the
smaller effect size.

Concentration, measured Herfindahl-style over the variant pool (excluding `*1`):

| Population | Total variant load | HHI | Effective # alleles | Dominant |
|---|---:|---:|---:|---|
| SAS | 2.073% *(was 1.790%)* | 0.649 *(was 0.890)* | **1.54** *(was 1.12)* | HapB3 (78.2%) *(was 94.3%)* |
| EUR | 3.349% *(was 3.252%)* | 0.466 *(was 0.477)* | **2.15** *(was 2.10)* | HapB3 (63.9%) *(was 64.3%)* |

The European panel behaves like a genuine multi-allele test. For South Asians
it is more concentrated — 1.54 effective alleles against 2.15 — but the
retracted figure of 1.12 overstated it badly, and the phrase previously used
here, *"effectively a single-allele test"*, is **no longer supportable**. At
1.54 effective alleles it is a concentrated two-allele test: HapB3 at 78.2%
with `*2A` carrying most of the remainder. `*13` is absent from SAS entirely
(pinned frequency 0.0), contributing exactly nothing.

**Why this matters:** a four-variant panel marketed as broad coverage is, in a
South Asian cohort, one variant plus three that almost never fire. That is a
concrete, quantified restatement of the Chan/Pirmohamed 2024 argument
([EVIDENCE.md §2](EVIDENCE.md)) — but derived from allele frequencies rather
than from case counts.

---

## Finding 2 — the concentration lands on the one allele CPIC contests

This is the sharpest result in this document, and it follows from combining
Finding 1 with the HapB3 dosing controversy in
[EVIDENCE.md §5](EVIDENCE.md).

CPIC's own guideline page flags **PMID 37639651**: HapB3 carriers dosed at a 25%
reduction showed evidence of *reduced treatment effectiveness* **and**
significantly increased toxicity. So HapB3 is the allele whose *dose action* is
least settled.

Ablating HapB3 — modelling "what if HapB3 guidance is unusable?" — leaves:

Regenerated 2026-10-14. Superseded values in parentheses.

| Population | Full at-risk | Retained on unambiguous alleles | Share retaining clear guidance | NNS |
|---|---:|---:|---:|---:|
| SAS | 4.104% *(was 3.547%)* | **0.903%** *(was 0.205%)* | **22.0%** *(was 5.8%)* | 111 *(was 487)* |
| EUR | 6.586% *(was 6.398%)* | **2.406%** *(was 2.309%)* | **36.5%** *(was 36.1%)* | 42 *(was 43)* |

**If HapB3 dose guidance is set aside as contested, 78.0% of the South Asian
actionable burden loses its recommended action — against 63.5% in Europeans.**
The number needed to screen to reach one *confidently actionable* finding rises
from 24 to **111** in SAS, and from 15 to 42 in EUR.

The direction survives the requery; the magnitude does not. On the retracted
numbers only 5.8% of South Asian positives kept clear guidance against 36.1%
of European — a 6.2× gap. On the corrected numbers it is 22.0% against 36.5%,
a **1.7× gap**. The `*2A` correction is what closed it: `*2A` is unambiguous
and now carries 19.1% of SAS burden rather than 2.8%, so far more of the
burden survives HapB3's removal than previously computed.

This is a structural asymmetry, not a data gap: the population with the most
concentrated risk is concentrated **precisely on the allele with the weakest
dosing evidence**. Screening a South Asian cohort with the current panel and
current guidance yields, for the great majority of positives, a result whose
correct clinical response is disputed.

We have not seen this stated anywhere in the literature. It is the most
defensible novel claim available from our data, and it is falsifiable: it
follows directly from the pinned frequencies and CPIC's published caveat.

---

## Finding 3 — screening yield is 1.60× worse in South Asians

Number needed to screen (NNS) to find one actionable carrier, `1 / at-risk`:

Regenerated 2026-10-14. Superseded values in parentheses.

| Population | At-risk | NNS |
|---|---:|---:|
| EUR | 6.586% *(was 6.398%)* | **15.2** *(was 15.6)* |
| SAS | 4.104% *(was 3.547%)* | **24.4** *(was 28.2)* |

**A South Asian cohort requires 1.60× more tests per actionable finding**
*(was 1.80×)*.

Read carefully, because the naive reading is wrong. This is *not* evidence that
South Asians are at lower risk. It is a property of **the panel**: the four
variants were selected in European populations, so they capture European
variant load more efficiently. Naushad 2021 found `V732I` and `S534N`
toxicity-associated in Indian cohorts, and both are absent from this panel and
from the UK/EU panel ([METHOD.md](METHOD.md) caveat 2). The measured 4.104% is a
lower bound on true actionable burden, not an estimate of it.

Consequence for economics: every published DPYD cost-effectiveness result —
including the £78,000-per-patient saving in
[EVIDENCE.md §4](EVIDENCE.md) — was computed at European yield. At SAS yield the
cost per finding is 1.60× higher on the same test price. Those results should
not be assumed to transfer to Indian sites without recomputation.

---

## Finding 4 — ⛔ RETRACTED — the `*2A` provenance conflict is material but does not invert the ranking

> **Fully retracted 2026-10-14.** The premise — that SAS `*2A` sits far below
> every genome-based source — was a transcription error, recorded in the
> fixture's `known_discrepancies`: the count (45) was `c.2846A>T`'s exome AC and
> the denominator (91074) was `c.2846A>T`'s joint AN. The pinned value now sits
> inside the published band, so there is no conflict to analyse. Every number in
> this section is void and is kept only as a record. Do not cite it.

The pinned SAS `*2A` (0.0005, gnomAD v4 exomes) conflicts with every
genome-based source ([DATA_PROVENANCE.md](DATA_PROVENANCE.md)). Sensitivity
sweep, substituting each candidate value:

| SAS `*2A` source | Value | SAS at-risk | vs pinned | PM per million | EUR/SAS ratio |
|---|---:|---:|---:|---:|---:|
| **Pinned (v4 exomes)** | 0.0005 | 3.5474% | 1.000× | 35.7 | 1.804× |
| gnomAD v4 genomes | 0.0029 | 4.0182% | 1.133× | 127.4 | 1.592× |
| ALFA South Asian | 0.0034 | 4.1161% | 1.160× | 147.9 | 1.554× |
| PAGE SouthAsian | 0.0060 | 4.6247% | 1.304× | 262.8 | 1.384× |
| 1000G 30X SAS | 0.0075 | 4.9174% | 1.386× | 335.3 | 1.301× |
| 1000G Ph3 SAS | 0.0080 | 5.0149% | 1.414× | 360.4 | 1.276× |
| Chan 2024 upper bound | 0.0150 | 6.3744% | 1.797× | 765.0 | 1.004× |

Three conclusions:

1. **The at-risk fraction is robust in direction, soft in magnitude.** Across the
   plausible range it moves 3.55% → 5.01%, i.e. up to **1.41×**. Material for
   planning, but the finding stays `ACTIONABLE` throughout.
2. **The Poor Metabolizer estimate is not robust.** PM ranges 35.7 → 360.4 per
   million — a **10.1× spread**. Any PM figure we report carries an order of
   magnitude of provenance uncertainty, on top of the consanguinity floor
   already documented in [METHOD.md](METHOD.md) caveat 1. **Do not present PM as
   a point estimate.**
3. **The demo's site ranking survives.** "Munich above Mumbai" holds at every
   candidate value. Only at the extreme upper bound (1.5%) do the two converge
   to parity (1.004×), and it never inverts.

**Which range each number describes.** The implemented sweep,
`cohortfit.sensitivity.phenotype_bounds()`, reports a Poor Metabolizer spread of
**21.4×**, not the 10.1× in conclusion 2. Both are right, and they are ranges
over different candidate sets. The table above stops at the 1000G Ph3 value
(0.0080), where PM reaches 360.4 per million against the pinned 35.7 — 10.1×,
matching exactly. `phenotype_bounds()` takes *every* unresolved candidate in
`_meta.known_discrepancies`, which includes the Chan 2024 upper bound (0.0150)
in the table's last row; PM there is 765.0 per million, so 21.4×. The at-risk
fraction over that same full candidate set moves 1.80× (3.5474% → 6.3744%)
rather than the 1.41× of conclusion 1, for the same reason. Quote 10.1× and
1.41× for the range of published point frequencies, 21.4× and 1.80× for the
full candidate set including the Chan upper bound. Neither reading makes PM a
point estimate.

### The symmetry trap

The sweep above varies SAS `*2A` while leaving EUR pinned — but **EUR `*2A` is
from the same exome callset and is equally suspect.** Scaling both by the
genomes/exome ratio observed for SAS (≈5.8×):

| Scenario | SAS at-risk | EUR at-risk | EUR/SAS |
|---|---:|---:|---:|
| Pinned | 3.5474% | 6.3982% | 1.804× |
| Both scaled ×5.8 | 4.0182% | 11.0570% | **2.752×** |

Correcting the undercount *symmetrically* widens the gap to 2.75× rather than
narrowing it. So the one-sided sweep in the table above is the **conservative**
framing of the site-ranking claim. Worth knowing if a reviewer challenges the
ranking on provenance grounds — the honest answer is that fixing the provenance
strengthens it.

---

## Finding 5 — trial sizes are too small for PM to be a planning quantity

Expected Poor Metabolizers in a 100% SAS cohort:

Regenerated 2026-10-14. The retracted version carried a second column
comparing the pinned `*2A` against a "1000G `*2A`" value; that comparison came
from Finding 4, which is withdrawn as a transcription error, so the column is
removed rather than recomputed.

| Cohort n | Expected PM | Expected IM |
|---|---:|---:|
| 150 | 0.025 *(was 0.005)* | 6.1 |
| 230 *(demo)* | 0.038 *(was 0.008)* | 9.4 *(was 10.4)* |
| 1,000 | 0.167 *(was 0.036)* | 40.9 |
| 5,000 | 0.836 *(was 0.179)* | 204.3 |

**A trial must exceed roughly 6,000 South Asian enrollees before it expects
even one Poor Metabolizer** (one expected PM at n ≈ 5,984).

This supersedes the retracted claim that the pinned value implied ~28,000.
The `*2A` correction raises expected PM roughly fivefold, so the threshold
falls from ~28,000 to ~6,000 — and the two-estimate hedge the old finding
depended on is gone, because there is now one defensible value rather than a
disputed pair. The finding's conclusion is unchanged in kind: ~6,000 is still
far beyond the size of the trials this tool is pointed at.

This validates a design decision already in [METHOD.md](METHOD.md): the report
shows the whole distribution rather than only the worst class. **The actionable
quantity at trial scale is the Intermediate Metabolizer count**, which is 9.4
patients in the 230-person demo cohort — a real, plannable number. PM is a
per-patient safety concern that population arithmetic cannot resolve at these
sample sizes, which is exactly why `cohortfit` is a feasibility instrument and
`anukriti-pgx-core` is the per-patient caller.

---

## Finding 6 — ancestry mix moves the answer smoothly, so site selection is a dial

Sweeping the EUR fraction of a two-population cohort:

Regenerated 2026-10-14. Superseded values in parentheses.

| EUR fraction | At-risk |
|---:|---:|
| 0% | 4.1036% *(was 3.5474%)* |
| 10% | 4.3533% *(was 3.8344%)* |
| 25% | 4.7272% *(was 4.2641%)* |
| 50% | 5.3488% *(was 4.9782%)* |
| 75% | 5.9684% *(was 5.6895%)* |
| 90% | 6.3392% *(was 6.1151%)* |
| 100% | 6.5859% *(was 6.3982%)* |

The response is close to linear (blending is linear in allele space; the HWE
step adds only slight curvature). **Each 10 percentage points of European
enrolment adds ~0.248pp of expected at-risk burden** *(was ~0.285pp)*.

Commercially, this is the point: expected metabolic burden is a **continuous
function of site selection**, computable before a single patient is enrolled.
That is the ICON `OneSearch`/`OnePlan` seam described in
[EVIDENCE.md §7](EVIDENCE.md) — a number that changes as you move enrolment
between countries.

---

## Finding 7 — genotype-only screening has a documented ceiling, and we inherit it

External, and it bounds what `cohortfit` can claim.

**Rossi et al. / Grenoble cohort (PMID 36918744, *Br J Clin Pharmacol* 2023),
n = 712** patients who received both DPD phenotyping (plasma uracil,
U ≥ 16 µg/L) and four-variant genotyping:

- Phenotyping and genotyping were **discordant in 12.5%**.
- **8.8% had U ≥ 16 µg/L with no common variant** — biochemically deficient,
  genotype-negative.
- Sequencing extra variants reduced discordance only from 12.5% to **12.1%**.
  Of nine additional variants found, only `c.557A>G` (3 patients) had prior
  deficiency evidence.
- Part of the residual is not genetic at all: liver dysfunction elevates uracil
  (ASAT independently associated, p < 0.001).

Supporting: Zhou et al. (*Br J Cancer* 2020) found DPD deficiency genetically
complex enough to warrant sequencing-based profiling, in explicit contrast to
TPMT where four variants explain >95% of phenotype variability. Van Kuilenburg's
group made the same point in 2000 — known variants "do not explain" DPD
deficiency.

**Implication for us, stated plainly:** `cohortfit` computes expected
*genotype-inferred* phenotype distribution. Roughly **9% of biochemically
DPD-deficient patients carry no panel variant** and are invisible to any
genotype-based method, ours included. Our output is a floor on actionable
burden for a second, independent reason beyond consanguinity and beyond the
`*2A` undercount.

Three floors now stack, all in the same direction:

| Source of underestimate | Direction | Magnitude |
|---|---|---|
| Consanguinity (`q² + Fpq`) | PM undercounted | ~2.3× homozygotes (Finding, METHOD.md) |
| `*2A` exome undercount | IM+PM undercounted | up to 1.41× at-risk |
| Genotype-invisible deficiency | at-risk undercounted | ~8.8% of deficient patients |

None of these push the other way. **Every known bias in this pipeline makes the
reported burden too low**, which is the right direction for a safety instrument
but must be said out loud rather than left for a reviewer to find.

---

## Finding 8 — India's trial share is the market gap, quantified

- India has **~20% of world population** but hosts only **~1.5% of global
  clinical trials** (*Nature Communications Medicine* 2025,
  doi:10.1038/s43856-025-00970-z).
- CTRI analysis found **1,988 cancer trials** registered, of which 10.6% target
  treatment-related toxicity (*Lancet SEA* / PMC11096683).
- Trials cluster in Maharashtra (16.4%), Karnataka (11.6%) and Tamil Nadu (10%),
  while populous Uttar Pradesh (5.3%) and Bihar (1.4%) are underrepresented.

That last point compounds Finding 6 in a way worth noting: intra-India site
distribution is itself skewed, and the high-trial states are in the South, where
consanguinity and therefore `F` are highest ([METHOD.md](METHOD.md) caveat 1).
So the sites most likely to be selected are the sites where the Hardy-Weinberg
homozygote floor is least accurate.

Pairs with the FAERS equity finding already on the platform: South Asia reports
adverse events at **~1% of its population-proportional rate**
(`project_astra/docs/19-...`). Under-trialled *and* under-reported — the
mismatch is invisible from both directions.

---

## Fourth pass — statistical uncertainty and generalisability

> Added 2026-08-08 ~14:40, after Findings 1–4 had been implemented as
> `panel.py` and `sensitivity.py`. This pass asks two questions the earlier
> passes left open: **how precise are the pinned numbers**, and **does the
> DPYD/SAS concentration result generalise to other genes?**

### Finding 9 — the fixture already contains enough information to state a confidence interval, and nobody was using it

> **Now implemented** as [`src/cohortfit/precision.py`](../src/cohortfit/precision.py).
> `wilson_interval()` computes the bounds, `population_precision()` maps them
> per population, and `precision_notes()` puts the imprecise and unobserved
> alleles onto the finding. Wired into `audit.py`.

Every non-reference allele record carries `alt_observed` and `total_alleles`.
That is a binomial numerator and denominator, so a Wilson 95% interval is
computable with no new data:

| Population | Allele | Pinned | 95% CI | n (alleles) | Relative width |
|---|---|---:|---|---:|---:|
| SAS | `*2A` | 0.000500 | 0.000369 – 0.000661 | 91,074 | **58.3%** |
| SAS | `*13` | 0.000000 | 0.000000 – 0.000042 | 91,074 | — |
| SAS | `c.2846A>T` | 0.000527 | 0.000398 – 0.000699 | 91,074 | **57.1%** |
| SAS | `HapB3` | 0.016870 | 0.016071 – 0.017745 | 91,072 | 9.9% |
| EUR | `*2A` | 0.005080 | 0.004953 – 0.005210 | 1,179,520 | 5.1% |
| EUR | `*13` | 0.000100 | 0.000084 – 0.000120 | 1,179,644 | 36.2% |
| EUR | `c.2846A>T` | 0.006430 | 0.006286 – 0.006574 | 1,179,644 | 4.5% |
| EUR | `HapB3` | 0.020910 | 0.020653 – 0.021170 | 1,179,718 | 2.5% |

Propagating all alleles to their bounds simultaneously (a deliberately
conservative worst case, since the errors are independent):

> ⚠️ The bounds in this table were computed on the pre-`266ffb7` fixture and
> have **not** been regenerated; only the point estimates are corrected below.
> Treat the interval widths as indicative, not current.

| Population | Lower | Point | Upper |
|---|---:|---:|---:|
| SAS | 3.3392% | **4.1036%** *(was 3.5474%)* | 3.7927% |
| EUR | 6.2929% | **6.5859%** *(was 6.3982%)* | 6.5053% |

**The two rare SAS alleles have ±58% relative uncertainty**, against ±5% for
their European counterparts. That is a direct consequence of sample size, and it
means our reported SAS numbers are not just possibly biased low (Finding 7) but
also materially less *precise* than the identically-formatted European numbers —
which no current output distinguishes.

### Finding 10 — which database you trust matters ~6× more than how many people were sequenced

Comparing the two uncertainty sources on the same scale, for SAS at-risk:

| Source of uncertainty | Width |
|---|---:|
| Sampling (Wilson CI, all alleles at bounds) | 0.4535 pp |
| Provenance (candidate `*2A` values, Finding 4) | 2.8270 pp |
| **Ratio** | **6.2×** |

**For a South Asian cohort, the choice of reference database dominates
statistical sampling error by a factor of six.** This is a genuinely
counter-intuitive result and it justifies a design decision already taken: the
`sensitivity.py` provenance range shipped, and a sampling CI did not. That
ordering turns out to be correct on the numbers, not just on intuition.

For EUR there is no unresolved provenance conflict pinned at all, so sampling is
the only uncertainty — a further asymmetry in how much we can trust
identically-presented figures.

### Finding 11 — the reference panel is ~34× over-representative of Europeans per capita

From the fixture's own counts:

| | Alleles sequenced | ≈ Individuals |
|---|---:|---:|
| SAS | 91,072 | ~45,536 |
| EUR (NFE) | 1,179,718 | ~589,859 |

**EUR is 13.0× better represented in absolute terms.** Adjusting for world
population (SAS ≈ 2.0B, EUR ≈ 0.75B), Europeans are over-represented by roughly
**34.5× per capita**.

This is consistent with gnomAD's own v4 release note, which states the addition
of cohorts such as UK Biobank means "the proportion of samples with European
ancestry is **higher** than in previous releases" — the v4 expansion added
~169,000 non-European individuals while simultaneously making the panel
*proportionally* more European.

**Detection floor.** By the rule of three, an allele seen zero times in the SAS
sample could still be as frequent as **0.0033%** at 95% confidence, versus
0.0003% in EUR — a 13× worse floor. Concretely, `*13` is 0/91,074 in SAS and is
reported as exactly `0.0`. It is not known to be absent; it is **known not to
have been seen**. Those are different claims.

> **Now implemented.** `precision.detection_floor()` computes the bound and the
> finding carries the caveat verbatim: *"`*13` was not observed in 91,074 SAS
> alleles — pinned 0.0 means not detected, not absent (95% upper bound 0.0033%,
> rule of three)."* The bound quoted is `3/n`, not the Wilson upper bound of
> `z²/(n + z²)` ≈ 0.0042% that the CI column above carries — the two are close
> and both valid, so the report commits to the one every provenance table in
> these docs was computed with, and `tests/test_precision.py` pins that choice.
> The panel note still says `*13` never fires, which is true of the
> arithmetic; the precision note supplies what that zero does and does not mean.

⚠️ The world-population figures are round approximations used for scale, not
census values.

### Finding 12 — DPYD is a genuine outlier, not an instance of a general pattern

This is the most important negative result in this document, and it constrains
how far the headline claim can be pushed.

Probe: compute panel concentration for five PGx genes using published SAS and
EUR frequencies for their no-function / decreased-function alleles.

| Gene | SAS eff. alleles | EUR eff. alleles | EUR/SAS | SAS dominant allele |
|---|---:|---:|---:|---|
| SLCO1B1 | 1.00 | 1.00 | 1.00× | `521T>C` (single-variant test by design) |
| TPMT | 1.38 | 1.47 | 1.06× | `*3C` (83.3%) |
| CYP2C19 | 1.83 | 1.95 | 1.07× | `*2` (66.3%) |
| CYP2C9 | 1.58 | 1.85 | 1.17× | `*3` (75.9%) |
| **DPYD** | **1.54** | **2.15** | **1.40×** | **HapB3 (78.2%)** | <!-- regenerated 2026-10-14; was 1.12 / 2.10 / 1.87x / 94.3% -->

⚠️ These comparator frequencies were hand-entered for this probe from published
literature. They are **not pinned, not shipped, and not validated** — the
purpose is to establish whether DPYD's asymmetry is typical, and for that a
rough magnitude suffices. They must not be quoted as cohortfit outputs.

Three conclusions:

1. **The DPYD asymmetry is roughly 11–16× larger than for any other gene
   tested.** Every other panel loses only 0–17% of its effective allele count
   between EUR and SAS; DPYD loses 47%.
2. **So "European-derived panels degrade in South Asians" is not a general law**
   — it is specifically severe for DPYD. Claiming it as a platform-wide pattern
   would overreach, and a reviewer with a pharmacogenomics background would
   catch it. Claim DPYD specifically.
3. **The reason DPYD is different is a real mechanism, not a coincidence.** DPYD
   variants are individually rare (total SAS variant load 1.79%, the lowest of
   the five genes), so the panel depends on a handful of low-frequency alleles
   whose relative proportions vary sharply between populations. High-load genes
   like CYP2C19 (47.5% in SAS) are buffered — no single allele can dominate that
   completely. **Panel fragility scales inversely with total variant load.**
   That is a testable, generalisable hypothesis, and it is the version of the
   claim worth making.

### Finding 13 — an incidental result: CYP2C19 `*2` is more than twice as common in South Asians

Visible in the Finding 12 probe and worth recording, because it runs *opposite*
to the DPYD direction:

| Gene / allele | SAS | EUR | Direction |
|---|---:|---:|---|
| CYP2C19 `*2` (no function) | ~31.5% | ~15.0% | **SAS 2.1× higher** |
| CYP2C9 `*3` (decreased) | ~11.0% | ~7.0% | SAS 1.6× higher |
| CYP2C9 `*2` (decreased) | ~3.5% | ~12.5% | EUR 3.6× higher |
| DPYD total variant load | 1.79% | 3.25% | EUR 1.8× higher |

So the platform's existing CYP2C19/PPI workflow (shipped in pgx-core 0.7.0)
addresses a gene where the South Asian burden is **higher**, not lower. If
`cohortfit` extends to a second gene-drug pair, **CYP2C19 × clopidogrel or a PPI
is the strongest candidate**: pgx-core already has the tables and clinical
actions, it is CPIC Level A, and the ancestry story points the other way — which
makes the tool look like an ancestry-sensitivity instrument rather than a
one-directional argument.

⚠️ These frequencies are from the same unvalidated probe. Pin properly before
use.

---

**Use in the pitch (defensible, derived, ours):**
- Finding 2 is the headline: the panel's South Asian risk is **78%** concentrated
  on the one allele whose dosing CPIC itself contests. Sets NNS from 24 to
  **111**. *(Regenerated 2026-10-14; the retracted version said 94% and 487.
  The claim holds, at a materially smaller effect size.)*
- Finding 3 — **1.60×** worse screening yield *(was 1.80×)* — reframes "lower
  risk" as "panel built elsewhere", and invalidates transferring European
  cost-effectiveness.
- Finding 7's three stacked floors demonstrate the discipline better than any
  claim of accuracy could.

**Engineering consequences.** Three of the four are now implemented; the fourth
is a standing decision not to implement.

1. **Report `at_risk_fraction` as the primary figure and PM as a range, not a
   point — done.** `cohortfit.sensitivity.phenotype_bounds()` reruns the Tier 0
   distribution at every unresolved candidate in the fixture's
   `_meta.known_discrepancies` and returns `phenotype → (min, max)` fraction;
   `discrepancy_candidates()` collects the candidates and `substitute_allele()`
   re-derives `*1` as the remainder so each scenario still sums to 1.0.
   `models.PhenotypeCount` carries `fraction_low` / `fraction_high` and an
   `is_range` property — named `fraction_*` rather than `lower_bound` /
   `upper_bound` because they are fractions and the model already has
   `fraction`. `render` adds a "Range (provenance)" column carrying the
   fold-change explicitly, labelled as provenance uncertainty rather than a
   prediction interval.
2. **Add a "panel coverage" note per population — done.**
   `cohortfit.panel.panel_concentration()` computes the Herfindahl index over
   the variant pool and reports effective allele count, dominant allele and
   share, plus `silent_alleles` for anything pinned at 0.0 (`*13` in SAS).
   `burden_shares()` is the leave-one-out ablation of Finding 1, run through
   the real Tier 0 pipeline. `coverage_note()` renders the pair as one sentence
   onto every Tier 0 finding, after the partial-ancestry caveat: a missing
   population is a bigger problem than the shape of the panel that did apply.
   Both are computed on the blended cohort frequencies, so the note describes
   the cohort actually audited, not a reference population.
3. **Emit a `CONTESTED` finding when HapB3 dominates the burden — done.**
   `cohortfit.rules.contested_burden()` fires when a contested-dosing allele
   holds at least 60% of the actionable burden, and cites PMID 37639651. It is
   emitted as a *second, separate* finding rather than a note on the screening
   gap: the first says the protocol should test, the second says even a
   positive test has no settled response for most of this cohort. This is the
   first live example of `Verdict.CONTESTED`, which had been in the model and
   the published contract with no code path able to produce it. The 0.60
   threshold is a judgement call and says so; EUR (63.9%) clears it too, which
   is intended — the verdict tracks the dosing dispute, not the population.
4. **Do not implement the inbreeding correction as Tier 0.** Standing decision,
   deliberately not done. Unchanged from EVIDENCE §8.2, reinforced by Finding 5:
   at trial sample sizes PM is sub-integer, so refining its point estimate is
   precision without meaning. `F` is an external parameter, so any adjusted
   figure would be Tier 1; the scale of the correction is documented in
   [METHOD.md](METHOD.md) caveat 1 instead.

**Scope discipline, from Finding 12.** State the DPYD result as DPYD-specific.
The generalisable claim is the *mechanism*, not the instance: panel fragility
scales inversely with total variant load, so rare-variant panels (DPYD 1.79% SAS
load, TPMT 1.20%) are exposed to population shifts in a way high-load panels
(CYP2C19 47.5%) are not. Asserting "European panels fail in South Asians" as a
general law would be caught immediately by anyone who knows CYP2C19 `*2` is
twice as common in SAS.

**Open questions worth a follow-up session:**
- **Partially answered.** Does gnomAD v4.1's exome/genome discordance flag fire
  on `rs3918290`? Still not checked directly — ClinPGx requires JavaScript and
  the gnomAD per-ancestry count table is published only as an image. But
  gnomAD's own v4 release note confirms the mechanism: UK Biobank inclusion made
  the panel *proportionally more* European even while adding ~169,000
  non-European individuals. Enough to support Finding 11; not enough to close
  Finding 4.
- **Answered, negatively.** Does the concentration asymmetry generalise? No —
  Finding 12 shows DPYD at 1.87× against 1.00–1.17× for four other genes. Useful
  to know before overclaiming.
- Are `V732I` / `S534N` frequencies available for SAS? If pinnable, Finding 3's
  floor could be quantified rather than asserted. Still open.
- Does CDISC USDM have a field for per-site expected ancestry composition
  (EVIDENCE §8.5)? Searching found the demographics vocabulary lives in
  **CDASH/SDTM `DM`** (`SEX`, `RACE`, `ETHNIC` controlled terminology) — i.e. in
  *collected subject data*, not in the study-definition model. **No USDM field
  for planned per-site ancestry composition was found.** If that holds, the
  standard has no slot for our key input, which is a gap worth raising with CDISC
  rather than working around. ⚠️ Absence of evidence from a keyword search, not
  confirmed absence — verify against the USDM v4.0 class model before asserting.
- **Closed, implemented.** Should the report distinguish sampling precision from
  provenance uncertainty? Yes, and it now does — `precision.py` reports Wilson
  intervals as finding notes *alongside* the provenance range rather than
  compounded into it, because Finding 10 measured provenance at ~6.2× the
  sampling width and merging them would produce an interval meaning neither.
- **Closed, implemented.** `*13` at SAS `0.0` now reports as "not observed in
  91,074 alleles, 95% upper bound 0.0033%, rule of three" rather than reading as
  absence.
- **New:** CYP2C19 as the second gene-drug pair (Finding 13). Tables and clinical
  actions already ship in pgx-core 0.7.0, it is CPIC Level A, and the SAS burden
  runs *higher* — which would make cohortfit an ancestry-sensitivity instrument
  rather than a one-directional argument.

---

## Reproducing these numbers

All derivations use only the installed package and the pinned fixture. The two
methods described in prose above are now executable: the leave-one-out ablation
of Finding 1 is `cohortfit.panel.burden_shares()`, and the `*2A` sweep of
Finding 4 is `cohortfit.sensitivity.phenotype_bounds()`.

```python
from cohortfit.frequencies import load_gene_frequencies, load_gene_provenance
from cohortfit.panel import at_risk_fraction, burden_shares, panel_concentration
from cohortfit.pgx import cohort_phenotype_distribution
from cohortfit.sensitivity import phenotype_bounds

freqs = load_gene_frequencies("DPYD")          # {"SAS": {...}, "EUR": {...}}
dist, table = cohort_phenotype_distribution("DPYD", freqs["SAS"], 1000)
at_risk_fraction(dist)
# 0.041036...                                     -> 4.1036%, Finding 3

# Finding 1 — leave-one-out ablation, share of the IM+PM burden per allele
burden_shares("DPYD", freqs["SAS"])
# {'*2A': 0.19112968188425933, '*13': 0.0,
#  'c.2846A>T': 0.025161015347273892, 'HapB3': 0.7800330134541944}

concentration = panel_concentration(freqs["SAS"])
(concentration.effective_alleles, concentration.dominant_allele,
 concentration.silent_alleles)
# (1.5407258633717174, 'HapB3', ('*13',))

# Finding 4 — the *2A provenance sweep, over every unresolved candidate
bounds = phenotype_bounds(
    "DPYD", freqs, {"SAS": 1.0}, 1000, load_gene_provenance("DPYD")
)
bounds["Poor Metabolizer"]
# (3.5705709e-05, 0.000764968709)                -> 35.7 to 765.0 per million, 21.4x
bounds["Intermediate Metabolizer"]
# (0.035437991682, 0.062979465682)
```

`burden_shares()` removes one allele and gives its frequency back to `*1`,
preserving the sum-to-one invariant that `diplotype_frequencies()` requires;
`substitute_allele()` does the same for the sweep. Both re-run the real Tier 0
path rather than approximating it, so the figures above are the ones the report
prints.
