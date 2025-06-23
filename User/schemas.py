from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr
    gender: str
    age: int
    phone_number: str
    nationality: str
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str]
    email: Optional[EmailStr]
    gender: Optional[str]
    age: Optional[int]
    phone_number: Optional[str]
    nationality: Optional[str]
    is_active: Optional[bool]

class UserIn(BaseModel):
    id: int
    username: str
    email: EmailStr
    hashed_password: str
    gender: str
    age: int
    phone_number: str
    nationality: str
    created_at: datetime
    is_active: Optional[bool] = True

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
