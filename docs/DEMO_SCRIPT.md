# cohortfit — stage demo script

Minute-by-minute cues for the person at the laptop.  
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
| 0:10–1:40 | Four dots (Dots 1→4) | Terminal idle |
| 1:40–1:50 | Product one-liner | Clear screen optional |
| 1:50–3:20 | Demo talk track (below) | **Main demo** |
| 3:20–3:35 | Honest limits | Terminal idle |
| 3:35–3:50 | Close | Terminal idle |

Adjust dots shorter if running long — **never cut the demo**.

---

## Main demo (primary path)

### Command

```bash
cohortfit audit protocols/demo.json
```

No flags. `--offline` is default. No wifi required.

### Point at screen — in order

1. **Header panel** — trial title, `NCT01095003`, `n=230`, `[offline]`
2. **TIER 0 panel** — `ACTIONABLE`, CPIC Level A, missing DPYD exclusion text
3. **Cohort phenotype table** — IM ~10.4 expected at n=230
4. **Site burden table** — Munich first (~6.40% rate); Mumbai vs Kochi same rate
5. **Footnote** — read aloud: *"Mumbai and Kochi share SAS ancestry — delta is headcount only"*
6. **Data sources** — gnomAD v4 fixture + CPIC diplotype table

### Speaker lines (while output is visible)

> "This is NCT01095003 — capecitabine, sites in India and Germany. Everything after protocol JSON is deterministic — pinned gnomAD, CPIC tables, no LLM in the math."

> "ACTIONABLE: fluoropyrimidine without DPYD screening. That's a real CPIC Level A gap."

> "Tier 0 — the phenotype mix you'd actually enrol, given these sites' ancestry."

> "Munich has a higher at-risk *rate* than Mumbai — ancestry, not headcount. Mumbai vs Kochi: same ancestry, so Mumbai expects twice the at-risk *count*."

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

---

## Post-demo

Leave terminal on last successful audit output for judge walk-up.

Offer: `docs/DATA_PROVENANCE.md` for every pinned number.
