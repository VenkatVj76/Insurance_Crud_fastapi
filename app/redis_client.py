import os
import redis.asyncio as redis
from dotenv import load_dotenv

load_dotenv()

# We fall back to localhost inside a local dev environment if Docker is not used
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Global variables for the Redis connection pool and client
redis_pool: redis.ConnectionPool = None
redis_client: redis.Redis = None

async def init_redis():
    global redis_pool, redis_client
    redis_pool = redis.ConnectionPool.from_url(REDIS_URL, decode_responses=True)
    redis_client = redis.Redis(connection_pool=redis_pool)

async def close_redis():
    global redis_client, redis_pool
    if redis_client:
        await redis_client.aclose()
    if redis_pool:
        await redis_pool.disconnect()
