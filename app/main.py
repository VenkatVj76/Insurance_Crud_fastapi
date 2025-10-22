# app/main.py
from fastapi import FastAPI
from app.database import db
from app.routes import auth_routes, employee_routes, vehicle_routes
import asyncio

app = FastAPI(title="FastAPI MongoDB Example")

app.include_router(auth_routes.router)
app.include_router(employee_routes.router)
app.include_router(vehicle_routes.router)

# create indexes on startup
@app.on_event("startup")
async def startup_db():
    await db.users.create_index("email", unique=True)
