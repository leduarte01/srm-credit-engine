# PR #14 — CI/CD: GitHub Actions + pre-commit

## Summary
Adds the continuous-integration backbone for the repo: three path-
filtered GitHub Actions workflows (backend, frontend, docker) and a
repo-level `pre-commit` config that runs the same quality gates
locally before every commit. Baselines the existing code under the
new format checks (`ruff format` for Python, `prettier --check` for
the frontend) so the workflows start green from the very first push.

## Scope
- `.github/workflows/backend.yml` — triggered by changes under
  `backend/`. Installs `uv` via `astral-sh/setup-uv@v3` with caching
  keyed on `backend/uv.lock`, then runs `ruff check`, `ruff format
  --check`, `mypy --strict src` and `pytest` (with the existing
  `--cov-fail-under=80` gate). Uploads `coverage.xml` as an artifact.
- `.github/workflows/frontend.yml` — triggered by changes under
  `frontend/`. Uses `actions/setup-node@v4` with npm cache, runs
  `npm ci`, then `prettier --check`, `eslint .`, `tsc -b --noEmit`,
  `vitest run` and `vite build` with
  `VITE_API_BASE_URL=/api/v1` (the path nginx proxies in compose).
- `.github/workflows/docker.yml` — triggered by Dockerfile / compose
  changes. A `build` matrix builds the backend and frontend images
  in parallel through `docker/build-push-action@v6` with GHA layer
  cache (`type=gha`). A separate `compose` job runs
  `docker compose config --quiet` to lint the stack manifest.
- `.pre-commit-config.yaml` (root) — standard hygiene hooks
  (`trailing-whitespace`, `end-of-file-fixer`, YAML/JSON/TOML lint,
  merge-conflict markers, 512 kB large-file guard, LF line endings),
  `ruff` lint + `ruff-format` scoped to `^backend/`, and two local
  hooks that delegate to the existing npm scripts (`lint` and
  `format:check`) for files under `frontend/`.
- `style(backend)` — applied `ruff format` to 13 pre-existing files
  (tests + a few modules) so the new `ruff format --check` step
  passes without churn.
- `style(frontend)` — applied `prettier --write` to 11 pre-existing
  files for the same reason.

## Quality gates (local pre-flight)
- **Backend**: `ruff check` clean, `ruff format --check` clean,
  `mypy src` (strict) clean — 64 source files — and **148/148**
  pytest tests passing with **89.68 %** coverage (gate ≥ 80 %).
- **Frontend**: `prettier --check` clean, `eslint .` clean,
  `tsc -b --noEmit` clean, **13/13** vitest tests passing, `vite
  build` produces 327.29 kB JS (101.72 kB gzipped) and 16.09 kB CSS
  (3.91 kB gzipped).
- **YAML**: all three workflows and `.pre-commit-config.yaml` parse
  cleanly with `yaml.safe_load`.

## Architectural decisions
- **Per-component workflows with `paths:` filters**: a backend-only
  change does not trigger the frontend or docker job (and vice-
  versa). Keeps CI minutes low and feedback fast.
- **`concurrency.group` with `cancel-in-progress: true`**: stale runs
  on superseded commits are cancelled automatically, so reviewers
  never wait on outdated builds.
- **`astral-sh/setup-uv@v3` with lock-keyed cache**: deterministic,
  reproducible installs aligned with the Dockerfile. Faster than
  `pip install` and tied to the same `uv.lock` the runtime images
  use.
- **Pin `python-version-file: backend/.python-version`**: keeps CI,
  Docker image and local dev on the exact same interpreter version.
- **Format checks promoted to required gates**: drift in formatting
  is silently corrosive on long-lived projects. Failing fast and
  baselining the existing files is the lowest-cost way to prevent
  it.
- **Docker layer cache via `type=gha`**: reuses Buildx caches across
  runs so the longest stage (`uv sync`, `npm ci`) only re-executes
  when its lock file actually changes.
- **`docker compose config --quiet`** as a cheap stack lint:
  validates env-var interpolation, service references and yaml
  shape without needing a runtime engine to boot.
- **Local hooks for frontend in `.pre-commit-config.yaml`**: keeps a
  single source of truth (the npm scripts) instead of duplicating
  lint configuration in two places.

## How to validate locally
```pwsh
# Backend gates
cd backend
uv sync --frozen
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest

# Frontend gates
cd ../frontend
npm ci
npm run format:check
npm run lint
npm run typecheck
npm test
npm run build

# Pre-commit (one-time install)
cd ..
pip install pre-commit
pre-commit install
pre-commit run --all-files
```
