# Demo video — recording script

For the **recorded** Devfolio submission. The live stage version is
[DEMO_SCRIPT.md](DEMO_SCRIPT.md) and it is terminal-only; this one drives the web
UI, because a recording gets watched without you in the room to explain it.

**Target: 2:45–3:00.** Every number below was verified against a live run before
this file was written. If a number on screen disagrees with a number here, the
script is wrong — re-check before re-recording.

---

## Pre-flight

```bash
cd web && npm run build && cd ..
pip install -e ".[web]"
cohortfit serve --port 8600
```

Open `http://127.0.0.1:8600/`. Second tab: a terminal in the repo root.

Checklist before you hit record:

- [ ] Browser zoom **125%**, window 1920×1080, no bookmarks bar, no extensions
- [ ] Terminal: large font, dark theme, cleared
- [ ] `/app` loads and shows the **empty** workbench (this is correct — it audits nothing until asked)
- [ ] Notifications off, phone silent
- [ ] Mic test — one sentence, play it back

No `ANTHROPIC_API_KEY` needed. Nothing here touches the network.

---

## Shot list

### 0:00–0:18 · Hook, on the landing hero

**Screen:** `/` at the top. Let the DNA helix rotate once before you speak.

> "Every trial protocol has an implicit genome it was written for. Nobody checks
> whether the patients you're actually enrolling have it."

> "A protocol's dose is calibrated on a largely European population. Run it at
> Indian sites and a computable fraction of your enrollees can't metabolise it
> safely."

### 0:18–0:38 · The ancestry mixer — the thesis in one control

**Screen:** drag the mixer slider from 100% South Asian to 0% and back. Slowly.

> "That fraction is a number, and it moves with where you enrol. Six-point-four
> percent at a European site, three-point-five-five at a South Asian one — same
> protocol, same drug."

> "cohortfit computes that before a single patient is enrolled."

*(Say nothing about the helix. It's decorative and a judge will assume it isn't.)*

### 0:38–0:50 · Into the workbench

**Screen:** click **Open app** / navigate to `/app`. Land on the empty state.

> "Four pinned protocols, each one exercising a different path through the
> engine. Nothing is audited until I ask for it."

### 0:50–1:45 · Card 1 — the headline audit

**Screen:** click the **demo** card (*"Site selection changes expected burden"*).
Report renders. Scroll slowly, pausing on each item.

> "NCT01095003 — capecitabine, two Indian sites and Munich. **ACTIONABLE**: CPIC
> Level A fluoropyrimidine pair, and this protocol never screens for DPYD
> deficiency."

Pause on the panel-concentration note.

> "It also tells you what the screen is made of. Four variants on paper —
> **1.53 effective alleles** for this cohort, with **79.3% of the burden on
> HapB3 alone**."

Pause on the phenotype table.

> "Ten-point-four expected intermediate metabolizers at n=230. And look at the
> Range column — Normal Metabolizer is flat, **Poor Metabolizer moves 3.7-fold**
> across the candidate frequencies for the one allele whose provenance we
> dispute. We won't print that as a point estimate."

Pause on the second finding. **Slow down here — this is the strongest beat.**

> "Second finding, same gene-drug pair: **CONTESTED**. The burden sits on HapB3,
> and CPIC's own guideline flags that HapB3 carriers dosed at the standard 25%
> reduction showed reduced effectiveness *and* increased toxicity — PMID
> 37639651. So the protocol should screen, and for most screen-positives here a
> positive test has **no settled clinical response**."

> "The tool refuses to resolve a dispute CPIC hasn't. It worked that out from the
> arithmetic — nobody wrote that sentence in."

Pause on the site burden table.

> "Munich has a higher at-risk *rate* than Mumbai — ancestry, not headcount.
> Mumbai and Kochi share ancestry, so same rate, twice the count."

### 1:45–2:05 · Card 4 — it doesn't always accuse

**Screen:** click the **dpyd-screened** card (*"It does not simply always accuse"*).

> "Same drug, same ancestry — but this protocol screens DPYD per the EMA 2020
> label requirement. **NO_SIGNAL.** The rule is a real discriminator, not a
> rubber stamp."

> "CONTESTED still stands, and that's correct: screening closes the gap, it
> doesn't settle the dose."

### 2:05–2:25 · Card 3 — it reports what it cannot compute

**Screen:** click the **us-multiancestry** card. Scroll to the coverage note.

> "A US cohort. We've pinned South Asian and European frequencies — not African
> or American. So **35% of declared enrolment is excluded, and the report says
> so**."

> "Without that line the output would be indistinguishable from a fully-covered
> cohort — it still sums to one. This is the honesty demonstration, and it
> matters more than any accuracy claim."

### 2:25–2:40 · Not canned — paste your own

**Screen:** **Paste Protocol JSON** tab. Paste a protocol with the ancestry mix
edited (e.g. Mumbai flipped to `{"EUR": 1.0}`). Click **Audit protocol**.

> "Not a canned response — paste any protocol and the numbers move. Same engine,
> same schema as the CLI."

### 2:40–3:00 · The receipt, and close

**Screen:** cut to terminal.

```bash
cohortfit audit protocols/demo.json
```

> "Same audit, offline, no API key."

Then, while it's on screen:

```bash
curl -s http://127.0.0.1:8600/provenance/DPYD | head -40
```

> "And every number traces. gnomAD v4.0 with the raw counts — HapB3 in South
> Asians is 1,538 copies in 91,072 alleles. Claude extracts the protocol.
> Everything after that is arithmetic on pinned tables."

> **"The deterministic layer decides. The model explains. Never the reverse."**

---

## Do not put on camera

| Thing | Why |
|---|---|
| `--no-offline` | Errors by design; reads as a bug on video |
| `pytest` | Nobody watches a test run |
| Live `cohortfit extract` | Needs a key and the network. Mention it; don't film it |
| The `/app` empty state without narrating it | Reads as broken |
| The WebGL helix as a feature | It's decorative. Claiming otherwise invites the one question you can't win |

## If you have 30 more seconds

Add the **capecitabine-india** card between cards 1 and 4:

> "Pure South Asian cohort: **1.12 effective alleles**, HapB3 at **94.2%**. The
> panel is marketed as four variants. For this population it's one variant and
> three that almost never fire — and Poor Metabolizer spans **21.4-fold**."

## Voiceover notes

- Record audio separately if you can. Screen-capture mic audio is the single
  most common reason a good demo reads as amateur.
- Two takes minimum. The CONTESTED beat is worth a third.
- Don't fill silence. Let the report sit on screen for a second after each claim.
- Say **"expected"** and **"distribution"**, never "predicts". The tier contract
  is the product; contradicting it in the voiceover undoes it.
