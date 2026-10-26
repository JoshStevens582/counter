from __future__ import annotations

import logging

from redis.asyncio import Redis

from counter.config import Settings

logger = logging.getLogger("counter.redis")


class RedisRequiredError(RuntimeError):
    """REDIS_REQUIRED is set and Redis did not answer the startup ping."""


async def connect_redis(settings: Settings) -> Redis | None:
    client: Redis = Redis.from_url(settings.redis_url, decode_responses=True)
    try:
        await client.ping()
    except Exception as exc:
        await client.aclose()
        if settings.redis_required:
            raise RedisRequiredError(
                "Redis is required but did not answer the startup ping."
            ) from exc
        logger.warning(
            "Redis unavailable (%s); rate-limited routes return 503 when fail-closed.",
            type(exc).__name__,
        )
        return None
    logger.info("Redis answered the startup ping.")
    return client
