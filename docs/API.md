# cohortfit HTTP API

The API is the **presentation layer** over the deterministic engine. It exposes
the same audit that the CLI runs, plus read-only fixtures for the web UI and an
optional Claude extraction endpoint.

- **Interactive docs (Swagger UI):** `http://<host>:<port>/docs`
- **Alternative docs (ReDoc):** `http://<host>:<port>/redoc`
- **Machine-readable schema:** `http://<host>:<port>/openapi.json`

Every endpoint is annotated in code (`summary`, `description`, `response_model`,
error `responses`, request examples), so the pages above are the canonical,
always-current reference. This file is the human-readable companion.

> **The boundary is the contract.** `POST /extract` is the only endpoint that
> touches an LLM, and it only produces a `Protocol`. `POST /audit` computes every
> number deterministically from pinned gnomAD/CPIC tables. No verdict or fraction
> is ever produced by a model.

## Running the API

```bash
pip install -e ".[web]"          # fastapi + uvicorn + httpx
cohortfit serve --port 8600      # serves the API and (if built) the web UI
```

If `web/dist` exists (after `cd web && npm run build`), the same server also
serves the marketing landing at `/` and the audit workbench at `/app`, so the UI
and API are same-origin — no CORS, no proxy. See [RUNNING.md](RUNNING.md).

## Conventions

- All responses are JSON.
- Errors use a single envelope: `{ "detail": "<human-readable message>" }`.
  Validation failures (`422`) may instead return `{ "detail": [ ...pydantic errors... ] }`.
- `AuditReport` and `Protocol` schemas mirror `src/cohortfit/models.py` exactly
  and are rendered in full in Swagger UI.

---

## Endpoints

### `GET /health` — liveness probe

Returns `{ "status": "ok" }` when the service is up. No parameters.

```bash
curl http://127.0.0.1:8600/health
```

---

### `POST /audit` — run the deterministic audit engine

The core endpoint. Takes a structured `Protocol`, returns the computed
`AuditReport` (tiered gene-drug findings, per-site metabolic burden, provenance
warnings, and the pinned data sources every number came from).

**Query parameters**

| Name | Type | Default | Description |
|---|---|---|---|
| `offline` | bool | `true` | Run against pinned fixtures only. Live frequency lookups are not implemented; the flag is echoed back on the report for transparency. |

**Request body:** `Protocol` (see schema in Swagger). Minimal shape:

```json
{
  "trial_id": "NCT01095003",
  "title": "Vinflunine Plus Capecitabine in Advanced Breast Cancer",
  "drugs": [{ "drug": "capecitabine", "dose": "1250 mg/m² twice daily", "route": "oral" }],
  "sites": [
    { "name": "Mumbai", "country": "IN", "planned_n": 100, "ancestry_mix": { "SAS": 1.0 } },
    { "name": "Munich", "country": "DE", "planned_n": 80,  "ancestry_mix": { "EUR": 1.0 } }
  ]
}
```

```bash
curl -X POST "http://127.0.0.1:8600/audit?offline=true" \
  -H "Content-Type: application/json" \
  -d @protocols/demo.json
```

**Responses**

| Status | Body | Meaning |
|---|---|---|
| `200` | `AuditReport` | Audit succeeded. |
| `422` | `ErrorResponse` | The protocol body failed schema validation. |

---

### `POST /extract` — prose → `Protocol` via Claude

Converts unstructured protocol text into a validated `Protocol`. Claude extracts
structure only (drugs, criteria, sites, enrolment); it never estimates a
frequency or phenotype. **Requires `ANTHROPIC_API_KEY` on the server.**

**Request body**

| Field | Type | Default | Description |
|---|---|---|---|
| `prose` | string | — (required) | Protocol text or ClinicalTrials.gov export. |
| `model` | string | `claude-sonnet-4-20250514` | Anthropic model ID. |
| `infer_ancestry` | bool | `true` | Fill country-default `ancestry_mix` when a site omits it (e.g. `IN` → SAS). |

```bash
curl -X POST http://127.0.0.1:8600/extract \
  -H "Content-Type: application/json" \
  -d '{"prose": "A phase II trial of capecitabine 1250 mg/m² BID ..."}'
```

**Responses**

| Status | Body | Meaning |
|---|---|---|
| `200` | `Protocol` | Extraction succeeded. |
| `400` | `ErrorResponse` | Claude output failed `Protocol` validation. |
| `503` | `ErrorResponse` | `ANTHROPIC_API_KEY` is not set; extraction unavailable. |

---

### `GET /provenance/{gene}` — frequency-fixture provenance

Returns the pinned allele-frequency provenance for a gene: source metadata,
per-population frequencies, ground-truth diplotypes, and any known discrepancies
the fixture explicitly refuses to resolve. This is what makes a report number
auditable.

**Path parameters**

| Name | Type | Description |
|---|---|---|
| `gene` | string | Gene symbol, case-insensitive (e.g. `DPYD`). |

```bash
curl http://127.0.0.1:8600/provenance/DPYD
```

**Responses**

| Status | Body | Meaning |
|---|---|---|
| `200` | provenance object | Provenance for the gene. |
| `404` | `ErrorResponse` | No pinned frequency fixture for that gene. |

---

### `GET /fixtures/protocols` — demo protocol catalogue

Lists the pinned demo protocols as cards (`ProtocolCard[]`), driving the UI's
selection cards. Each entry exercises a different path through the engine (see
[DATASETS.md](DATASETS.md)). The pinned JSON itself is fetched separately by slug.

```bash
curl http://127.0.0.1:8600/fixtures/protocols
```

Returns `200` with `[ { slug, title, trial_id, cohort, demonstrates, detail, expect }, ... ]`.

---

### `GET /fixtures/protocols/{slug}` — one pinned protocol

Returns the pinned, hand-verified `Protocol` JSON for a catalogue slug.

**Path parameters**

| Name | Type | Description |
|---|---|---|
| `slug` | string | Catalogue slug from `GET /fixtures/protocols` (e.g. `demo`, `capecitabine-india`, `us-multiancestry`, `dpyd-screened`). |

```bash
curl http://127.0.0.1:8600/fixtures/protocols/demo
```

**Responses**

| Status | Body | Meaning |
|---|---|---|
| `200` | `Protocol` | The pinned protocol. |
| `404` | `ErrorResponse` | Unknown slug (message lists known slugs). |

A typical UI flow chains this into an audit: fetch the protocol by slug, then
`POST /audit` with the result.

---

### `GET /fixtures/reports/sample` — pinned sample report

Returns a pinned `AuditReport` — the only view that shows Tier 0/1/2 styling side
by side, since no single real audit produces all three. Served on demand from the
workbench's **Load sample report** button, not on mount. `200` with an
`AuditReport`.

### `GET /fixtures/reports/partial-coverage` — pinned partial-coverage report

Returns a pinned `AuditReport` that exercises the partial-ancestry-coverage UI
state (some declared populations have no pinned frequencies). `200` with an
`AuditReport`.

---

## Schemas

Full field-level schemas render in Swagger UI (`/docs`) and ReDoc (`/redoc`).
The load-bearing ones:

- **`Protocol`** — Claude's only output surface: `trial_id`, `title`, `drugs[]`,
  `inclusion_criteria[]`, `exclusion_criteria[]`, `sites[]` (each with
  `ancestry_mix`), `target_n`.
- **`AuditReport`** — `protocol_title`, `trial_id`, `total_planned_n`,
  `findings[]` (`GeneDrugFinding`: gene, drug, `verdict`, `tier`, `distribution[]`,
  `cpic_level`, `missing_exclusion`, `notes[]`, `citations[]`, `coverage`),
  `site_findings[]`, `data_sources[]`, `offline`, `warnings[]`.
- **`ProtocolCard`** — catalogue card metadata (`slug`, `title`, `trial_id`,
  `cohort`, `demonstrates`, `detail`, `expect`).
- **`ErrorResponse`** — `{ "detail": string }`.
