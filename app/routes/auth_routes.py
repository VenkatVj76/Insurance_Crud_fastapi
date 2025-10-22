# app/routes/auth_routes.py
from fastapi import APIRouter, HTTPException, Depends
from app.database import db
from app.schemas import UserCreate, Token, UserOut
from app.utils import serialize_doc
from app.auth import hash_password, verify_password, create_access_token
from bson import ObjectId

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserOut)
async def register_user(payload: UserCreate):
    existing = await db.users.find_one({"email": payload.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user_doc = {
        "email": payload.email,
        "password": hash_password(payload.password),
        "created_at": __import__("datetime").datetime.utcnow()
    }
    res = await db.users.insert_one(user_doc)
    user = await db.users.find_one({"_id": res.inserted_id})
    return serialize_doc(user)

@router.post("/login", response_model=Token)
async def login(payload: UserCreate):
    user = await db.users.find_one({"email": payload.email})
    if not user or not verify_password(payload.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token({"sub": str(user["_id"])})
    return {"access_token": access_token, "token_type": "bearer"}
