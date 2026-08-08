# Deploy cohortfit to Azure

One-command deploy of the API + web UI to **Azure Container Apps**, using only
the Azure CLI. The image is built in the cloud (`az acr build`) — you do **not**
need Docker installed locally.

## What you get

| URL | Content |
|---|---|
| `https://<app>.azurecontainerapps.io/` | Marketing landing |
| `https://<app>.azurecontainerapps.io/app` | Interactive audit workbench |
| `https://<app>.azurecontainerapps.io/docs` | Swagger UI |
| `https://<app>.azurecontainerapps.io/health` | Liveness probe |

Same-origin serving (API + static UI from one container), offline-by-default
engine, optional Claude extraction if you pass `ANTHROPIC_API_KEY`.

## Prerequisites

1. [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) installed.
2. An Azure subscription you can create resources in.
3. Logged in:

```bash
az login
az account set --subscription "<your-subscription-id-or-name>"
```

## Deploy

From the **cohortfit repo root**:

```bash
chmod +x scripts/deploy-azure.sh
./scripts/deploy-azure.sh
```

Optional knobs:

```bash
# Choose names / region
./scripts/deploy-azure.sh \
  --resource-group cohortfit-rg \
  --location eastus \
  --name cohortfit

# Enable POST /extract in the cloud
ANTHROPIC_API_KEY=sk-ant-... ./scripts/deploy-azure.sh

# Preview without creating anything
./scripts/deploy-azure.sh --dry-run

# Push a new revision without rebuilding the image
./scripts/deploy-azure.sh --skip-build --tag <existing-tag>
```

The script is **idempotent**: re-running rebuilds the image (unless
`--skip-build`) and updates the existing Container App.

## What the script creates

| Resource | Purpose |
|---|---|
| Resource group | Holds everything (default `cohortfit-rg`) |
| Azure Container Registry (Basic) | Stores the image; `az acr build` runs here |
| Container Apps environment | Shared hosting fabric |
| Container App | The running service (HTTPS, external ingress on port 8000) |

Image build uses the repo [`Dockerfile`](../Dockerfile) (Node builds `web/dist`,
then a Python 3.12 image installs `.[web,llm]` and serves with uvicorn).

## Useful commands after deploy

```bash
# Follow logs
az containerapp logs show -n cohortfit -g cohortfit-rg --follow

# Show the public FQDN
az containerapp show -n cohortfit -g cohortfit-rg \
  --query properties.configuration.ingress.fqdn -o tsv

# Scale (e.g. keep one warm replica)
az containerapp update -n cohortfit -g cohortfit-rg --min-replicas 1

# Rotate / set the Anthropic key later
az containerapp secret set -n cohortfit -g cohortfit-rg \
  --secrets anthropic-api-key="$ANTHROPIC_API_KEY"
az containerapp update -n cohortfit -g cohortfit-rg \
  --set-env-vars ANTHROPIC_API_KEY=secretref:anthropic-api-key
```

## Tear down

```bash
az group delete -n cohortfit-rg --yes --no-wait
```

## Local Docker smoke test (optional)

If you *do* have Docker locally and want to verify the image before Azure:

```bash
docker build -t cohortfit:local .
docker run --rm -p 8000:8000 cohortfit:local
# → http://127.0.0.1:8000/health
```

## Cost notes

- Defaults scale to **zero** (`--min-replicas 0`) when idle — good for demos.
- ACR Basic + Container Apps consumption plan are usually enough for a hackathon
  / prototype. Cold starts after idle can take 20–40s; set `--min-replicas 1`
  if you need instant responses on stage.
- First deploy registers resource providers (`Microsoft.App`, etc.) and can take
  several minutes on a fresh subscription.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `az: command not found` | Install Azure CLI, then `az login` |
| ACR name already taken | Pass `--acr <unique alphanumeric name>` |
| `/health` never goes green | `az containerapp logs show -n … -g … --follow` — usually image pull or provider registration still running |
| `POST /extract` → 503 | Redeploy with `ANTHROPIC_API_KEY=… ./scripts/deploy-azure.sh` |
| UI 404 on `/app` | Image was built without the web stage — rebuild without `--skip-build` |
