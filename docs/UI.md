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
| Demo (default) | Sample report fixture or one-click audit of `protocols/demo.json` |
| Upload JSON | Paste/upload Protocol JSON → `POST /audit` |
| Extract prose | Textarea → `POST /extract` → audit (503 without `ANTHROPIC_API_KEY`) |

## Security note

Do not deploy the extract endpoint publicly without authentication. The demo
returns 503 when no API key is configured.
