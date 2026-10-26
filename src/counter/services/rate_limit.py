from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta

from redis.asyncio import Redis
from redis.exceptions import RedisError

from counter.config import Settings

logger = logging.getLogger("counter.rate_limit")


class RateLimitExceeded(Exception):
    def __init__(self, detail: str, *, retry_after_seconds: int) -> None:
        super().__init__(detail)
        self.detail = detail
        self.retry_after_seconds = retry_after_seconds


class RateLimiterUnavailable(Exception):
    """Redis unreachable while rate limits are enabled."""


class RateLimiter:
    def __init__(self, client: Redis, settings: Settings) -> None:
        self._client = client
        self._settings = settings

    async def hit(self, *, subject: str, bucket: str = "ask") -> None:
        if bucket != "ask":
            raise ValueError(f"Unknown rate-limit bucket '{bucket}'.")
        if not subject.strip():
            raise ValueError("subject is required for rate limiting.")

        minute_limit = self._settings.rate_limit_ask_per_minute
        daily_limit = self._settings.rate_limit_ask_per_day

        await self._bump(
            key=f"counter:ratelimit:ask:min:{subject}",
            limit=minute_limit,
            ttl_seconds=self._settings.rate_limit_window_seconds,
            label="ask (per minute)",
        )
        await self._bump(
            key=f"counter:ratelimit:ask:day:{_utc_day()}:{subject}",
            limit=daily_limit,
            ttl_seconds=_seconds_until_utc_midnight(),
            label="ask (per day)",
        )
        await self._bump(
            key=f"counter:ratelimit:ask:day:{_utc_day()}:global",
            limit=self._settings.rate_limit_ask_global_per_day,
            ttl_seconds=_seconds_until_utc_midnight(),
            label="ask (app daily budget)",
        )

    async def _bump(
        self,
        *,
        key: str,
        limit: int,
        ttl_seconds: int,
        label: str,
    ) -> None:
        if limit <= 0:
            raise RateLimitExceeded(
                f"Rate limit blocked for {label}.",
                retry_after_seconds=max(1, ttl_seconds),
            )
        try:
            count = int(await self._client.incr(key))
            if count == 1:
                await self._client.expire(key, max(1, ttl_seconds))
        except RedisError as exc:
            logger.warning("rate limiter Redis error key=%s: %s", key, exc)
            raise RateLimiterUnavailable("Redis rate limiter is unreachable.") from exc

        if count > limit:
            try:
                ttl = await self._client.ttl(key)
            except RedisError as exc:
                raise RateLimiterUnavailable("Redis rate limiter is unreachable.") from exc
            retry_after = ttl_seconds if ttl is None or ttl < 0 else max(1, int(ttl))
            raise RateLimitExceeded(
                f"Rate limit exceeded for {label}. Try again in {retry_after} seconds.",
                retry_after_seconds=retry_after,
            )


def _utc_day() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%d")


def _seconds_until_utc_midnight() -> int:
    now = datetime.now(UTC)
    tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return max(1, int((tomorrow - now).total_seconds()))
