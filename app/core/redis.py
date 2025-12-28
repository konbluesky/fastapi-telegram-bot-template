"""Redis initialization and client management."""

from redis import asyncio as aioredis

from app.core.config import settings

redis_client: aioredis.Redis | None = None


async def init_redis() -> aioredis.Redis:
    """Initialize Redis client."""
    global redis_client
    redis_client = await aioredis.from_url(settings.redis.url, encoding="utf-8", decode_responses=True)
    return redis_client


async def close_redis() -> None:
    """Close Redis connection."""
    global redis_client
    if redis_client is not None:
        await redis_client.close()
        redis_client = None


def get_redis() -> aioredis.Redis:
    """Get Redis client instance."""
    if redis_client is None:
        raise RuntimeError("Redis not initialized. Call init_redis() first.")
    return redis_client
