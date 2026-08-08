# cohortfit — pitch script

**Event:** Push to Prod (Anthropic × Elevation Capital × Mesa), Bengaluru, 2026-08-08  
**Target length:** ~3 minutes spoken  
**Demo:** `cohortfit audit protocols/demo.json` (offline, pinned)

Stage cues and exact commands: [DEMO_SCRIPT.md](DEMO_SCRIPT.md)

---

## Hook (~10 sec)

> **Every trial protocol has an implicit genome it was written for. Nobody checks whether the patients you're actually enrolling have it.**

Pause. Then the four dots.

---

## Four dots (~90 sec total)

Deliver in this order. Each dot ends with a bridge into the next.

### Dot 1 — ICON / Anthropic: operational, not scientific (~20 sec)

> Anthropic's clinical-trial partner **ICON** says enrolment delays hold up **up to 80% of trials**. Their words: *"the barrier to getting medicines to patients faster is operational, not scientific."*
>
> The bottleneck isn't discovering molecules. It's running trials — finding the right patients, at the right sites, on a dose written for a population you aren't actually enrolling.

**Bridge:** *"So where is the AI money going?"*

---

### Dot 2 — Isomorphic $2.1B: chasing molecules, not trial operations (~20 sec)

> **Isomorphic Labs** raised **$2.1B in May 2026** for AI-first drug *design*. Almost nobody is building for the **eighteen months** a trial loses waiting for patients — or discovering mid-enrolment that the protocol's dose doesn't match the cohort's metabolism.

**Bridge:** *"And regulators are starting to require an answer upfront."*

---

### Dot 3 — India / Japan / China: filing requirement, not nice-to-have (~25 sec)

> **Japan and China** mandate local testing or foreign-data ethnic-sensitivity analysis. **India's** waiver of local trials is [actively contested](https://www.thelancet.com/journals/lansea/article/PIIS2772-3682(24)00151-3/fulltext) on exactly these grounds: *does this dose hold in a South Asian cohort?*
>
> That's moving from a slide in the ethics appendix to a **regulatory deliverable**.
>
> And if the dose is wrong, postmarket surveillance won't save you — in FAERS, South Asia reports at roughly **1% of its population-proportional rate** (1.3M cases). The mismatch is invisible after the fact.

**Bridge:** *"We didn't wait to invent the hard part."*

---

### Dot 4 — You already own the deterministic engine (~25 sec)

> We ship on **[anukriti-pgx-core](https://github.com/AnukritiAi-hq/anukriti-pgx-core)** — pinned CPIC tables, 13 genes, no runtime API calls to CPIC.
>
> **Claude extracts the protocol. Everything after that is arithmetic.** No LLM estimates a frequency. Tier 0 is pinned gnomAD + Hardy–Weinberg + CPIC phenotype tables. **128 tests**, offline by default.
>
> If the renderer prints Tier 0 and Tier 2 in identical styling, the contract collapses — so every claim carries a tier label.

**Bridge:** *"Here's what that looks like on a real fluoropyrimidine trial."*

---

## Product one-liner (~10 sec)

> **cohortfit** reads a trial protocol and computes the pharmacogenomic phenotype distribution of the cohort that protocol will *actually* recruit — given the ancestry mix of its planned sites — plus missing PGx screening gaps and per-site metabolic burden.

---

## Live demo talk track (~90 sec)

Run: `cohortfit audit protocols/demo.json`

| Moment | Say |
|---|---|
| Header | "NCT01095003 — capecitabine in advanced breast cancer. Mumbai, Kochi, Munich. **Offline** — pinned fixtures, no venue wifi." |
| ACTIONABLE | "**ACTIONABLE** — CPIC Level A fluoropyrimidine pair, and this protocol never excludes or screens for DPYD deficiency. PMID on screen." |
| Tier 0 table | "Tier 0 — expected intermediate and poor metabolizers for the *actual* enrolment-weighted mix. Not the implicit European default." |
| Site burden | "Site selection: Munich ~**6.4%** at-risk *rate*. Mumbai and Kochi share South Asian ancestry — **same rate**, Mumbai expects twice the count because it's enrolling twice as many patients. Say that before a judge notices." |
| Close demo | "Same engine a CRO would run before first patient in." |

**Optional (if time + tier demo):**  
`cohortfit render fixtures/reports/sample_audit_report.json` — show Tier 1 with required citation and Tier 2 labelled SCENARIO.

**Optional (risky, once only):**  
`cohortfit extract protocols/sources/nct01095003.txt -o /tmp/out.json` — then: *"Pydantic validates before any math. Main demo uses hand-verified pinned JSON."*

---

## Honest limits (~15 sec)

> Prototype. **Tier 0 is load-bearing** — pinned, tested, reproducible. Tier 1/2 are directional. We demo DPYD × capecitabine deeply; we show **CONTESTED** when literature genuinely disagrees instead of picking a number.
>
> And the tool reports its own gaps. Only SAS and EUR frequencies are pinned, so a US cohort prints a **coverage warning** naming the 32% of enrolment it could not compute rather than quietly returning European numbers. The one pinned value we don't trust — SAS `*2A` from the exome callset — carries a runtime warning with the direction of the error. Every number is either defensible or flagged.

---

## Close (~15 sec)

> cohortfit is **genomic feasibility auditing for clinical trial protocols** — the operational layer ICON says the industry needs, built on the deterministic engine we already ship.
>
> **The deterministic layer decides. The model explains. Never the reverse.**

---

## Judge Q&A crib sheet

| Question | Answer |
|---|---|
| Why not just use ChatGPT? | LLM only extracts structure. Every frequency is pinned gnomAD + CPIC — reproducible offline. |
| Is 27% DPYD in Indians real? | We **exclude** *9A/M166V from Tier 0 (CPIC Normal). SAS at-risk for the CPIC panel is ~**3.5%** — see [DATA_PROVENANCE.md](DATA_PROVENANCE.md). |
| Why capecitabine? | CPIC Level A, common in oncology, missing DPYD screening is a real protocol gap — ACTIONABLE is honest. |
| What's the business? | CRO site selection + protocol amendment before FPI — metabolic burden per site before enrolment spend. |
| Claude dependency? | Extraction only. `cohortfit audit` runs from JSON with zero API key. |
| Why Munich > Mumbai on rate? | CPIC-panel EUR allele frequencies yield ~6.4% vs ~3.5% SAS at-risk — honest direction for this allele set. |
| Isn't DPYD screening just a CPIC suggestion? | No — **EMA (Apr 2020)** and **MHRA/NHS England (2020)** require pre-treatment DPD testing; treatment is *contraindicated* in known complete deficiency. A capecitabine protocol with no DPYD criterion is inconsistent with the approved EU/UK label, not merely off-guideline. |
| How does this get adopted? | Accept **CDISC USDM** / **ICH M11** — the machine-readable protocol standard (USDM v4.0 public review 2025, Implementation Handbook v1.0 2026). We slot into a pipeline sponsors and CROs are already being pushed toward. Claude's job is bridging *legacy prose* protocols during that transition. |
| Is your SAS proxy trustworthy? | For DPYD, checked: **Naushad 2021, n=2,000 Indians** found Indian and South Asian DPYD profiles cluster together (Level 1A combined MAF 1.889%). It does **not** generalise — the IndiGenomes pilot found a 34.2% gap on CYP2C9 `*2`. |
| So you'd tell them to cut the dose? | Not for HapB3. **CPIC's own guideline page** flags PMID 37639651: HapB3 carriers on a 25% reduction showed possible *reduced effectiveness* and increased toxicity. That is a real `CONTESTED` case, and HapB3 dominates our IM bucket. |
| Any number you don't trust? | Yes, and it's in the repo: SAS `*2A` is pinned from gnomAD **exomes** at 0.0005 while every genome-based source says 0.003–0.008. `*2A` is a splice-donor variant where exome capture is unreliable. Logged as `_meta.known_discrepancies`, warned at runtime, direction stated (our PM estimate is conservative). |
| What's the cost of getting this wrong? | Tufts CSDD: a substantial amendment is **$141k (Ph II) / $535k (Ph III)**, 76% of protocols need one, and a delay day is **~$840k** unrealised oncology sales + **$55,716** direct Ph III cost. (The popular $600k–$8M/day figure is a 1993 artefact Tufts revised down — we don't cite it.) |
| What did you build today? | Tier 0 audit pipeline, tier-aware renderer, Claude extractor, population-coverage warnings, 128 tests, ruff clean — see repo commits. |

---

## Devfolio blurb (copy-paste)

**One-liner:** Genomic feasibility auditing for clinical trial protocols — compute the PGx phenotype distribution of the cohort you will actually recruit.

**Problem:** Up to 80% of trials are delayed by enrolment (ICON). $2.1B chases molecule design (Isomorphic); almost nothing addresses whether the protocol dose matches the sites' ancestry mix. India/Japan/China are making ethnic sensitivity a filing requirement.

**Solution:** Claude extracts protocol structure; a deterministic engine (pinned gnomAD + CPIC via anukriti-pgx-core) computes cohort phenotype distribution, screening gaps, and per-site metabolic burden — offline, tier-labelled, 128 tests.

**Demo:** `cohortfit audit protocols/demo.json`
