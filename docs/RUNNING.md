# Running cohortfit

Three ways to run the project: the **CLI** (fastest to a result), the **API**
(HTTP surface + Swagger docs), and the **web UI** (landing page + interactive
audit workbench). All of it runs **offline against pinned fixtures by default** —
no network, no API key — except optional Claude extraction.

## Prerequisites

- Python **3.11+**
- Node **18+** and npm (only for the web UI)
- The deterministic engine [`anukriti-pgx-core`](https://github.com/AnukritiAi-hq/anukriti-pgx-core)
  is pulled in automatically as a pinned dependency.

## Install

```bash
# from the repo root (cohortfit/)
python -m venv .venv && source .venv/bin/activate   # optional but recommended
pip install -e .            # core CLI only
pip install -e ".[web]"     # + API server (fastapi, uvicorn, httpx)
pip install -e ".[llm]"     # + Claude extraction (anthropic)
pip install -e ".[dev]"     # + pytest, ruff
# combine extras as needed, e.g.:
pip install -e ".[web,dev]"
```

## 1. CLI

```bash
cohortfit audit protocols/demo.json          # run the audit (offline, default)
cohortfit render fixtures/reports/sample_audit_report.json   # render a pinned report, no engine
cohortfit --help                             # all commands
```

`--offline` defaults to **on** — pinned fixtures only, no network. `--no-offline`
is intentionally rejected (live frequency lookups are not implemented).

Optional live extraction (needs `pip install -e ".[llm]"` and a key):

```bash
export ANTHROPIC_API_KEY=...
cohortfit extract protocols/sources/nct01095003.txt -o /tmp/out.json
```

## 2. API server

```bash
pip install -e ".[web]"
cohortfit serve --port 8600            # host defaults to 127.0.0.1
```

Then:

- **Swagger UI:** http://127.0.0.1:8600/docs
- **ReDoc:** http://127.0.0.1:8600/redoc
- **OpenAPI schema:** http://127.0.0.1:8600/openapi.json
- **Health:** http://127.0.0.1:8600/health

Full endpoint reference: [API.md](API.md). Quick smoke test:

```bash
curl http://127.0.0.1:8600/health
curl -X POST "http://127.0.0.1:8600/audit?offline=true" \
  -H "Content-Type: application/json" -d @protocols/demo.json
```

> **Port note.** `cohortfit serve` uses `uvicorn` with `reload=False`, so after
> changing Python source you must restart it. Pick any free port with `--port`;
> `8000` is a common default but may already be taken by another local service.

## 3. Web UI

The web app has two routes: the marketing landing at `/` and the interactive
audit workbench at `/app`. There are two ways to run it.

### 3a. Production / demo — one server, same origin (recommended)

Build the static bundle once, then let `cohortfit serve` serve both the API and
the UI from the same origin (no CORS, no proxy):

```bash
pip install -e ".[web]"
cd web && npm install && npm run build && cd ..
cohortfit serve --port 8600
```

Open:

- Landing: http://127.0.0.1:8600/
- Audit workbench: http://127.0.0.1:8600/app

The workbench opens **empty** — nothing is audited until you ask for it, so the
first report on screen is one you watched it compute. Pick a demo protocol card,
paste JSON, extract from prose, or click **Load sample report**; every one of
those runs a real request against the engine (`/fixtures/protocols`, `/audit`,
`/provenance/...`). Rebuild (`npm run build`) after any change under `web/` for
the served bundle to update.

### 3b. Development — hot-reloading Vite dev server

Two terminals:

```bash
# terminal 1 — API on port 8000 (the dev proxy target)
cohortfit serve --port 8000

# terminal 2 — Vite dev server with HMR
cd web
npm install
npm run dev
```

Open http://localhost:5173/ (landing) and http://localhost:5173/app (workbench).

> The Vite dev proxy forwards `/api/*` to `http://127.0.0.1:8000` (see
> `web/vite.config.ts`). The dev API server **must** run on port `8000`, and that
> port must be free — if another service holds it, audit calls will hit the wrong
> server and the UI will look inert. If `8000` is taken, either free it or use the
> same-origin production flow in 3a instead.

## Tests

```bash
pip install -e ".[dev]"
pytest                                   # full suite
pytest tests/test_catalogue.py -v        # API catalogue endpoints
pytest tests/test_audit.py tests/test_rules.py   # engine
```

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `/app` returns 404 when served statically | `web/dist` not built | `cd web && npm run build`, then restart `cohortfit serve` |
| UI loads but buttons do nothing (dev) | Nothing on the proxy target `:8000`, or a different service holds it | Start `cohortfit serve --port 8000`, or use flow 3a |
| `POST /extract` → 503 | `ANTHROPIC_API_KEY` not set | `export ANTHROPIC_API_KEY=...` and `pip install -e ".[llm]"` |
| Python changes not reflected in API | `serve` runs with `reload=False` | Restart `cohortfit serve` |
| `cohortfit serve` → "Web extras not installed" | Missing `[web]` extra | `pip install -e ".[web]"` |
