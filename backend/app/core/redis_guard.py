import asyncio
import json
import secrets
import time
from datetime import UTC, datetime
from typing import Any

import redis.asyncio as aioredis
from fastapi import HTTPException, status

from app.core.config import settings

_redis_client: aioredis.Redis | None = None
_redis_loop: asyncio.AbstractEventLoop | None = None


async def get_redis() -> aioredis.Redis:
    """Return an async Redis client bound to the current running event loop."""
    global _redis_client, _redis_loop
    current_loop = asyncio.get_running_loop()
    if _redis_client is None or _redis_loop is not current_loop:
        _redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
        _redis_loop = current_loop
    return _redis_client


async def check_rate_limit(
    scope: str,
    ip_sha256: str,
    limit: int,
    window_seconds: int,
) -> tuple[bool, int]:
    """Enforce an atomic Redis sorted-set sliding-window rate limit."""
    client = await get_redis()
    key = f"rl:{scope}:{ip_sha256}"
    now = time.time()
    window_start = now - window_seconds
    member = f"{now:.6f}:{secrets.token_hex(4)}"

    async with client.pipeline(transaction=True) as pipe:
        pipe.zremrangebyscore(key, 0, window_start)
        pipe.zcard(key)
        results = await pipe.execute()

    current_count = int(results[1])
    if current_count >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error_code": "RATE_LIMIT_EXCEEDED",
                "message": (
                    f"Too many requests from this network. Please wait "
                    f"{window_seconds} seconds before retrying."
                ),
                "retry_after_seconds": window_seconds,
            },
        )

    async with client.pipeline(transaction=True) as pipe:
        pipe.zadd(key, {member: now})
        pipe.expire(key, window_seconds)
        await pipe.execute()

    remaining = max(0, limit - (current_count + 1))
    return True, remaining


async def get_cached_json(key: str) -> dict[str, Any] | None:
    """Fetch and deserialize a cached JSON object from Redis."""
    client = await get_redis()
    raw = await client.get(key)
    if not raw:
        return None
    return json.loads(raw)


async def set_cached_json(
    key: str,
    payload: dict[str, Any],
    ttl_seconds: int = 3600,
) -> None:
    """Serialize and store a JSON object in Redis with an expiration TTL."""
    client = await get_redis()
    await client.set(key, json.dumps(payload, default=str), ex=ttl_seconds)


async def invalidate_portfolio_cache() -> None:
    """Purge cached public portfolio and manifest payloads."""
    client = await get_redis()
    await client.delete("cache:public:portfolio:v1", "cache:public:manifest:v1")


async def acquire_webhook_delivery_lock(
    delivery_id: str,
    ttl_seconds: int = 86400,
) -> bool:
    """Acquire an idempotency lock for a GitHub X-GitHub-Delivery UUID."""
    client = await get_redis()
    key = f"webhook:lock:{delivery_id}"
    acquired = await client.set(key, "1", nx=True, ex=ttl_seconds)
    return bool(acquired)


async def consume_ai_tokens(tokens: int) -> bool:
    """Increment daily AI token usage and trip circuit breaker if budget exceeded."""
    client = await get_redis()
    today = datetime.now(UTC).strftime("%Y-%m-%d")
    key = f"ai:tokens:{today}"
    new_total = await client.incrby(key, tokens)
    if new_total == tokens:
        await client.expire(key, 86400)
    return int(new_total) <= settings.DAILY_AI_TOKEN_BUDGET

