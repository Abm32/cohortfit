# Evidence base and open corrections

> Compiled 2026-08-08 during **Push to Prod** (Anthropic × Elevation Capital ×
> Mesa School of Business), Bengaluru. Every figure below was fetched from the
> cited source on that date, not recalled. Where a claim could **not** be
> verified it is marked ⚠️ — including three claims made by this repo itself.
>
> Purpose: give the next working session a citable factual floor, and a short
> list of corrections that are owed before any of these numbers are shown to a
> reviewer.

---

## 1. Corrections owed to this repo

These are provenance defects in `cohortfit` itself. They are listed first
because the project's whole thesis is that a number with an unverifiable source
is indistinguishable from a correct one.

### 1.1 ✅ Closed — the unverified frequency module was deleted

> **Resolved 2026-08-08.** `src/cohortfit/allele_frequencies.py` no longer
> exists. It had no importers and no tests — the audit path had already moved to
> `fixtures/frequencies/dpyd.json` (gnomAD v4.0, mandatory provenance fields,
> loader rejects incomplete entries). Deleting it was a smaller and more honest
> fix than relabelling a module nothing called. The record below stands as the
> account of the defect.

That module declared its values to be "gnomAD v2.1.1 exome allele frequencies".
**That specific claim was not verifiable.** Its DPYD `*2A` SAS value of `0.006`
was checked against every South Asian figure dbSNP reports for rs3918290:

| Source | SAS allele frequency |
|---|---|
| gnomAD v4 genomes | 0.0029 |
| ALFA (South Asian) | 0.0034 |
| PAGE Study (SouthAsian) | 0.006 |
| 1000 Genomes 30X | 0.0075 |
| 1000 Genomes Phase 3 | 0.008 |
| BJC 2024 review (SAS reference populations) | 0.003–0.015 |

`0.006` sat inside the published band and matched PAGE exactly, so the *number*
was defensible. The *label* was not: no gnomAD v2.1.1 exome release was
consulted.

**Action taken:** the module was deleted rather than relabelled. Nothing
imported it, so there was no third option worth taking.

This is the same defect class as the 52-day `U4_SAS_DPYD_OVERRIDE` incident
(`anukriti_docs/DPYD_SAS_OVERRIDE_AUDIT_2026-07-28.md`): a plausible citation
attached to a number that did not come from it.

### 1.2 ✅ Closed — `*13` is implemented

> **Resolved 2026-08-08.** The gap was in the deleted module (§1.1), which
> pinned only `rs3918290`, `rs67376798` and `rs56038477`. The live fixture
> `fixtures/frequencies/dpyd.json` carries all four, `*13` (`c.1679T>G`,
> `rs55886062`, p.Ile560Ser) included, at SAS 0.0 / EUR 0.0001. Its being zero
> in SAS is itself a reported result — `panel.panel_concentration()` lists it as
> a silent allele ([FINDINGS.md](FINDINGS.md) Finding 1). Docs no longer
> overstate coverage.

### 1.3 HapB3 is keyed on a tagging variant, not the causal one

`rs56038477` is `c.1236G>A` (p.Glu412Glu) — **synonymous**. It tags
`c.1129-5923C>G` (`rs75017182`), a deep-intronic splice variant that is the
actual cause of lost DPD activity, in near-perfect linkage disequilibrium with
the HapB3 haplotype (which also carries `rs56276561`, `rs6668296`,
`rs115349832`). Tagging is standard clinical practice and the frequency is
usable as-is; the code comment should say *tags* rather than imply causality.

### 1.4 Nomenclature note

The BJC 2024 review labels `c.2846A>T` (`rs67376798`, p.Asp949Val) as
**`DPYD*9B`**. Given that the platform already had one incident rooted in
`*9A`/`M166V` confusion, prefer the `c.` HGVS form over star nomenclature for
this allele in code, output and pitch.

---

## 2. The premise, peer-reviewed

**Chan TH, Zhang JE, Pirmohamed M. "DPYD genetic polymorphisms in non-European
patients with severe fluoropyrimidine-related toxicity: a systematic review."**
*British Journal of Cancer* 131:498–514 (17 June 2024). Open access.
DOI [10.1038/s41416-024-02754-z](https://doi.org/10.1038/s41416-024-02754-z)

This is `cohortfit`'s thesis, published, from Pirmohamed's group. PRISMA,
PROSPERO CRD42023385227, 32 studies, 53 DPYD variants, 1,313 patients, 12
countries, 5 ancestry groups.

**The panel is ancestry-mismatched to the cohort:**

- The UK and EU test **four** variants, all "identified from studies undertaken
  in European populations".
- `c.1905+1G>A` (`*2A`) *is* present in non-Europeans with severe toxicity —
  18 Indian and 7 Bangladeshi patients across six studies. SAS reference
  prevalence 0.3–1.5%; **0% in East Asian** reference populations.
- `c.557A>G` (p.Tyr186Cys) runs 1–4% in African populations, reduces DPD
  activity 15–46%, is tested by Mayo Clinic and several US commercial labs, and
  **is not in the UK NHS panel**. Carriers are treated as wild-type and dosed in
  full.
- In South Asians the review found `c.704G>A` (`rs755416212`), not in CPIC,
  predicted deleterious by 100% of in-silico tools used.
- England performs **38,000 DPYD tests per year**.
- Authors' conclusion: extending screening beyond European variants "will
  improve patient safety and reduce race and health inequalities in ethnically
  diverse societies."
- They have launched a programme, **DPYD-International**, to close this gap.

**Base rates — useful as an independent sanity check on our Tier 0 output:**

| Quantity | Value |
|---|---|
| Severe toxicity on standard fluoropyrimidine dose | 10–30% of patients |
| Mortality from severe fluoropyrimidine toxicity | 0.5–1% (up to 5% in elderly) |
| Partial DPD deficiency, European ancestry | 3–5% |
| Complete DPD deficiency, European ancestry | 0.1–0.2% |
| Patients treated with fluoropyrimidines annually | >2M worldwide, ~600k in Europe |
| DPD is responsible for catabolism of | >80% of administered 5-FU |
| DPYD variants in CPIC guideline | 82 known; 21 no function, 6 diminished |

Our engine returns **4.7% Intermediate / 0.04% Poor** for a 100% SAS cohort.
Both land inside the independently published deficiency bands. Worth saying
aloud — it is external corroboration that the arithmetic is not producing
nonsense.

---

## 3. Regulatory position is stronger than this repo currently claims

Our docs frame DPYD screening as CPIC *guidance*. In the EU and UK it is a
label requirement.

- **EMA, 30 April 2020** (Article 31 referral): patients **should be tested**
  for DPD deficiency — phenotyping or genotyping — before fluorouracil (IV),
  capecitabine, tegafur or flucytosine. Treatment is **contraindicated** in
  known complete DPD deficiency.
- **MHRA Drug Safety Update, October 2020**: "All patients should be tested for
  DPD deficiency before initiation."
- **NHS England, November 2020**: DPYD genetic testing commissioned nationally
  — among the first pharmacogenomic tests applied at national scale in the UK.
- **CPIC**: Fluoropyrimidines/DPYD guideline, 2017 update — *Clin Pharmacol
  Ther* 2018;103:210–216, **PMID 29152729**. This matches the
  `_guideline_pmid` already pinned in `pgx-core`'s
  `DPYD_CLINICAL_ACTIONS_v2024.01.json`.
- Also endorsing universal pre-treatment testing: DPWG (2020), ESMO.

**Consequence for the demo:** a protocol dosing capecitabine with no DPYD
criterion is not merely guideline-divergent — it is inconsistent with the
approved product label in the EU and UK. That is a materially sharper
`ACTIONABLE` than "CPIC advises".

### The right regulatory hook for the ancestry argument: ICH E17

**ICH E17** — General Principles for Planning and Design of Multi-Regional
Clinical Trials. It formalises **intrinsic ethnic factors** (genetic,
physiological) and extrinsic factors as potential **"effect modifiers"**
requiring holistic evaluation of treatment-effect consistency across regions.
Adopted by EMA, FDA (CDER) and implemented by China's NMPA.

This is the term of art for "does this dose hold in a South Asian cohort".
Pair it with the *Lancet Southeast Asia* paper on India's local-trial waivers
([PIIS2772-3682(24)00151-3](https://www.thelancet.com/journals/lansea/article/PIIS2772-3682(24)00151-3/fulltext)),
which argues waiving local trials is unsafe precisely because "India's
population diversity means bypassing trials could result in unanticipated
adverse effects or reduced efficacy."

### ⚠️ Do not cite FDA Diversity Action Plans as a tailwind

The FDORA §3601 statutory requirement for sponsors to file DAPs stands, and
§3602 obliges FDA to issue guidance. **But FDA removed the June 2024 draft
guidance from its website on ~24 January 2025**, following the executive order
on DEI programmes. Citing it as regulatory momentum in front of an informed
audience is a credibility risk. Use ICH E17 and EMA/MHRA instead — both stable.

---

## 4. Cost figures that replace our vague ones

Drop "a failed Phase III costs $100M–$1B". It is unsourced in our docs and
too diffuse to be actionable. Use protocol amendments instead — a recurring,
sourced line item that a pre-submission screening-gap catch plausibly prevents.

**Tufts CSDD**, *Therapeutic Innovation & Regulatory Science* (2024),
"New Benchmarks on Protocol Amendment Practices, Trends and their Impact on
Clinical Trial Performance":

| Metric | Value |
|---|---|
| Phase I–IV protocols with ≥1 amendment | **76%** (was 57% in 2015) |
| Mean amendments per protocol | **3.3** (up ~60% from 2.1) |
| Phase III protocols | 80% average 3.5 substantial amendments |
| Cost per substantial amendment, Phase II | **$141,000** |
| Cost per substantial amendment, Phase III | **$535,000** |
| Incremental time per amendment (earlier Tufts study) | ~4 months |
| Amendments deemed avoidable (2016 study) | 45% |

**The intervention we recommend is already economically established.** Per the
BJC review (its ref 98): a UK study of an extended DPYD panel found genotyping
**dominant** over standard of care — a saving of **£78,000 per patient over a
lifetime**. Studies from Canada and Iran found pre-prescription DPYD genotyping
cost-saving; US and Spain found it cost-effective. ⚠️ The £78,000 figure is
quoted as reported in BJC 2024; the underlying study was not independently
retrieved.

---

## 5. A live scientific complication: HapB3

CPIC's own guideline page flags **PMID 37639651** (Knikman et al., *J Clin
Oncol* 2023, "Survival of Patients With Cancer With DPYD Variant Alleles and
Dose-Individualized Fluoropyrimidine Therapy — A Matched-Pair Analysis"):

> "A recent publication (PMID 37639651) reported evidence for a potentially
> reduced treatment effectiveness in DPYD c.1236G>A (HapB3) carriers receiving
> fluoropyrimidine dosing reduced by 25%. In the same patient group, also
> significantly increased toxicity was observed."
> — CPIC guideline page, retrieved 2026-08-08

⚠️ Note a genuine tension in secondary coverage: the ASCO Post summary of the
same paper reports that reduced doses "did not result in poorer outcomes vs
DPYD wild-type controls receiving full doses". CPIC's caveat is HapB3-specific
and more cautious. Cite **CPIC's wording**, not the summary.

**Why this matters to us:** HapB3 is the highest-frequency allele in our pinned
table (EUR 0.042, SAS 0.012) and therefore dominates our Intermediate
Metabolizer bucket. Tier 0 arithmetic is unaffected — this is a question about
what *action* follows, not about the distribution. But if asked "so you'd
reduce the dose?", the honest answer is that for HapB3 specifically the right
action is contested *within CPIC itself*.

**This is the first genuine `CONTESTED` case available to us**, and it is
better than the `*9A`/`M166V` example because it comes from the guideline body
rather than from three disagreeing cohort studies. It now ships:
`rules.contested_burden()` fires on it, so the `CONTESTED` verdict path has a
live example in the engine rather than only in the model.

Supporting literature for HapB3's toxicity association (not its dosing):
Meulendijks et al., *Lancet Oncol* 2015;16:1639–50 — IPD meta-analysis
establishing `c.1679T>G`, `c.1236G>A`/HapB3 and `c.1601G>A` as predictors of
severe fluoropyrimidine toxicity (**PMID 26603945**).

---

## 6. Prospective evidence that genotype-guided dosing works

- **Henricks et al., *Lancet Oncol* 2018 (PMID 30348537)** — "DPYD
  genotype-guided dose individualisation of fluoropyrimidine therapy in
  patients with cancer: a prospective safety analysis." The pivotal prospective
  study; abstract states fluoropyrimidine treatment causes severe toxicity in
  up to 30% of patients, mostly from reduced DPD activity.
- **Deenen et al., *J Clin Oncol* 2016** — upfront `*2A` genotyping,
  safety and cost analysis.
- **Glewis et al., *Br J Cancer* 2022;127:126–36** — systematic review and
  meta-analysis, PGx-guided vs BSA-based dosing.
- **Henricks et al., *Int J Cancer* 2019;144:2347–54** — matched-pair analysis,
  reduced-dose therapy in `*2A` carriers.

Together: the clinical action our `ACTIONABLE` verdict recommends is supported
prospectively, endorsed by two regulators, and cost-saving. We are not asking a
reviewer to accept a hypothesis.

---

## 7. Competitive and strategic position

### ICON × Anthropic (confirmed)

Multi-year collaboration announced late July 2026. Verified details:

- ICON plc (NASDAQ: ICLR), CRO, **~40,200 staff, 99 locations, 55 countries**
  as of end-June.
- Four initial production capabilities inside ICON's **Orbis** platform:
  **site intelligence and study planning**, **predictive trial intelligence**,
  **protocol optimization**, and client technology integration.
- Claude reasoning going into ICON's **OneSearch** and **OnePlan** — site
  selection and study feasibility.
- Internal rollout: Claude Code for developers, Claude for knowledge teams,
  **Claude Science** for scientific and clinical teams.
- "Enrolment bottlenecks affecting **up to 80% of trials**."
- Pip White (ICON, Ireland/UK): "Far too often, the barrier to getting
  medicines to patients faster is operational, not scientific."
- ICON stock rose ~7–8% on announcement.

**Read this precisely.** ICON's roadmap is site selection plus protocol
optimization. `cohortfit` computes a genomic feasibility number *for a site and
a protocol*. We are not adjacent to that roadmap — we are a **missing input to
it**. That is the infrastructure claim (theme #5) with evidence instead of
assertion.

### Prior art — state it plainly if asked

The neighbourhood is populated, the specific gap is not:

- **In-silico trial platforms** exist and are moving toward regulatory
  qualification — e.g. jinkō.ai (Novadiscovery), QSP/virtual-patient work,
  digital twins, synthetic control arms (see PMID 37702936, PMID 29868882).
- **PGx-aware simulated trials** have been published, but drug-specific and
  PK/PD-driven: warfarin dosing simulation (PMID 23261867, 2013) and
  genotype-stratified warfarin protocol optimisation (PMID 29237680, 2017).
- **Not found:** any tool taking *protocol text* → ancestry-weighted allele
  frequencies → Hardy-Weinberg → CPIC phenotype distribution → guideline
  screening-gap verdict.

Claim the specific gap. Do not claim an empty field.

### Molecule lane vs operations lane

Isomorphic Labs raised a $2.1B Series B (May 2026) chasing drug *design*.
Anthropic paid $400M for Coefficient Bio and hired John Jumper from DeepMind —
then pointed its first large pharma collaboration at trial **operations**.
⚠️ These figures are carried over from `BUILD_HANDOFF.md` §2 and were not
re-verified in this pass.

---

## 8. Second pass — findings that change the code, not just the pitch

> Added later the same day. Kept separate from §1–7 so it is clear which claims
> were checked when.

### 8.1 The SAS proxy is validated *specifically for DPYD*

[`METHOD.md`](METHOD.md) caveat #2 warns that gnomAD-SAS proxy quality is
allele-specific and cannot be assumed — citing the IndiGenomes pilot where
CYP2C9 `*2` diverged 34.2%. There is now direct evidence the proxy **holds for
DPYD**.

**Naushad SM, Hussain T, Alrokayan SA, Kutala VK. "Pharmacogenetic profiling of
dihydropyrimidine dehydrogenase (DPYD) variants in the Indian population."**
*J Gene Med* 2021 Jan;23(1):e3289. **PMID 33105068**. n = **2,000 Indian
subjects**, Infinium Global Screening Array.

- Level 1A (non-functional/dysfunctional) alleles — `rs75017182`, `rs3918290`,
  `P633Qfs*5`, `D949V` — are **rare: combined MAF 1.889%**.
- Level 3 alleles predominate: **C29R 24.91%, I543V 9.047%, M166V 8.993%,
  V732I 8.44%**.
- Associated with 5-FU/capecitabine toxicity in pooled Indian data: **V732I,
  S534N, rs3918290**.
- **Null association: C29R, I543V, M166V.**
- Verbatim conclusion: "Clustering analysis revealed the similarities in the
  DPYD profiles of the Indian and South Asian populations," and their data
  "showed similarities with the South Asian data" from ALFA.

Three consequences:

1. **Our SAS proxy is defensible for this gene.** Say so, and cite this. It
   converts METHOD.md caveat #2 from an open risk into a checked one — for DPYD
   only, not in general.
2. **Sanity check on magnitude.** Their Level 1A combined MAF is 1.889%. Our
   three pinned variants sum to 2.4% (`*2A` 0.006 + `c.2846A>T` 0.006 +
   HapB3 0.012). Same order, different variant sets — theirs includes
   `P633Qfs*5` and uses `rs75017182` (the causal HapB3 variant) where we use the
   `rs56038477` tag. Not a contradiction, but worth stating rather than
   glossing.
3. **Independent corroboration of the override audit.** M166V is at 8.993% in
   2,000 Indians and shows **null association** with toxicity. That is a second
   source agreeing with `DPYD_SAS_OVERRIDE_AUDIT_2026-07-28.md`: M166V is
   common and not the actionable signal. It also flags **V732I and S534N** as
   Indian-relevant toxicity-associated variants that are in *neither* our pinned
   table nor the UK/EU four-variant panel.

### 8.2 Consanguinity data makes the per-site deltas real

`BUILD_HANDOFF.md` §6 flags a demo weakness: both fixture sites are
`{"SAS": 1.0}`, so per-site deltas are driven only by `planned_n`, and advises
saying "add a European site and it diverges" before a judge notices. **There is
a better answer, and it is already in the fixture.**

Consanguinity — and therefore the inbreeding coefficient F — varies sharply
*within* India, and our two fixture sites sit at opposite ends of that range:

| Source | Finding |
|---|---|
| NFHS 2015–16 (n-national) | Overall consanguineous marriage **9.9%**; **South region 23%**, Northeast 3.1% |
| NFHS 1992–93 | South India **34.7%** (26.2% close blood relatives, 8.5% distant) |
| Bittles et al., Karnataka | 29.29% consanguineous → **F = 0.0231** for the population |
| Karnataka, childhood genetic disorders | General population **F = 0.0271**; affected group F = 0.0414 |
| Karnataka 1980–89 | Bangalore **F = 0.0339**, Mysore **F = 0.0203** |
| Trends in consanguinity, South India | **"In Kerala, the frequency of consanguineous marriages is very low"** and uncle–niece marriage is "conspicuously absent." In the other South Indian states, consanguinity and F are high. |

Our fixture is **Kerala (n=100)** and **Chennai (n=50)** — the one South Indian
state with conspicuously low consanguinity, and a Tamil Nadu site in the
high-F region. That is a genuine per-site difference in expected homozygote
burden that has nothing to do with `planned_n`.

**The correction, if we implement it.** Under inbreeding with coefficient F,
homozygote frequency is not `q²` but:

```
f(aa) = q² + F·p·q          (homozygotes inflated)
f(Aa) = 2pq·(1 − F)         (heterozygotes deflated)
```

⚠️ Worked example below is **our own arithmetic**, not taken from a paper.
Using HapB3 at SAS `q = 0.012`, `p = 0.988`, and Karnataka `F = 0.0231`:

```
q²           = 0.012 × 0.012                 = 0.000144
F·p·q        = 0.0231 × 0.988 × 0.012         = 0.000274
q² + F·p·q                                    = 0.000418
```

**~2.9× the random-mating homozygote frequency.** This substantiates
METHOD.md's claim that our Poor Metabolizer estimate is "a floor, not a point
estimate" — and puts a number on it for the first time.

Two honest options, in preference order:

- **Do not implement it today.** Instead cite these numbers in METHOD.md so the
  caveat carries a magnitude and a source. Lower risk, and Tier 0 stays pure
  arithmetic over pinned inputs.
- If implemented, F must be a **declared per-site input with provenance**, never
  inferred from country code, and the output must be labelled Tier 1 (it needs
  an external parameter), *not* Tier 0.

Do not silently fold F into `diplotype_frequencies()`. That function's
defensibility comes from being pure Hardy-Weinberg with a sum-to-one test.

### 8.3 ⚠️ The delay-cost figure everyone cites is wrong — including ours

Widely quoted: clinical trial delays cost **$600,000–$8 million per day**. That
range appears across CRO and vendor marketing. **Tufts CSDD debunked it.**

The `$4–5 million per delay day` figure traces to 1993 estimates from the
Office of Technology Assessment and Boston Consulting Group, computed as a
1990s blockbuster's annual revenue ÷ 365. Tufts' October 2023 study analysed
**645 drugs and biologics** launched since 2000, inflated to 2023 USD:

| Metric | Corrected value |
|---|---|
| Lost prescription sales per delay day | **~$800,000** (not $4–5M) |
| Oncology median, per day | **$840,000** |
| Cardiovascular / hematology median | $1.4M / $1.3M |
| Trend | Declining **$80,000–$100,000 per year** |
| Direct cost to run a trial, per day (mean, Ph II–III) | **~$40,000** |
| Phase III direct cost per day | **$55,716** |
| Phase II direct cost per day | **$23,737** |
| Phase I / Phase IV | $7,829 / $14,091 |
| (Superseded Medidata figure) | $35,000/day, also ~30 years old |

Published in *Therapeutic Innovation & Regulatory Science*; see also
PMID 38773058.

**Use the corrected numbers.** For an oncology trial the honest framing is
**~$840,000/day in unrealised sales plus ~$55,716/day in direct Phase III
cost**. That is still a large number, it is current, and quoting it while
noting that the popular $4–5M figure is a 30-year-old artefact is itself a
demonstration of the discipline we are selling. Citing the inflated range in a
room that knows better would undercut the entire pitch.

### 8.4 CPIC scaling denominator, now sourced

`BUILD_HANDOFF.md` §6 says the scaling story is "one rule per CPIC Level A
pair, of which there are dozens." Now quantified:

- CPIC guidelines cover **34 genes and 164 drugs** — *"the global standard for
  translating pharmacogenomic test results into actionable prescribing
  decisions"* (PMID 40678821, 2025).
- Of 145 ADME-related drug–gene pairs in the CPIC database: **Level A 43 (30%)**,
  Level B 22 (15%), Level C 59 (41%), Level D 21 (14%) (PMID 36257916).
- A separate 2025 prescribing study identified **53 drugs** with CPIC Level A
  actionable pharmacogenetic variants (PMID 41017291).

So: **~43–53 Level A pairs** is the addressable rule count, against 34 genes and
164 drugs of guideline coverage. `pgx-core`'s 13 genes are ~38% of CPIC's gene
coverage. "Dozens" is right; now it has a citation and a denominator.

### 8.5 There is a standard for machine-readable protocols — align to it

This is the strongest available support for the "infrastructure everyone builds
on" claim (theme #5), and we were not aware of it.

**CDISC USDM** — Unified Study Definitions Model, produced by the
**Digital Data Flow (DDF)** initiative, the standard for exchanging structured
study definitions between clinical systems, aligned with **ICH M11** (the
harmonised electronic protocol template).

- **USDM v4.0** went to public review in 2025; **USDM Implementation Handbook
  v1.0 FINAL** published 2026 (CDISC).
- Includes a REST API architecture and a central Repository component "aimed at
  facilitating the exchange of structured study definitions across clinical
  systems."

`cohortfit`'s `Protocol` / `Site` / `DoseRegimen` model is an ad-hoc subset
invented for this build. That was correct for a five-hour sprint. But the
credible path from prototype to infrastructure is: **accept USDM/ICH M11 as an
input format**, so cohortfit slots into a pipeline sponsors and CROs are
already being pushed toward, instead of asking them to author our JSON.

Say this if asked "how does this get adopted?" It is a far better answer than
"an API". It also reframes the Claude extractor: its job is bridging *legacy
prose protocols* into structured form, while USDM handles the ones already
digital — which is exactly the transition the industry is mid-way through.

⚠️ Not verified: whether USDM has a native field for per-site expected ancestry
composition. If it does not, that is a gap worth naming out loud — the standard
would then have no slot for the input our whole computation depends on.

---

## 9. Action list

Ordered by value. None of it is large.

1. ~~**Fix the frequency provenance label** (§1.1).~~ **Done** — the module
   carrying the unverifiable label was deleted; the audit path reads
   `fixtures/frequencies/dpyd.json` (gnomAD v4.0, provenance enforced by the
   loader).
2. ~~**Reconcile `*13`** between docs and code (§1.2).~~ **Done** — the live
   fixture pins all four panel alleles.
3. ~~**Note `rs56038477` as a tagging variant** for `rs75017182` (§1.3).~~
   **Done** — the fixture pins the frequency from the causal `rs75017182` and
   records the label/frequency rsID split in each `HapB3` record's `notes`; see
   [DATA_PROVENANCE.md](DATA_PROVENANCE.md#hapb3-label-vs-frequency-rsid).
4. **Upgrade the regulatory claim** from "CPIC advises" to EMA 2020 /
   MHRA-NHS 2020 mandatory pre-treatment testing (§3).
5. **Replace the delay/failure cost with the corrected Tufts figures** (§8.3) —
   ~$840k/day oncology unrealised sales, $55,716/day Phase III direct cost,
   $141k/$535k per substantial amendment (§4). Explicitly do **not** cite
   $600k–$8M/day.
6. **Add BJC 2024 and Naushad 2021 to citations** (§2, §8.1) — the second
   validates our SAS proxy for DPYD specifically and independently corroborates
   the M166V finding from the override audit.
7. **Add the consanguinity magnitude to METHOD.md caveat #1** (§8.2). Cite F
   values and note Kerala vs Chennai differ. Do not fold F into the Tier 0
   engine.
8. ~~**Consider HapB3 as the first live `CONTESTED` finding** (§5).~~ **Done** —
   `rules.contested_burden()` raises it when a contested-dosing allele holds
   ≥60% of the cohort's actionable burden (79.3% on the demo cohort), citing
   PMID 37639651.
9. **Name CDISC USDM / ICH M11 as the adoption path** (§8.5).
10. **Drop FDA Diversity Action Plans** from any positioning material (§3).

---

## Appendix — sources retrieved 2026-08-08

- CPIC Fluoropyrimidines/DPYD guideline page — https://cpicpgx.org/guidelines/guideline-for-fluoropyrimidines-and-dpyd/
- CPIC 2017 update — PMID 29152729, *Clin Pharmacol Ther* 2018;103:210–216
- Chan, Zhang & Pirmohamed — *Br J Cancer* 131:498–514 (2024), DOI 10.1038/s41416-024-02754-z
- Henricks et al. — PMID 30348537, *Lancet Oncol* 2018
- Meulendijks et al. — PMID 26603945, *Lancet Oncol* 2015;16:1639–50
- Knikman et al. — PMID 37639651, *J Clin Oncol* 2023
- Hariprakash et al. — PMID 29239269, *Pharmacogenomics* 2018;19:227–41
- Naushad et al. — PMID 33105068, *J Gene Med* 2021
- dbSNP rs3918290 — https://www.ncbi.nlm.nih.gov/snp/rs3918290
- EMA Article 31 referral, fluorouracil and related substances (2020)
- MHRA Drug Safety Update, October 2020 — gov.uk
- NHS England urgent policy statement, DPYD polymorphisms (2020)
- ICH E17, MRCT general principles — EMA scientific guideline page
- Lancet SEA, India local-trial waivers — PIIS2772-3682(24)00151-3
- Tufts CSDD — *Ther Innov Regul Sci* (2024), DOI 10.1007/s43441-024-00622-9
- FDA Diversity Action Plans guidance page and "Withdrawn or Expired Clinical
  Trial Guidance Documents"
- ICON plc press release and coverage of the Anthropic collaboration

### Second pass

- Naushad et al. — PMID 33105068, *J Gene Med* 2021;23(1):e3289, n=2,000 Indians
- IndiGenomes — *Nucleic Acids Res* 2021;49(D1):D1225, 1,029 Indian genomes
- Chan et al. (SAS variant coverage) — *Br J Cancer* 2024, as §2
- Consanguinity: NFHS 2015–16 analysis (ResearchGate 342804303); NFHS 1992–93
  (PMID 12055694); Karnataka F values (PMID 7294724, PMID 3612707, PMID 8425878);
  Kerala exception (PMID 11284626)
- Tufts CSDD day-of-delay white paper (Aug 2024) and Getz & Smith summary,
  *Contract Pharma* 2024-09-05; PMID 38773058
- CPIC coverage — PMID 40678821 (34 genes / 164 drugs); PMID 36257916 (Level A
  43 of 145 ADME pairs); PMID 41017291 (53 Level A drugs)
- CDISC USDM v4.0 public review; USDM Implementation Handbook v1.0 FINAL (2026);
  CDISC Digital Data Flow / ICH M11 alignment materials
- Hardy–Weinberg with inbreeding: standard `q² + Fpq` formulation
  (Wright's F; Hardy–Weinberg principle, general population-genetics references)
