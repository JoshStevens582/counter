import logging
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status

from counter.services.rate_limit import (
    RateLimiter,
    RateLimiterUnavailable,
    RateLimitExceeded,
)

logger = logging.getLogger("counter.deps")


def _client_ip(request: Request) -> str:
    if request.client is not None and request.client.host:
        return request.client.host
    return "unknown"


def _get_rate_limiter(request: Request) -> RateLimiter | None:
    limiter = getattr(request.app.state, "rate_limiter", None)
    if limiter is None:
        return None
    if not isinstance(limiter, RateLimiter):
        raise RuntimeError("Rate limiter is misconfigured.")
    return limiter


async def enforce_public_ask_rate_limit(request: Request) -> None:
    settings = request.app.state.settings
    if not settings.rate_limit_enabled:
        return
    limiter = _get_rate_limiter(request)
    if limiter is None:
        if settings.rate_limit_fail_closed:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=(
                    "Rate limits require Redis. Start Redis or set "
                    "RATE_LIMIT_ENABLED=false for local use."
                ),
            )
        return
    try:
        await limiter.hit(subject=_client_ip(request), bucket="ask")
    except RateLimitExceeded as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=exc.detail,
            headers={"Retry-After": str(exc.retry_after_seconds)},
        ) from exc
    except RateLimiterUnavailable as exc:
        logger.warning("rate limiter unavailable mid-request")
        if settings.rate_limit_fail_closed:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Rate limits require Redis.",
            ) from exc


AskRateLimit = Annotated[None, Depends(enforce_public_ask_rate_limit)]
