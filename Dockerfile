# cohortfit — API + static web UI in one image.
# Build:  docker build -t cohortfit .
# Run:    docker run --rm -p 8000:8000 cohortfit

# ---------------------------------------------------------------------------
# Stage 1: frontend
# ---------------------------------------------------------------------------
FROM node:20-alpine AS web
WORKDIR /web
COPY web/package.json web/package-lock.json ./
RUN npm ci
COPY web/ ./
RUN npm run build

# ---------------------------------------------------------------------------
# Stage 2: API + UI
# ---------------------------------------------------------------------------
FROM python:3.12-slim

WORKDIR /app

# System deps for some wheels; keep the image lean.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md LICENSE ./
COPY src ./src
COPY fixtures ./fixtures
COPY protocols ./protocols
COPY --from=web /web/dist ./web/dist

# Editable install keeps repo layout so repo_root() / fixtures / web/dist resolve.
RUN pip install --no-cache-dir -U pip \
    && pip install --no-cache-dir -e ".[web,llm]"

ENV PORT=8000 \
    HOST=0.0.0.0 \
    PYTHONUNBUFFERED=1

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS "http://127.0.0.1:${PORT}/health" || exit 1

# Bind 0.0.0.0 so Azure ingress can reach the process.
CMD ["sh", "-c", "exec uvicorn cohortfit.api.app:app --host ${HOST} --port ${PORT}"]
