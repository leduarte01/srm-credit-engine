# PR #13 — Docker: end-to-end local stack with Compose

## Summary
Containerises the full credit engine so the whole stack — Postgres,
FastAPI backend and the React panel — comes up with a single
`docker compose up --build`. The backend image is a slim, multi-stage
build that runs Alembic migrations on boot and serves Uvicorn as a
non-root user. The frontend image is a multi-stage Node build that
ends in an `nginx:alpine` image which both serves the SPA and reverse-
proxies `/api` to the backend over the docker network.

## Scope
- `backend/Dockerfile` — multi-stage image based on `python:3.12-slim`.
  Builder stage installs `uv`, syncs the locked dependency tree into
  `/opt/venv` (with `UV_COMPILE_BYTECODE=1`) and copies in source and
  Alembic config. Runtime stage drops `curl`/`ca-certificates`, copies
  the venv and source over, creates an unprivileged `app` user,
  declares a `HEALTHCHECK` against `/health` and uses an entrypoint
  script as `ENTRYPOINT`.
- `backend/docker/entrypoint.sh` — runs `alembic upgrade head` (gated
  by `RUN_MIGRATIONS=true`) before `exec`-ing the passed command, so
  schema changes ship atomically with the image.
- `backend/.dockerignore` — excludes caches, virtualenvs, tests, docs
  and local env files from the build context to keep the layer cache
  hot and the image small.
- `frontend/Dockerfile` — multi-stage image. Builder runs
  `npm ci --no-audit --no-fund` and `npm run build` with
  `VITE_API_BASE_URL` injected via `ARG`. Runtime stage is
  `nginx:1.27-alpine` which serves `/usr/share/nginx/html` and the
  custom config.
- `frontend/docker/nginx.conf` — SPA-aware nginx config: a `/healthz`
  liveness endpoint, a `/api/` reverse proxy to the backend service,
  the `try_files $uri $uri/ /index.html` fallback for client-side
  routing and long-cache headers for hashed `/assets/`.
- `frontend/.dockerignore` — excludes `node_modules`, `dist`, env and
  editor files.
- `docker-compose.yml` (root) — three services: `db`
  (`postgres:16-alpine` with `pg_isready` healthcheck and named
  volume), `backend` (depends on `db: service_healthy`, env vars wire
  the asyncpg URL to the `db` hostname, exposes `:8000`), `frontend`
  (depends on `backend`, exposes `:8080 → :80`). All ports, the DB
  credentials and the CORS origins are overridable from a root
  `.env`.
- `.env.example` (root) — documents every variable consumed by
  `docker-compose.yml`.

## Quality gates
- **YAML**: `docker-compose.yml` parses cleanly (`yaml.safe_load`,
  3 services + 1 volume).
- **Shell**: `entrypoint.sh` written with LF endings (repo-wide
  `.gitattributes eol=lf` enforces it).
- **Dockerfile**: targets pinned (`python:3.12-slim`,
  `node:22-alpine`, `nginx:1.27-alpine`, `postgres:16-alpine`).
- **Runtime build/run not executed locally** — no Docker engine
  available in the dev environment. Listed under "How to validate".

## Architectural decisions
- **Multi-stage builds**: build tooling (`build-essential`, `uv`,
  full `node_modules`) stays in the builder stage. Runtime images
  only carry the venv / static bundle. Keeps the final layers small
  and removes attack surface.
- **`uv sync --frozen --no-dev`**: reproducible installs from
  `uv.lock`. `UV_COMPILE_BYTECODE=1` precompiles `.pyc` so the first
  request after boot is not slowed down by import-time compilation.
- **Migrations run on boot via entrypoint**: keeps schema and code
  coupled in one deployable unit. Toggleable via `RUN_MIGRATIONS=false`
  for orchestrators that prefer dedicated migration jobs.
- **Non-root runtime user (`app:app`)**: the runtime container has no
  reason to run as UID 0; restricting privileges is OWASP-A5 hygiene
  and matches the resilience-first posture of the rest of the stack.
- **nginx in front of the SPA + reverse proxy `/api`**: production-
  shape topology (single origin, no CORS in prod). The Vite dev
  proxy already mirrors this, so dev and prod runtime behaviour stay
  identical.
- **`depends_on: service_healthy`**: the backend only starts after
  Postgres reports ready, which prevents Alembic from racing the
  database and exiting non-zero on the first boot.
- **Healthchecks everywhere**: Postgres (`pg_isready`), backend
  (`curl /health`), nginx (`/healthz`). Compose can surface unhealthy
  containers and orchestrators (k8s, ECS) can reuse the same probes.
- **Frontend build arg `VITE_API_BASE_URL=/api/v1`**: keeps the SPA
  origin-agnostic. In compose, nginx proxies that path to the
  backend service over the docker network — no env vars need to
  reach the browser.

## How to validate locally
```pwsh
# from the repo root
cp .env.example .env   # optional; defaults work out of the box
docker compose up --build

# then
# Panel:    http://localhost:8080
# Backend:  http://localhost:8000/health
# Postgres: localhost:5432 (srm / srm / srm_credit)

# Tear down (keep the data volume)
docker compose down

# Tear down and wipe the database volume
docker compose down -v
```
