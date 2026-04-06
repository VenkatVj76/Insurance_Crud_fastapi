import json
from typing import Any, Optional
from fastapi import Request, HTTPException
import app.redis_client as rc

# --- CACHE UTILITIES ---

async def get_cache(key: str) -> Optional[Any]:
    """Retrieve data from Redis cache."""
    if not rc.redis_client:
        return None
    val = await rc.redis_client.get(key)
    if val:
        return json.loads(val)
    return None

async def set_cache(key: str, value: Any, expire: int = 300) -> None:
    """Store data in Redis cache with an expiration time."""
    if rc.redis_client:
        await rc.redis_client.set(key, json.dumps(value), ex=expire)

async def invalidate_cache(key: str) -> None:
    """Delete a key from Redis to invalidate the cache."""
    if rc.redis_client:
        await rc.redis_client.delete(key)

async def invalidate_pattern(pattern: str) -> None:
    """Delete all keys matching a specific pattern."""
    if rc.redis_client:
        cursor = 0
        while True:
            cursor, keys = await rc.redis_client.scan(cursor=cursor, match=pattern, count=100)
            if keys:
                await rc.redis_client.delete(*keys)
            if cursor == 0:
                break

# --- RATE LIMITER DEPENDENCY ---

class RateLimiter:
    """
    A custom rate limiting dependency for FastAPI using Redis.
    Limits requests based on the client IP address and route.
    """
    def __init__(self, times: int = 5, seconds: int = 60):
        self.times = times
        self.seconds = seconds

    async def __call__(self, request: Request):
        if not rc.redis_client:
            return  # Fail open if Redis is not connected
        
        client_ip = request.client.host if request.client else "unknown"
        # We rate limit per IP per endpoint route
        key = f"rate_limit:{client_ip}:{request.url.path}"
        
        # Atomically increment the request count for this key
        current_count = await rc.redis_client.incr(key)
        
        if current_count == 1:
            # First request in the time window: set the key's TTL (Time To Live)
            await rc.redis_client.expire(key, self.seconds)
            
        if current_count > self.times:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Max {self.times} requests per {self.seconds} seconds."
            )
