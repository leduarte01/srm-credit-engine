#!/usr/bin/env bash
set -euo pipefail

# Run database migrations before booting the API. Alembic reads the
# database URL from settings, so DATABASE_URL needs to be set in the
# environment (docker-compose wires this).
if [[ "${RUN_MIGRATIONS:-true}" == "true" ]]; then
  echo "[entrypoint] Running alembic upgrade head"
  alembic upgrade head
else
  echo "[entrypoint] RUN_MIGRATIONS=false — skipping migrations"
fi

echo "[entrypoint] Launching: $*"
exec "$@"
