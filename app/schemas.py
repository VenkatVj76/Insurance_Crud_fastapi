# app/schemas.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: str = Field(..., alias="_id")
    email: EmailStr

    model_config = {"populate_by_name": True}

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class EmployeeCreate(BaseModel):
    name: str
    position: Optional[str]
    email: Optional[EmailStr]

class EmployeeOut(EmployeeCreate):
    id: str = Field(..., alias="_id")

class InsuranceCreate(BaseModel):
    name: str
    contact: Optional[str]

class InsuranceOut(InsuranceCreate):
    id: str = Field(..., alias="_id")

class VehicleCreate(BaseModel):
    owner_employee_id: str  # foreign key reference to employees._id
    vehicle_type: str  # "car" or "bike"
    vehicle_make: str
    vehicle_model: Optional[str]
    vehicle_year: int
    vehicle_number: str
    insurance_id: Optional[str]  # foreign key to insurance_companies._id

class VehicleOut(VehicleCreate):
    id: str = Field(..., alias="_id")
