from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from uuid import uuid4
from datetime import datetime, timedelta
from jose import JWTError, jwt
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(description='User Data')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class User(BaseModel):
    id: str
    username: str
    email: EmailStr
    password: str
    gender: str
    age: int
    phone_number: str
    nationality: str
    is_active: Optional[bool] = True

users: List[User] = []

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload["sub"]

@app.post("/register", response_model=User)
def register(user: User):
    if any(u.email == user.email for u in users):
        raise HTTPException(status_code=400, detail="Email already exists")
    users.append(user)
    return user

@app.post("/token")
def generate_token(form_data: OAuth2PasswordRequestForm = Depends()):
    for u in users:
        if u.email == form_data.username and u.password == form_data.password:
            token = create_access_token({"sub": u.email})
            return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/users/", response_model=List[User])
def list_users(current_user: str = Depends(get_current_user)):
    return users

@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: str, current_user: str = Depends(get_current_user)):
    for user in users:
        if user.id == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")

@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: str, updated: User, current_user: str = Depends(get_current_user)):
    for i, user in enumerate(users):
        if user.id == user_id:
            updated.id = user.id
            users[i] = updated
            return updated
    raise HTTPException(status_code=404, detail="User not found")

@app.delete("/users/{user_id}")
def delete_user(user_id: str, current_user: str = Depends(get_current_user)):
    for i, user in enumerate(users):
        if user.id == user_id:
            users.pop(i)
            return {"detail": f"User {user_id} deleted successfully"}
    raise HTTPException(status_code=404, detail="User not found")

# Preloaded admin user
users.append(User(
    id=str(uuid4()),
    username="admin",
    email="admin@example.com",
    password="adminpass",
    gender="non-binary",
    age=35,
    phone_number="9999999999",
    nationality="Adminland",
    is_active=True
))
