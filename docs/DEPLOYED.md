# Live deployment — Azure Container Apps

Deployed 2026-08-08 15:50 IST from `00a5396`, image tag `cohortfit:00a5396`.

## Live now

| | URL |
|---|---|
| Landing | https://cohortfit.lemonrock-26394a7b.eastus.azurecontainerapps.io/ |
| Audit workbench | https://cohortfit.lemonrock-26394a7b.eastus.azurecontainerapps.io/app |
| Swagger | https://cohortfit.lemonrock-26394a7b.eastus.azurecontainerapps.io/docs |
| Health | https://cohortfit.lemonrock-26394a7b.eastus.azurecontainerapps.io/health |

Verified live: all six routes return 200, and `POST /audit` on
`capecitabine-india` returns `ACTIONABLE` + `CONTESTED` with Normal 96.453% /
Intermediate 3.544% / Poor 0.004% — identical to local, which is what pinned
offline fixtures are supposed to guarantee.

`POST /extract` returns **503** because `ANTHROPIC_API_KEY` is deliberately not
set on the container. See [Security](#security).

## Resources

| Resource | Name |
|---|---|
| Subscription | `e64e3da3-a8ef-452e-a709-7d7437e12be9` (tech@anukritiai.com) |
| Resource group | `cohortfit-rg` |
| Location | `eastus` |
| Container registry | `cohortfitacr44749` |
| Container Apps env | `cohortfit-env` |
| Container app | `cohortfit` |
| Log Analytics | `workspace-cohortfitrgQzp5` (auto-created) |
| Scale | 0.5 CPU / 1.0 Gi, **0–3 replicas** |

Min replicas is **0**, so the app scales to zero when idle and costs nothing but
storage. First request after idle incurs a cold start of a few seconds — worth
warming it with a `curl` before demoing.

## Custom subdomain — needs two DNS records at Namecheap

**This step could not be automated.** `anukritiai.com` uses
`dns1.registrar-servers.com` / `dns2.registrar-servers.com` (Namecheap), and there
is no Azure DNS zone for it in the subscription, so there is no Azure API to
create records through. The records must be added in the Namecheap dashboard.

Suggested hostname: **`cohortfit.anukritiai.com`** (currently unresolved, so it
is free). `app.` and `api.` are also unused.

### Step 1 — add these two records

In Namecheap → Domain List → `anukritiai.com` → Advanced DNS:

| Type | Host | Value | TTL |
|---|---|---|---|
| `CNAME` | `cohortfit` | `cohortfit.lemonrock-26394a7b.eastus.azurecontainerapps.io` | Automatic |
| `TXT` | `asuid.cohortfit` | `302CA23B1DDF96612519BE81AC2DC9D62AD569A3DF26A7F76642122FA2513021` | Automatic |

The `TXT` record is Azure's ownership proof. Both must exist and have propagated
before the next step, or binding fails.

### Step 2 — verify propagation

```bash
dig +short CNAME cohortfit.anukritiai.com
dig +short TXT   asuid.cohortfit.anukritiai.com
```

### Step 3 — bind the hostname and issue a free managed certificate

```bash
az containerapp hostname add \
  -n cohortfit -g cohortfit-rg \
  --hostname cohortfit.anukritiai.com

az containerapp hostname bind \
  -n cohortfit -g cohortfit-rg \
  --hostname cohortfit.anukritiai.com \
  --environment cohortfit-env \
  --validation-method CNAME
```

Azure issues and auto-renews a managed TLS certificate; allow a few minutes.

### Step 4 — confirm

```bash
curl -s https://cohortfit.anukritiai.com/health
```

## Security

**The API has no authentication.** That is acceptable for this deployment only
because of what is *not* enabled:

- `ANTHROPIC_API_KEY` is **unset**, so `POST /extract` returns 503 and the
  container cannot be used as an open proxy to a paid Anthropic account. **Do not
  set that variable on a public deployment without adding auth first.**
- Every other route is read-only or pure computation over pinned offline
  fixtures. `POST /audit` accepts a `Protocol` body and returns arithmetic; it
  reads no user data, writes nothing, and reaches no network.
- CORS still allows only localhost origins, so a browser on another site cannot
  call it with credentials.

If extraction is needed in the deployed demo, the honest options are an API key
in a header checked by the route, or Container Apps authentication in front of
the whole app. Neither is done.

## Operations

```bash
# Logs
az containerapp logs show -n cohortfit -g cohortfit-rg --follow

# Redeploy after a commit (rebuilds in ACR, updates the revision)
./scripts/deploy-azure.sh -g cohortfit-rg -n cohortfit --acr cohortfitacr44749

# Current revision and image
az containerapp show -n cohortfit -g cohortfit-rg \
  --query "properties.template.containers[0].image" -o tsv

# Tear everything down — deletes the registry, env, app and workspace
az group delete -n cohortfit-rg --yes --no-wait
```

The image tag is the git short SHA, so a redeploy from a new commit produces a
new tag and a new revision rather than overwriting one.
