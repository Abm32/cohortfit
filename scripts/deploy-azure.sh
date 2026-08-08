#!/usr/bin/env bash
# Deploy cohortfit to Azure Container Apps via az CLI.
#
# Prerequisites:
#   - Azure CLI (`az`) installed and logged in:  az login
#   - Contributor (or equivalent) on the subscription
#
# Usage (from the cohortfit repo root):
#   ./scripts/deploy-azure.sh
#   ./scripts/deploy-azure.sh --resource-group my-rg --location eastus --name cohortfit
#   ANTHROPIC_API_KEY=sk-... ./scripts/deploy-azure.sh   # enables POST /extract
#
# What it creates:
#   Resource group → ACR → cloud image build → Container Apps env → app (HTTPS)
#
# Idempotent: re-running updates the image and revises the container app.

set -euo pipefail

# ---------------------------------------------------------------------------
# Defaults (override with flags or env)
# ---------------------------------------------------------------------------
RESOURCE_GROUP="${COHORTFIT_AZ_RG:-cohortfit-rg}"
LOCATION="${COHORTFIT_AZ_LOCATION:-eastus}"
APP_NAME="${COHORTFIT_AZ_APP:-cohortfit}"
# ACR names are global + alphanumeric only. Default includes a short unique suffix.
ACR_NAME="${COHORTFIT_AZ_ACR:-}"
IMAGE_REPO="${COHORTFIT_AZ_IMAGE:-cohortfit}"
IMAGE_TAG="${COHORTFIT_AZ_TAG:-$(git rev-parse --short HEAD 2>/dev/null || date +%Y%m%d%H%M)}"
ENV_NAME=""
CPU="${COHORTFIT_AZ_CPU:-0.5}"
MEMORY="${COHORTFIT_AZ_MEMORY:-1.0Gi}"
MIN_REPLICAS="${COHORTFIT_AZ_MIN_REPLICAS:-0}"
MAX_REPLICAS="${COHORTFIT_AZ_MAX_REPLICAS:-3}"
SKIP_BUILD=0
DRY_RUN=0

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

usage() {
  cat <<'EOF'
Deploy cohortfit to Azure Container Apps.

Usage:
  ./scripts/deploy-azure.sh [options]

Options:
  --resource-group, -g NAME   Azure resource group (default: cohortfit-rg)
  --location, -l REGION       Azure region (default: eastus)
  --name, -n NAME             Container app name (default: cohortfit)
  --acr NAME                  Azure Container Registry name (global, alphanumeric)
  --tag TAG                   Image tag (default: short git SHA)
  --cpu N                     vCPU per replica (default: 0.5)
  --memory SIZE               Memory per replica (default: 1.0Gi)
  --min-replicas N            Min replicas; 0 = scale to zero (default: 0)
  --max-replicas N            Max replicas (default: 3)
  --skip-build                Reuse the existing :tag image in ACR (no rebuild)
  --dry-run                   Print the plan and exit
  -h, --help                  Show this help

Environment:
  ANTHROPIC_API_KEY           If set, injected as a Container App secret so
                              POST /extract works in the cloud.
  COHORTFIT_AZ_*              Same as the flags above (see script header).
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -g|--resource-group) RESOURCE_GROUP="$2"; shift 2 ;;
    -l|--location) LOCATION="$2"; shift 2 ;;
    -n|--name) APP_NAME="$2"; shift 2 ;;
    --acr) ACR_NAME="$2"; shift 2 ;;
    --tag) IMAGE_TAG="$2"; shift 2 ;;
    --cpu) CPU="$2"; shift 2 ;;
    --memory) MEMORY="$2"; shift 2 ;;
    --min-replicas) MIN_REPLICAS="$2"; shift 2 ;;
    --max-replicas) MAX_REPLICAS="$2"; shift 2 ;;
    --skip-build) SKIP_BUILD=1; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 1 ;;
  esac
done

ENV_NAME="${APP_NAME}-env"

# Derive a valid ACR name if the caller did not pass one.
if [[ -z "${ACR_NAME}" ]]; then
  # Strip non-alphanumeric, lowercase, keep ≤ 40 chars, append short hash for uniqueness.
  base="$(echo "${APP_NAME}acr" | tr '[:upper:]' '[:lower:]' | tr -cd 'a-z0-9')"
  suffix="$(printf '%s' "${RESOURCE_GROUP}${LOCATION}" | cksum | awk '{print $1}' | tail -c 6)"
  ACR_NAME="${base}${suffix}"
  ACR_NAME="${ACR_NAME:0:50}"
fi

if ! [[ "${ACR_NAME}" =~ ^[a-zA-Z0-9]+$ ]]; then
  echo "Error: ACR name must be alphanumeric only (got: ${ACR_NAME})" >&2
  exit 1
fi

IMAGE="${IMAGE_REPO}:${IMAGE_TAG}"

log() { printf '\n\033[1;32m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33mWarning:\033[0m %s\n' "$*" >&2; }

# ---------------------------------------------------------------------------
# Preconditions
# ---------------------------------------------------------------------------
if [[ ! -f "${REPO_ROOT}/pyproject.toml" || ! -f "${REPO_ROOT}/Dockerfile" ]]; then
  echo "Error: run this from the cohortfit repo (missing pyproject.toml / Dockerfile)." >&2
  exit 1
fi

if ! command -v az >/dev/null 2>&1; then
  echo "Error: Azure CLI (az) not found. Install: https://learn.microsoft.com/cli/azure/install-azure-cli" >&2
  exit 1
fi

if ! az account show >/dev/null 2>&1; then
  echo "Error: not logged in. Run: az login" >&2
  exit 1
fi

SUBSCRIPTION="$(az account show --query id -o tsv)"
ACCOUNT_NAME="$(az account show --query user.name -o tsv 2>/dev/null || echo unknown)"

cat <<EOF
cohortfit → Azure Container Apps
  subscription : ${SUBSCRIPTION} (${ACCOUNT_NAME})
  resource group: ${RESOURCE_GROUP}
  location      : ${LOCATION}
  app           : ${APP_NAME}
  environment   : ${ENV_NAME}
  ACR           : ${ACR_NAME}
  image         : ${IMAGE}
  cpu / memory  : ${CPU} / ${MEMORY}
  replicas      : ${MIN_REPLICAS}–${MAX_REPLICAS}
  extract key   : $([ -n "${ANTHROPIC_API_KEY:-}" ] && echo set || echo not set — POST /extract will 503)
  skip build    : ${SKIP_BUILD}
EOF

if [[ "${DRY_RUN}" -eq 1 ]]; then
  log "Dry run — nothing created."
  exit 0
fi

cd "${REPO_ROOT}"

# ---------------------------------------------------------------------------
# Providers + resource group
# ---------------------------------------------------------------------------
log "Ensuring resource providers (Microsoft.App, Microsoft.ContainerRegistry)…"
az provider register --namespace Microsoft.App --wait >/dev/null
az provider register --namespace Microsoft.ContainerRegistry --wait >/dev/null
az provider register --namespace Microsoft.OperationalInsights --wait >/dev/null

log "Ensuring resource group ${RESOURCE_GROUP} in ${LOCATION}…"
az group create --name "${RESOURCE_GROUP}" --location "${LOCATION}" --output none

# ---------------------------------------------------------------------------
# ACR + image build (cloud build — no local Docker required)
# ---------------------------------------------------------------------------
if ! az acr show --name "${ACR_NAME}" --resource-group "${RESOURCE_GROUP}" >/dev/null 2>&1; then
  log "Creating Azure Container Registry ${ACR_NAME}…"
  az acr create \
    --resource-group "${RESOURCE_GROUP}" \
    --name "${ACR_NAME}" \
    --sku Basic \
    --admin-enabled true \
    --output none
else
  log "ACR ${ACR_NAME} already exists."
fi

ACR_LOGIN_SERVER="$(az acr show --name "${ACR_NAME}" --resource-group "${RESOURCE_GROUP}" --query loginServer -o tsv)"
FULL_IMAGE="${ACR_LOGIN_SERVER}/${IMAGE}"

if [[ "${SKIP_BUILD}" -eq 0 ]]; then
  log "Building image in ACR (az acr build) → ${FULL_IMAGE}…"
  az acr build \
    --registry "${ACR_NAME}" \
    --image "${IMAGE}" \
    --file Dockerfile \
    .
else
  warn "Skipping image build; expecting ${FULL_IMAGE} already in ACR."
fi

ACR_USERNAME="$(az acr credential show --name "${ACR_NAME}" --query username -o tsv)"
ACR_PASSWORD="$(az acr credential show --name "${ACR_NAME}" --query passwords[0].value -o tsv)"

# ---------------------------------------------------------------------------
# Container Apps environment
# ---------------------------------------------------------------------------
if ! az containerapp env show --name "${ENV_NAME}" --resource-group "${RESOURCE_GROUP}" >/dev/null 2>&1; then
  log "Creating Container Apps environment ${ENV_NAME}…"
  az containerapp env create \
    --name "${ENV_NAME}" \
    --resource-group "${RESOURCE_GROUP}" \
    --location "${LOCATION}" \
    --output none
else
  log "Container Apps environment ${ENV_NAME} already exists."
fi

# ---------------------------------------------------------------------------
# Secrets + app create / update
# ---------------------------------------------------------------------------
SECRET_ARGS=( "acr-password=${ACR_PASSWORD}" )
ENV_ARGS=( "PORT=8000" "HOST=0.0.0.0" )
if [[ -n "${ANTHROPIC_API_KEY:-}" ]]; then
  SECRET_ARGS+=( "anthropic-api-key=${ANTHROPIC_API_KEY}" )
  ENV_ARGS+=( "ANTHROPIC_API_KEY=secretref:anthropic-api-key" )
fi

# Join arrays as space-separated for az --secrets / --env-vars (name=value …)
secrets_csv="${SECRET_ARGS[*]}"
env_csv="${ENV_ARGS[*]}"

if ! az containerapp show --name "${APP_NAME}" --resource-group "${RESOURCE_GROUP}" >/dev/null 2>&1; then
  log "Creating Container App ${APP_NAME}…"
  # shellcheck disable=SC2086
  az containerapp create \
    --name "${APP_NAME}" \
    --resource-group "${RESOURCE_GROUP}" \
    --environment "${ENV_NAME}" \
    --image "${FULL_IMAGE}" \
    --target-port 8000 \
    --ingress external \
    --transport auto \
    --cpu "${CPU}" \
    --memory "${MEMORY}" \
    --min-replicas "${MIN_REPLICAS}" \
    --max-replicas "${MAX_REPLICAS}" \
    --registry-server "${ACR_LOGIN_SERVER}" \
    --registry-username "${ACR_USERNAME}" \
    --registry-password "${ACR_PASSWORD}" \
    --secrets ${secrets_csv} \
    --env-vars ${env_csv} \
    --output none
else
  log "Updating Container App ${APP_NAME} → ${FULL_IMAGE}…"
  # Refresh registry credentials + secrets, then point at the new image.
  # shellcheck disable=SC2086
  az containerapp secret set \
    --name "${APP_NAME}" \
    --resource-group "${RESOURCE_GROUP}" \
    --secrets ${secrets_csv} \
    --output none

  # shellcheck disable=SC2086
  az containerapp update \
    --name "${APP_NAME}" \
    --resource-group "${RESOURCE_GROUP}" \
    --image "${FULL_IMAGE}" \
    --cpu "${CPU}" \
    --memory "${MEMORY}" \
    --min-replicas "${MIN_REPLICAS}" \
    --max-replicas "${MAX_REPLICAS}" \
    --set-env-vars ${env_csv} \
    --output none

  # Ensure registry login stays valid after ACR password rotation.
  az containerapp registry set \
    --name "${APP_NAME}" \
    --resource-group "${RESOURCE_GROUP}" \
    --server "${ACR_LOGIN_SERVER}" \
    --username "${ACR_USERNAME}" \
    --password "${ACR_PASSWORD}" \
    --output none
fi

FQDN="$(az containerapp show \
  --name "${APP_NAME}" \
  --resource-group "${RESOURCE_GROUP}" \
  --query properties.configuration.ingress.fqdn -o tsv)"

# ---------------------------------------------------------------------------
# Smoke check
# ---------------------------------------------------------------------------
URL="https://${FQDN}"
log "Waiting for /health on ${URL}…"
ok=0
for i in $(seq 1 30); do
  if curl -fsS --max-time 10 "${URL}/health" >/dev/null 2>&1; then
    ok=1
    break
  fi
  sleep 5
done

if [[ "${ok}" -eq 1 ]]; then
  log "Deployed and healthy."
else
  warn "App is reachable at ${URL} but /health did not respond yet (cold start / pull still in progress)."
  warn "Check logs: az containerapp logs show -n ${APP_NAME} -g ${RESOURCE_GROUP} --follow"
fi

cat <<EOF

────────────────────────────────────────────────────────
  Landing        ${URL}/
  Audit app      ${URL}/app
  Swagger        ${URL}/docs
  Health         ${URL}/health

  Logs:
    az containerapp logs show -n ${APP_NAME} -g ${RESOURCE_GROUP} --follow

  Redeploy (rebuild + update):
    ./scripts/deploy-azure.sh -g ${RESOURCE_GROUP} -n ${APP_NAME} --acr ${ACR_NAME}

  Tear down everything in the resource group:
    az group delete -n ${RESOURCE_GROUP} --yes --no-wait
────────────────────────────────────────────────────────
EOF
