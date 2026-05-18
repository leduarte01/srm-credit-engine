"""ASGI middleware that injects request_id and records HTTP metrics."""

from __future__ import annotations

import time
import uuid
from typing import TYPE_CHECKING

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from srm_credit_engine.observability.metrics import (
    HTTP_REQUEST_DURATION_SECONDS,
    HTTP_REQUESTS_TOTAL,
)

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

REQUEST_ID_HEADER = "x-request-id"


class ObservabilityMiddleware(BaseHTTPMiddleware):
    """Bind a per-request correlation id and emit Prometheus counters.

    - Reads ``X-Request-ID`` from the inbound headers, falling back to a
      fresh UUID4 when absent.
    - Stores the id in :mod:`structlog.contextvars` so every log emitted
      during the request carries it without further plumbing.
    - Records request count and latency histogram on the way out, using
      the route template (when available) to keep cardinality bounded.
    - Echoes the request id back in the response headers.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid.uuid4())
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        )

        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            # Counted as a 500 — the framework's exception handler still
            # produces the final response, this is the metrics-side view.
            elapsed = time.perf_counter() - start
            route = _route_template(request)
            HTTP_REQUESTS_TOTAL.labels(request.method, route, "500").inc()
            HTTP_REQUEST_DURATION_SECONDS.labels(request.method, route).observe(elapsed)
            raise

        elapsed = time.perf_counter() - start
        route = _route_template(request)
        HTTP_REQUESTS_TOTAL.labels(request.method, route, str(response.status_code)).inc()
        HTTP_REQUEST_DURATION_SECONDS.labels(request.method, route).observe(elapsed)
        response.headers[REQUEST_ID_HEADER] = request_id
        return response


def _route_template(request: Request) -> str:
    route = request.scope.get("route")
    path = getattr(route, "path", None)
    return path if isinstance(path, str) else request.url.path
