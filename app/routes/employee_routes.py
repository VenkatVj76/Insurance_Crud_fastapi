# app/routes/employee_routes.py
from fastapi import APIRouter, Depends, HTTPException
from app.database import db
from app.schemas import EmployeeCreate, EmployeeOut
from app.utils import serialize_doc, serialize_docs
from app.auth import get_current_user
from app.redis_utils import RateLimiter, get_cache, set_cache, invalidate_pattern
from bson import ObjectId

router = APIRouter(prefix="/employees", tags=["employees"])

EMPLOYEES_CACHE_PREFIX = "cache:employees:list"

@router.post("/", response_model=EmployeeOut)
async def create_employee(payload: EmployeeCreate, current=Depends(get_current_user)):
    existing = await db.employees.find_one({"email": payload.email})
    if existing:
        raise HTTPException(status_code=400, detail="Employee already registered")
    res = await db.employees.insert_one(payload.dict())
    emp = await db.employees.find_one({"_id": res.inserted_id})
    # Invalidate cache when a new employee is created
    await invalidate_pattern(f"{EMPLOYEES_CACHE_PREFIX}*")
    return serialize_doc(emp)

@router.get("/", response_model=list[EmployeeOut], dependencies=[Depends(RateLimiter(times=10000, seconds=60))])
async def list_employees(skip: int = 0, limit: int = 20, current=Depends(get_current_user)):
    # Check cache first
    cache_key = f"{EMPLOYEES_CACHE_PREFIX}:{skip}:{limit}"
    cached_data = await get_cache(cache_key)
    if cached_data:
        return cached_data

    employees = []
    cursor = db.employees.find().skip(skip).limit(limit)
    async for e in cursor:
        employees.append(serialize_doc(e))
        
    # Save to cache
    await set_cache(cache_key, employees, expire=300)
    return employees

@router.put("/{employee_id}", response_model=EmployeeOut)
async def update_employee(employee_id: str, payload: EmployeeCreate, current=Depends(get_current_user)):
    oid = ObjectId(employee_id)
    update_data = {k:v for k,v in payload.dict().items() if v is not None}
    result = await db.employees.update_one({"_id": oid}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(404, "Employee not found")
    emp = await db.employees.find_one({"_id": oid})
    # Invalidate cache when an employee is updated
    await invalidate_pattern(f"{EMPLOYEES_CACHE_PREFIX}*")
    return serialize_doc(emp)
