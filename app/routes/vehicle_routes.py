# app/routes/vehicle_routes.py
from fastapi import APIRouter, Depends, HTTPException
from app.database import db
from app.schemas import VehicleCreate, VehicleOut, InsuranceCreate, InsuranceOut
from app.utils import serialize_doc
from app.auth import get_current_user
from bson import ObjectId

router = APIRouter(prefix="/vehicles", tags=["vehicles"])

# Insurance company endpoints
@router.post("/insurance", response_model=InsuranceOut)
async def create_insurance(payload: InsuranceCreate, current=Depends(get_current_user)):
    existing = await db.insurance_companies.find_one({"name": payload.name})
    if existing:
        raise HTTPException(400, "Insurance company already registered")
    res = await db.insurance_companies.insert_one(payload.dict())
    insurance = await db.insurance_companies.find_one({"_id": res.inserted_id})
    return serialize_doc(insurance.dict())

@router.get("/insurance", response_model=list[InsuranceOut])
async def list_insurance(current=Depends(get_current_user)):
    out=[]
    async for doc in db.insurance_companies.find():
        out.append(serialize_doc(doc))
    return out

# Vehicle endpoints
@router.post("/", response_model=VehicleOut)
async def create_vehicle(payload: VehicleCreate, current=Depends(get_current_user)):
    existing = await db.vehicles.find_one({"vehicle_number": payload.vehicle_number})
    if existing:
        raise HTTPException(400, "Vehicle already insured")
    if payload.insurance_id:
        existing = await db.insurance_companies.find_one({"_id": payload.insurance_id})
        if not existing:
            raise HTTPException(404, "Insurance company not found")
    existing = await db.employees.find_one({"_id": payload.owner_employee_id})
    if not existing:
        raise HTTPException(404, "Owner employee not found")
    res = await db.vehicles.insert_one(payload.dict())
    v = await db.vehicles.find_one({"_id": res.inserted_id})
    return serialize_doc(v)

@router.get("/", response_model=list[VehicleOut])
async def list_vehicles(current=Depends(get_current_user)):
    out=[]
    async for v in db.vehicles.find():
        out.append(serialize_doc(v))
    return out

@router.put("/{vehicle_id}", response_model=VehicleOut)
async def update_vehicle(vehicle_id: str, payload: VehicleCreate, current=Depends(get_current_user)):
    oid = ObjectId(vehicle_id)
    update_data = {k:v for k,v in payload.dict().items() if v is not None}
    result = await db.vehicles.update_one({"_id": oid}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(404,"Vehicle not found")
    doc = await db.vehicles.find_one({"_id": oid})
    return serialize_doc(doc)