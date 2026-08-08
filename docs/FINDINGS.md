# Derived findings: what the pinned data actually says

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

| Allele removed | SAS at-risk | Share of SAS burden | EUR at-risk | Share of EUR burden |
|---|---:|---:|---:|---:|
| *(none — baseline)* | 3.5474% | — | 6.3982% | — |
| `HapB3` | 0.2053% | **94.2%** | 2.3085% | **63.9%** |
| `c.2846A>T` | 3.4438% | 2.9% | 5.1499% | 19.5% |
| `*2A` | 3.4491% | 2.8% | 5.4127% | 15.4% |
| `*13` | 3.5474% | 0.0% | 6.3789% | 0.3% |

**In a South Asian cohort, 94.2% of the entire CPIC-panel actionable burden
rests on a single allele: HapB3.** In Europeans the same allele carries 63.9%,
with `c.2846A>T` and `*2A` contributing a meaningful 19.5% and 15.4%.

Concentration, measured Herfindahl-style over the variant pool (excluding `*1`):

| Population | Total variant load | HHI | Effective # alleles | Dominant |
|---|---:|---:|---:|---|
| SAS | 1.790% | 0.890 | **1.12** | HapB3 (94.3%) |
| EUR | 3.252% | 0.477 | **2.10** | HapB3 (64.3%) |

The European panel behaves like a genuine multi-allele test. **For South Asians
it is effectively a single-allele test** — 1.12 effective alleles. `*13` is
absent from SAS entirely (pinned frequency 0.0), contributing exactly nothing.

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

| Population | Full at-risk | Retained on unambiguous alleles | Share retaining clear guidance | NNS |
|---|---:|---:|---:|---:|
| SAS | 3.547% | **0.205%** | **5.8%** | 487 |
| EUR | 6.398% | **2.309%** | **36.1%** | 43 |

**If HapB3 dose guidance is set aside as contested, 94.2% of the South Asian
actionable burden loses its recommended action — against 63.9% in Europeans.**
The number needed to screen to reach one *confidently actionable* finding rises
from 28 to **487** in SAS, and from 16 to 43 in EUR.

This is a structural asymmetry, not a data gap: the population with the most
concentrated risk is concentrated **precisely on the allele with the weakest
dosing evidence**. Screening a South Asian cohort with the current panel and
current guidance yields, for the great majority of positives, a result whose
correct clinical response is disputed.

We have not seen this stated anywhere in the literature. It is the most
defensible novel claim available from our data, and it is falsifiable: it
follows directly from the pinned frequencies and CPIC's published caveat.

---

## Finding 3 — screening yield is 1.80× worse in South Asians

Number needed to screen (NNS) to find one actionable carrier, `1 / at-risk`:

| Population | At-risk | NNS |
|---|---:|---:|
| EUR | 6.398% | **15.6** |
| SAS | 3.547% | **28.2** |

**A South Asian cohort requires 1.80× more tests per actionable finding.**

Read carefully, because the naive reading is wrong. This is *not* evidence that
South Asians are at lower risk. It is a property of **the panel**: the four
variants were selected in European populations, so they capture European
variant load more efficiently. Naushad 2021 found `V732I` and `S534N`
toxicity-associated in Indian cohorts, and both are absent from this panel and
from the UK/EU panel ([METHOD.md](METHOD.md) caveat 2). The measured 3.547% is a
lower bound on true actionable burden, not an estimate of it.

Consequence for economics: every published DPYD cost-effectiveness result —
including the £78,000-per-patient saving in
[EVIDENCE.md §4](EVIDENCE.md) — was computed at European yield. At SAS yield the
cost per finding is 1.80× higher on the same test price. Those results should
not be assumed to transfer to Indian sites without recomputation.

---

## Finding 4 — the `*2A` provenance conflict is material but does not invert the ranking

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

| Cohort n | PM (pinned `*2A`) | PM (1000G `*2A`) | Difference |
|---|---:|---:|---:|
| 150 | 0.005 | 0.054 | +0.049 |
| 230 *(demo)* | 0.008 | 0.083 | +0.075 |
| 1,000 | 0.036 | 0.360 | +0.325 |
| 5,000 | 0.179 | **1.802** | +1.624 |

**A trial must exceed roughly 5,000 South Asian enrollees before it expects even
one Poor Metabolizer** — and only under the higher `*2A` estimate. At the pinned
value, ~28,000.

This validates a design decision already in [METHOD.md](METHOD.md): the report
shows the whole distribution rather than only the worst class. **The actionable
quantity at trial scale is the Intermediate Metabolizer count**, which is 10.4
patients in the 230-person demo cohort — a real, plannable number. PM is a
per-patient safety concern that population arithmetic cannot resolve at these
sample sizes, which is exactly why `cohortfit` is a feasibility instrument and
`anukriti-pgx-core` is the per-patient caller.

---

## Finding 6 — ancestry mix moves the answer smoothly, so site selection is a dial

Sweeping the EUR fraction of a two-population cohort:

| EUR fraction | At-risk |
|---:|---:|
| 0% | 3.5474% |
| 10% | 3.8344% |
| 25% | 4.2641% |
| 50% | 4.9782% |
| 75% | 5.6895% |
| 90% | 6.1151% |
| 100% | 6.3982% |

The response is close to linear (blending is linear in allele space; the HWE
step adds only slight curvature). **Each 10 percentage points of European
enrolment adds ~0.285pp of expected at-risk burden.**

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

## What follows from this

**Use in the pitch (defensible, derived, ours):**
- Finding 2 is the headline: the panel's South Asian risk is 94% concentrated on
  the one allele whose dosing CPIC itself contests. Sets NNS from 28 to 487.
- Finding 3 — 1.80× worse screening yield — reframes "lower risk" as "panel
  built elsewhere", and invalidates transferring European cost-effectiveness.
- Finding 7's three stacked floors demonstrate the discipline better than any
  claim of accuracy could.

**Engineering consequences:**
1. **Report `at_risk_fraction` as the primary figure and PM as a range, not a
   point.** Finding 4 shows PM spans 10.1× on provenance alone. Consider a
   `PhenotypeCount.lower_bound` / `upper_bound` pair for Tier 0.
2. **Add a "panel coverage" note per population.** Finding 1 means `*13` never
   fires in SAS and the effective panel is 1.12 alleles. That belongs in the
   report next to the distribution.
3. **Emit a `CONTESTED` finding when HapB3 dominates the burden.** Finding 2
   makes this the correct verdict for a SAS cohort, not an optional extra — and
   it finally exercises the verdict path that has no live example.
4. **Do not implement the inbreeding correction as Tier 0.** Unchanged from
   EVIDENCE §8.2, reinforced by Finding 5: at trial sample sizes PM is
   sub-integer, so refining its point estimate is precision without meaning.

**Open questions worth a follow-up session:**
- Does gnomAD v4.1's exome/genome discordance flag fire on `rs3918290`? That
  would settle Finding 4 definitively. ⚠️ Not checked — the ClinPGx page
  requires JavaScript and could not be fetched.
- Are `V732I` / `S534N` frequencies available for SAS? If pinnable, Finding 3's
  floor could be quantified rather than merely asserted.
- Does CDISC USDM have a field for per-site expected ancestry composition
  (EVIDENCE §8.5)? If not, the standard has no slot for our key input — worth
  raising with CDISC rather than working around.

---

## Reproducing these numbers

All derivations use only the installed package and the pinned fixture:

```python
from cohortfit.frequencies import load_gene_frequencies
from cohortfit.pgx import cohort_phenotype_distribution

freqs = load_gene_frequencies("DPYD")          # {"SAS": {...}, "EUR": {...}}
dist, table = cohort_phenotype_distribution("DPYD", freqs["SAS"], 1000)
at_risk = sum(d.fraction for d in dist
              if d.phenotype in ("Intermediate Metabolizer", "Poor Metabolizer"))
```

Leave-one-out ablation removes one allele and re-derives `*1` as the remainder,
preserving the sum-to-one invariant that `diplotype_frequencies()` requires.
