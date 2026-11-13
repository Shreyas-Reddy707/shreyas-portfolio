import asyncio
import json
import logging
import secrets
import time
from datetime import UTC, datetime
from typing import Any

import redis.asyncio as aioredis
from fastapi import HTTPException, status

from app.core.config import settings

logger = logging.getLogger(__name__)

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


_RATE_LIMIT_LUA = """
local key = KEYS[1]
local now = tonumber(ARGV[1])
local window_start = tonumber(ARGV[2])
local limit = tonumber(ARGV[3])
local window_seconds = tonumber(ARGV[4])
local member = ARGV[5]

redis.call('zremrangebyscore', key, 0, window_start)
local current_count = tonumber(redis.call('zcard', key))

if current_count >= limit then
    return {0, current_count}
else
    redis.call('zadd', key, now, member)
    redis.call('expire', key, window_seconds)
    return {1, current_count + 1}
end
"""

_AI_CONSUME_BUDGET_LUA = """
local key = KEYS[1]
local tokens = tonumber(ARGV[1])
local budget = tonumber(ARGV[2])

local current = tonumber(redis.call('get', key) or '0')
if (current + tokens) <= budget then
    local new_val = redis.call('incrby', key, tokens)
    if current == 0 then
        redis.call('expire', key, 86400)
    end
    return 1
else
    return 0
end
"""


async def check_rate_limit(
    scope: str,
    ip_sha256: str,
    limit: int,
    window_seconds: int,
) -> tuple[bool, int]:
    """Enforce an atomic Redis sorted-set sliding-window rate limit via Lua script."""
    client = await get_redis()
    key = f"rl:{scope}:{ip_sha256}"
    now = time.time()
    window_start = now - window_seconds
    member = f"{now:.6f}:{secrets.token_hex(4)}"

    res = await client.eval(
        _RATE_LIMIT_LUA,
        1,
        key,
        now,
        window_start,
        limit,
        window_seconds,
        member,
    )
    allowed, count = int(res[0]), int(res[1])

    if allowed == 0:
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

    remaining = max(0, limit - count)
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
    """Purge cached public portfolio and manifest payloads and advance shared cache generation."""
    client = await get_redis()
    await client.delete("cache:public:portfolio:v1", "cache:public:manifest:v1")
    try:
        await client.incr("cache:generation:portfolio")
    except Exception as exc:
        logger.debug("Failed to advance portfolio cache generation: %s", exc)
    try:
        from app.services.rag_agent import clear_portfolio_data_cache
        clear_portfolio_data_cache()
    except Exception as exc:
        logger.debug("Failed to clear local portfolio cache: %s", exc)


async def get_portfolio_cache_generation() -> int:
    """Retrieve the current shared portfolio cache generation counter from Redis."""
    try:
        client = await get_redis()
        val = await client.get("cache:generation:portfolio")
        return int(val) if val else 0
    except Exception:
        return 0


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
    """Atomically increment daily AI token usage and trip circuit breaker if budget exceeded."""
    client = await get_redis()
    today = datetime.now(UTC).strftime("%Y-%m-%d")
    key = f"ai:tokens:{today}"
    res = await client.eval(_AI_CONSUME_BUDGET_LUA, 1, key, tokens, settings.DAILY_AI_TOKEN_BUDGET)
    return bool(int(res) == 1)

