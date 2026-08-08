# Sample datasets — what to run, and where real protocols come from

Five fixtures, each chosen to exercise a *different* path through the engine. Run
them in this order and the tool has demonstrated its whole contract without
anyone having to take a claim on trust.

| # | Fixture | Cohort | Demonstrates |
|---|---|---|---|
| 1 | `protocols/demo.json` | 230, IN + DE | `ACTIONABLE` + the site-selection delta (Munich 6.40% vs Mumbai 3.55%) |
| 2 | `protocols/capecitabine_india.json` | 150, 100% SAS | `ACTIONABLE` + `CONTESTED`, the HapB3 concentration story |
| 3 | `protocols/us_multiancestry.json` | 200, US | **Coverage warning** — 35% of enrolment has no pinned data |
| 4 | `protocols/dpyd_screened_compliant.json` | 150, IN + DE | **`NO_SIGNAL`** — the tool does not simply always accuse |
| 5 | `protocols/sources/gastric_adj_2026.txt` | 360, IN/BD/DE | **Claude extraction** from prose (needs `ANTHROPIC_API_KEY`) |

## Why each one is in the set

**1. `demo.json`** — the headline number. Two Indian sites plus Munich, so the
at-risk *rate* diverges on ancestry (6.40% vs 3.55%, ratio 1.80×) while expected
counts also reflect headcount. This is the commercial argument: site selection
changes expected metabolic burden, computable before enrolment.

**2. `capecitabine_india.json`** — 100% SAS, no DPYD screening. Produces both an
`ACTIONABLE` finding and a second `CONTESTED` finding, because HapB3 carries
94.2% of this cohort's actionable burden and CPIC's dose action for HapB3 is
disputed (PMID 37639651). The strongest scientific claim the tool makes.

**3. `us_multiancestry.json`** — Houston and Chicago with EUR/AFR/AMR mixes. Only
SAS and EUR frequencies are pinned, so **35% of declared enrolment is dropped**
and the report says so: *"35% of declared enrolment (AFR 17%, AMR 18%) has no
pinned frequency data and was excluded."* Without that warning the output would
be indistinguishable from a fully-covered cohort — it still sums to 1.0. This is
the honesty demonstration, and it is more persuasive than any accuracy claim.

**4. `dpyd_screened_compliant.json`** — same drug, same ancestry mix as #2, but the
criteria reference DPYD genotyping per EMA 2020 and exclude complete deficiency.
Verdict flips to **`NO_SIGNAL`**. Without this fixture a reviewer can reasonably
suspect the rule always fires; with it, the screening-gap check is shown to be a
real discriminator. Note it also still raises `CONTESTED`, which is correct: the
protocol screens, but a positive screen for HapB3 still has no settled response.

**5. `gastric_adj_2026.txt`** — realistic protocol prose, four sites across three
countries, written so nothing is trivially parseable. Site ancestry is *not*
stated in the text, so it exercises `ancestry.py`'s country-code priors
(IN → SAS, DE → EUR; **BD is not in the prior table**, so Dhaka should surface as
a site with no ancestry mix — a real gap, honestly reported).

## Running them

```bash
# Offline, no API key, no network
cohortfit audit protocols/demo.json --offline
cohortfit audit protocols/capecitabine_india.json --offline
cohortfit audit protocols/us_multiancestry.json --offline
cohortfit audit protocols/dpyd_screened_compliant.json --offline

# Tier contrast (0/1/2 side by side) from a pinned report
cohortfit render fixtures/reports/sample_audit_report.json

# Live Claude extraction — demo once, early, then go offline
export ANTHROPIC_API_KEY=...
cohortfit extract protocols/sources/gastric_adj_2026.txt -o /tmp/gastric.json
cohortfit audit /tmp/gastric.json --offline
```

Via the API (`uvicorn cohortfit.api.app:app`): `POST /audit` takes a bare
`Protocol` body — **not** wrapped in a `{"protocol": ...}` envelope.

## Where real protocols come from

Everything above is hand-authored, which is deliberate: a pinned fixture is how
you test an extractor, because you have hand-verified expected output to diff
against. For real inputs:

- **ClinicalTrials.gov** — `https://clinicaltrials.gov/api/v2/studies/{NCT_ID}`
  returns JSON including `eligibilityModule.eligibilityCriteria` (free text),
  `armsInterventionsModule`, `contactsLocationsModule.locations`, and
  `designModule.enrollmentInfo.count`. Everything `Protocol` needs except
  ancestry mix. `protocols/sources/nct01095003.txt` is a real export.
- **CTRI (India)** — `ctri.nic.in`, no public API; the CTRI landscape analysis
  (PMC11096683) counted 1,988 registered cancer trials.
- **EU CTIS** — `euclinicaltrials.eu`, structured protocol data.
- **CDISC USDM / ICH M11** — the machine-readable protocol standard. The right
  long-term input format (see `EVIDENCE.md` §8.5), and the reason the extractor
  is a bridge rather than the product.

**Ancestry mix is the one field no registry provides.** ClinicalTrials.gov gives
site *locations*, never expected ancestry composition, and our USDM search found
demographics only in CDASH/SDTM `DM` collected-subject terminology — i.e. after
enrolment, not in the study definition. `ancestry.py` fills it from country
codes, and that assumption is explicit and inspectable rather than inferred
silently. It is also a genuine gap in the standards worth naming out loud.

## Caveats to state, not hide

- Ancestry mixes in these fixtures are **plausible assumptions, not
  measurements**. `METHOD.md` caveat 3 says so.
- Trial IDs on fixtures 3 and 4 are real NCT numbers used for realism; the
  protocol contents are **authored for this demo** and do not reproduce those
  trials.
- Only DPYD × fluoropyrimidines resolves to a gene. A protocol with any other
  drug correctly produces no findings.
