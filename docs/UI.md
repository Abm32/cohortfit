# Web UI

Browser UI over pinned or live `AuditReport` JSON. The UI and API **never**
compute fractions, phenotypes, verdicts, or tier assignments — they only format
and display values already present in the report.

## Architecture

```
Protocol JSON / fixture ──▶ POST /audit ──▶ audit_protocol() ──▶ AuditReport JSON
                                                                    │
Sample fixture ──▶ GET /fixtures/reports/sample ────────────────────┤
                                                                    ▼
                                                          React components (display only)
```

Shared formatters live in:

- Python: `src/cohortfit/display.py` (CLI + API)
- TypeScript: `web/src/display.ts` (golden parity in `web/src/display.test.ts` vs `tests/test_display.py`)

## Data contract

The UI renders fields from `AuditReport` as defined in `src/cohortfit/models.py`:

| Component | JSON fields |
|---|---|
| ReportHeader | `protocol_title`, `trial_id`, `total_planned_n`, `offline` |
| WarningsBanner | `warnings[]` (always visible) |
| FindingCard | `findings[]` — tier sub-layouts 0/1/2 |
| SiteBurdenPanel | `site_findings[]` sorted by `at_risk_fraction` desc |
| DataSourcesPanel | `data_sources[]`, citation PMIDs |
| ProvenancePanel | `GET /provenance/{gene}` on expand (read-only fixture metadata) |

### Display-only derivations (allowed)

- `format_fraction` / `format_expected_n` — mirror CLI rounding rules
- Sort `site_findings` by existing `at_risk_fraction`
- `planned_n` via `round(expected_at_risk_n / at_risk_fraction)` when fraction > 0
- PubMed URLs from PMIDs

## Local development

```powershell
# Terminal 1 — API
pip install -e ".[web,dev]"
cohortfit serve --port 8000
```

```powershell
# Terminal 2 — Vite dev server (proxies /api → uvicorn)
cd web
npm install
npm run dev
```

Open http://localhost:5173 — default tab loads `GET /fixtures/reports/sample`.

## Production single-process demo

```powershell
cd web
npm install
npm run build
cd ..
pip install -e ".[web]"
cohortfit serve --port 8000
```

Uvicorn serves `web/dist` at `/` when the build directory exists; API routes
(`/audit`, `/fixtures/*`, etc.) are registered first.

## Input paths

| Tab | Path |
|---|---|
| Demo (default) | **Dataset cards** — pick one of four pinned protocols → `POST /audit`. Below them, the sample-report fixture (the only way to see Tier 0/1/2 styling side by side) |
| Upload JSON | Paste/upload Protocol JSON → `POST /audit` |
| Extract prose | Textarea → `POST /extract` → audit (503 without `ANTHROPIC_API_KEY`) |

### Dataset cards

[`DatasetCards.tsx`](../web/src/components/DatasetCards.tsx) renders
`GET /fixtures/protocols` as a responsive grid. Each card shows what its fixture
demonstrates, the cohort shape, and the verdicts to expect; clicking it fetches
the protocol by slug and audits it.

**The catalogue is served, not hardcoded.** The `demonstrates` / `detail` /
`expect` strings live in
[`api/routes/fixtures.py`](../src/cohortfit/api/routes/fixtures.py) beside the
files they describe, because a card claiming `NO_SIGNAL` on a protocol that
returns `ACTIONABLE` is a false claim rendered on screen — the exact defect this
project exists to catch. `tests/test_catalogue.py` runs every catalogued protocol
through the real engine and asserts each card's promise against the result, so
that drift fails in CI rather than on stage. It has already caught one: the demo
card claimed `ACTIONABLE` when the protocol also returns `CONTESTED`.

The left accent bar is derived from `expect`, so a card previews the shape of its
own result before it is clicked:

| Accent | Meaning |
|---|---|
| Green (`--forest-bright`) | `ACTIONABLE` |
| Amber | `CONTESTED` |
| Ochre | Coverage warning |
| Mint (`--mint-dim`) | `NO_SIGNAL` |

That preview is why the tab shows four fixtures rather than one: the *set*
demonstrates the engine discriminates instead of always accusing. See
[DATASETS.md](DATASETS.md) for what each fixture is for.

Accessibility: cards are `<button>` elements inside a `<ul>`, carry
`aria-busy` while auditing, keep a visible focus ring, and drop the hover
transform under `prefers-reduced-motion`.

## Fixture endpoints

| Endpoint | Returns |
|---|---|
| `GET /fixtures/protocols` | Catalogue for the cards. Internal `file` field is stripped |
| `GET /fixtures/protocols/{slug}` | One protocol. 404 lists the known slugs. `demo` still resolves, so pre-card clients keep working |
| `GET /fixtures/reports/sample` | Pinned `AuditReport` with Tier 0/1/2 findings |
| `GET /fixtures/reports/partial-coverage` | `AuditReport` exercising the partial-ancestry UI state |

Slugs: `demo`, `capecitabine-india`, `us-multiancestry`, `dpyd-screened`.

`POST /audit` takes a **bare `Protocol` body** — not wrapped in a
`{"protocol": ...}` envelope.

## Security note

Do not deploy the extract endpoint publicly without authentication. The demo
returns 503 when no API key is configured.
