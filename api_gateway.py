# CodexImmortal Agentic AI NFT War Lab
# Author: Caleb Fedor Byker Konev | 10/27/1998
# [CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-API-GATEWAY]

from __future__ import annotations

import asyncio
import time
import uuid
from collections import defaultdict, deque
from typing import Awaitable, Callable

import httpx
import pybreaker
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

SERVICE_MAP = {
    "pqc": "http://pqc-spine-api:8090",
    "storage": "http://storage-mesh-api:8091",
    "agents": "http://neural-fabric-api:8092",
    "nft": "http://nft-vault-api:8093",
    "playbook": "http://playbook-engine:8094",
    "threats": "http://threat-board-api:8095",
}

app = FastAPI(title="CodexImmortal API Gateway")
rate_buckets: dict[str, deque] = defaultdict(deque)
breakers = {name: pybreaker.CircuitBreaker(fail_max=5, reset_timeout=30) for name in SERVICE_MAP}


class PQCTLSVerifierMiddleware:
    async def __call__(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        algo = request.headers.get("x-client-cert-algorithm", "")
        if algo and "ML-DSA" not in algo and "SLH-DSA" not in algo:
            return JSONResponse(status_code=403, content={"detail": "Unsupported client certificate algorithm"})
        return await call_next(request)


class UnifiedAuthMiddleware:
    async def __call__(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        if not request.headers.get("authorization") and not request.headers.get("x-wallet-signature"):
            return JSONResponse(status_code=401, content={"detail": "Missing auth"})
        return await call_next(request)


class RateLimiterMiddleware:
    def __init__(self, limit: int = 60, window_seconds: int = 60) -> None:
        self.limit = limit
        self.window = window_seconds

    async def __call__(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        principal = request.headers.get("authorization", request.client.host if request.client else "anonymous")
        bucket = rate_buckets[principal]
        now = time.time()
        while bucket and now - bucket[0] > self.window:
            bucket.popleft()
        if len(bucket) >= self.limit:
            return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})
        bucket.append(now)
        return await call_next(request)


class AuditLoggerMiddleware:
    async def __call__(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        response = await call_next(request)
        print(
            {
                "event": "api_request",
                "path": request.url.path,
                "method": request.method,
                "status": response.status_code,
            }
        )
        return response


class LineageInjectorMiddleware:
    async def __call__(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        response = await call_next(request)
        response.headers["X-Codex-Tag"] = "[CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL]"
        response.headers["X-Lineage-ID"] = str(uuid.uuid4())
        return response


class SecretRedactorMiddleware:
    async def __call__(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        response = await call_next(request)
        return response


app.middleware("http")(LineageInjectorMiddleware())
app.middleware("http")(SecretRedactorMiddleware())
app.middleware("http")(AuditLoggerMiddleware())
app.middleware("http")(RateLimiterMiddleware(limit=120, window_seconds=60))
app.middleware("http")(UnifiedAuthMiddleware())
app.middleware("http")(PQCTLSVerifierMiddleware())


async def proxy_request(service_name: str, tail: str, request: Request) -> Response:
    upstream = f"{SERVICE_MAP[service_name]}/{tail}".rstrip("/")
    breaker = breakers[service_name]

    headers = dict(request.headers)
    content = await request.body()

    async def _send():
        async with httpx.AsyncClient(timeout=15.0) as client:
            return await client.request(
                request.method,
                upstream,
                headers=headers,
                params=dict(request.query_params),
                content=content,
            )

    for attempt in range(3):
        try:
            upstream_response = await breaker.call_async(_send)
            return Response(
                content=upstream_response.content,
                status_code=upstream_response.status_code,
                headers=dict(upstream_response.headers),
            )
        except Exception:
            if attempt == 2:
                return JSONResponse(status_code=502, content={"detail": f"Upstream failure for {service_name}"})
            await asyncio.sleep((2 ** attempt) + 0.1)


@app.api_route("/api/v1/{service}/{tail:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def gateway(service: str, tail: str, request: Request) -> Response:
    if service not in SERVICE_MAP:
        return JSONResponse(status_code=404, content={"detail": "Unknown service"})
    return await proxy_request(service, tail, request)


@app.get("/openapi-aggregate")
async def openapi_aggregate():
    return {"services": list(SERVICE_MAP.keys()), "status": "placeholder"}