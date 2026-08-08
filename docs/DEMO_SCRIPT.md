# cohortfit — stage demo script

Minute-by-minute cues for the person at the laptop, **live on stage** — terminal
only, with a recovery cheatsheet for when something goes wrong in the room.

For the **recorded** submission video, which drives the web UI instead, use
[DEMO_VIDEO.md](DEMO_VIDEO.md).

Pitch narrative: [PITCH.md](PITCH.md)

**Pre-flight (5 min before):**

```bash
cd cohortfit
pip install -e .
cohortfit audit protocols/demo.json    # must exit 0
cohortfit --help
```

Terminal: large font, dark theme, `protocols/demo.json` path ready to paste if needed.

---

## Timeline (~3 min total)

| Time | Speaker | Laptop |
|---|---|---|
| 0:00–0:10 | Hook (verbatim from PITCH.md) | Terminal idle |
| 0:10–1:25 | Four dots (Dots 1→4, tightened — see below) | Terminal idle |
| 1:25–1:35 | Product one-liner | Clear screen optional |
| 1:35–3:25 | Demo talk track (below) | **Main demo** |
| 3:25–3:38 | Honest limits | Terminal idle |
| 3:38–3:50 | Close | Terminal idle |

The output now carries eight things to point at, not six. The demo talk track is
**110 seconds, not 90**. Take the extra 20 seconds out of the dots, in this order:

1. Dot 2 — drop the Coefficient Bio / John Jumper aside, keep the $2.1B number.
2. Dot 3 — drop the FAERS sentence. It is in the honest-limits beat anyway.

Both optional beats stay off unless the main demo lands under 3:00.
**Never cut the CONTESTED finding** — it is the strongest thing on screen.

---

## Main demo (primary path)

### Command

```bash
cohortfit audit protocols/demo.json
```

No flags. `--offline` is default. No wifi required.

### Point at screen — in order

This is the order the renderer prints. Do not jump ahead; the CONTESTED panel
lands *after* the phenotype table and it needs the table's numbers behind it.

1. **Header panel** — trial title, `NCT01095003`, `n=230`, `[offline]`
2. **First TIER 0 panel** — `ACTIONABLE`, CPIC Level A, missing DPYD exclusion text
3. **Panel-concentration note** (inside that panel) — `1.53 effective alleles; HapB3 carries 79.3% of actionable burden`
4. **Cohort phenotype table** — IM ~10.4 expected at n=230, and the **Range (provenance)** column: Normal 1.0×, Intermediate 1.4×, **Poor Metabolizer 3.7×**
5. **Second TIER 0 panel** — `CONTESTED`, same gene-drug pair, PMID 37639651
6. **Site burden table** — Munich first (~6.40% rate); Mumbai vs Kochi same rate
7. **Footnote** — read aloud: *"Mumbai and Kochi share SAS ancestry — delta is headcount only"*
8. **Coverage warning + data sources** — `*2A` SAS conflict, then gnomAD v4 fixture + CPIC diplotype table

### Speaker lines (while output is visible)

> "This is NCT01095003 — capecitabine, sites in India and Germany. Everything after protocol JSON is deterministic — pinned gnomAD, CPIC tables, no LLM in the math."

> "ACTIONABLE: fluoropyrimidine without DPYD screening. That's a real CPIC Level A gap."

*(new — panel concentration)*

> "And it tells you what the screen is actually made of. Four variants on paper; **1.53 effective alleles** for this cohort, with **79.3% of the burden on HapB3 alone**. That's a mixed South Asian and European cohort — pure South Asian, it's 1.12."

*(new — provenance range)*

> "Look at the Range column. Normal Metabolizer is flat. **Poor Metabolizer moves 3.7-fold** across the candidate frequencies for the disputed allele. We will not print that one as a point estimate — that's provenance uncertainty, not a confidence interval."

*(new — CONTESTED, the strongest beat; slow down here)*

> "Second finding, same gene-drug pair: **CONTESTED**. The burden sits on HapB3, and **CPIC's own guideline** flags that HapB3 carriers dosed at the standard 25% reduction showed reduced effectiveness and increased toxicity — PMID 37639651. So the protocol should screen, and for most screen-positives here a positive test has **no settled clinical response**. The tool refuses to resolve a dispute CPIC hasn't resolved — and it worked that out from the arithmetic, nobody wrote that sentence in."

> "Munich has a higher at-risk *rate* than Mumbai — ancestry, not headcount. Mumbai vs Kochi: same ancestry, so Mumbai expects twice the at-risk *count*."

> "Bottom: the tool naming the one number it doesn't trust, and every source it used."

---

## Optional beat A — tier styling (~30 sec)

Only if main demo finished under 2:30.

```bash
cohortfit render fixtures/reports/sample_audit_report.json
```

Say:

> "Same renderer — Tier 0 arithmetic, Tier 1 requires a PMID, Tier 2 is labelled scenario, not prediction."

Point at yellow TIER 1 citation line and dim SCENARIO panel.

---

## Optional beat B — live extraction (~45 sec, risky)

**Rehearse once backstage.** Skip if wifi or API key uncertain.

```bash
export ANTHROPIC_API_KEY=...   # set before stage
cohortfit extract protocols/sources/nct01095003.txt -o /tmp/extracted.json
head -20 /tmp/extracted.json
```

Say:

> "Claude reads unstructured prose. Pydantic validates before any math. We run the audit from hand-verified pinned JSON for the numbers demo."

**If it fails:**

> "Validation caught malformed output — that's the boundary working. Here's the verified fixture."

Then:

```bash
cohortfit audit protocols/demo.json
```

---

## Do not run on stage

| Command | Why |
|---|---|
| `--no-offline` | Errors by design |
| `pytest` | Not a judge demo |
| Live gnomAD / network fetch | Not implemented |
| Unrehearsed PDF upload | Extraction scope is `.txt` fixture |

---

## Split roles (2-person team)

| Role | Owns |
|---|---|
| **Speaker** | Hook, four dots, Q&A |
| **Driver** | Pre-flight, `audit` command, point-at-screen cues |

Driver does not explain architecture unless speaker hands off.

---

## Recovery cheatsheet

| Problem | Fix |
|---|---|
| Command not found | `pip install -e .` in repo root |
| Red error on audit | `cohortfit audit protocols/demo.json` from repo root |
| Terminal too small | Zoom in; re-run audit |
| Judge asks "is this live?" | "Audit is offline pinned fixtures. Extract is optional Claude layer." |
| Judge asks SAS/EUR direction | "For this CPIC allele panel, EUR > SAS — documented in DATA_PROVENANCE.md" |
| Judge says "the docs say 94.2%, the screen says 79.3%" | "Different cohorts. 94.2% and 1.12 alleles are pure South Asian. The demo cohort is 150 South Asian plus 80 European, so it blends to 79.3% and 1.53. Both come out of the same function." |
| Judge asks "why two findings on one pair?" | "They say different things. One says the protocol should test. The other says a positive test has no settled dose action for most of this cohort. Folding the second into the first would bury it." |

---

## Post-demo

Leave terminal on last successful audit output for judge walk-up.

Offer: `docs/DATA_PROVENANCE.md` for every pinned number.
