# app/main.py
from fastapi import FastAPI
from app.database import db
from app.routes import auth_routes, employee_routes, vehicle_routes
from app.redis_client import init_redis, close_redis
import app.redis_client as rc
import asyncio
import time
import json

app = FastAPI(title="FastAPI MongoDB Example")

app.include_router(auth_routes.router)
app.include_router(employee_routes.router)
app.include_router(vehicle_routes.router)

@app.get("/speedtest", tags=["benchmark"])
async def speed_test():
    # 1. MongoDB Cold Read
    start_mongo = time.time()
    cursor = db.employees.find().limit(2000)
    mongo_data = []
    async for d in cursor:
        d["_id"] = str(d["_id"])
        mongo_data.append(d)
    mongo_time = (time.time() - start_mongo) * 1000

    # 2. Setup Redis key
    if not rc.redis_client:
        return {"error": "Redis not connected"}
    
    dummy_key = "benchmark:speedtest:dummy"
    await rc.redis_client.set(dummy_key, json.dumps(mongo_data), ex=60)
    
    # 3. Redis Hot Read
    start_redis = time.time()
    val = await rc.redis_client.get(dummy_key)
    redis_time = (time.time() - start_redis) * 1000

    return {
        "records_fetched": len(mongo_data),
        "mongo_time_ms": round(mongo_time, 2),
        "redis_time_ms": round(redis_time, 2),
        "comparison": f"Redis is {round(mongo_time / redis_time, 2)}x faster" if redis_time > 0 else "Infinity"
    }

# create indexes on startup
@app.on_event("startup")
async def startup_db():
    await db.users.create_index("email", unique=True)
    await init_redis()

@app.on_event("shutdown")
async def shutdown_events():
    await close_redis()
