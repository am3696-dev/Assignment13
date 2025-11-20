from redis import asyncio as aioredis  # Use the modern redis library as a drop-in replacement
from app.core.config import settings

# Create Redis client
redis_client = aioredis.from_url(
    settings.REDIS_URL, 
    encoding="utf-8", 
    decode_responses=True
)

async def add_to_blacklist(token: str, expiration: int = 3600):
    """
    Adds a token to the Redis blacklist with an expiration time.
    """
    await redis_client.setex(token, expiration, "blacklisted")

async def is_blacklisted(token: str) -> bool:
    """
    Checks if a token is in the Redis blacklist.
    """
    exists = await redis_client.get(token)
    return exists is not None

async def close_redis():
    """
    Closes the Redis connection.
    """
    await redis_client.close()