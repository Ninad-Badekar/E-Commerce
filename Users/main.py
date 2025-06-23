# users/main.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from dotenv import load_dotenv
from urllib.parse import urlparse
import pymysql

# External imports
from Products.schemas import ProductSummary
from Orders.app.orders.schemas import OrderResponse, OrderStatusUpdate, CartItemResponse

load_dotenv()
app = FastAPI(description='User Data')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Parse DB URL
DATABASE_URL = os.getenv("DATABASE_URL")
parsed_url = urlparse(DATABASE_URL)
DB_USER = parsed_url.username
DB_PASSWORD = parsed_url.password
DB_HOST = parsed_url.hostname
DB_PORT = parsed_url.port or 3306
DB_NAME = parsed_url.path.lstrip('/')

# DB connection helper
connection = pymysql.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME,
    port=DB_PORT,
    autocommit=True
)

# User schema
class User(BaseModel):
    id: int
    username: str
    email: EmailStr
    password: str
    gender: str
    age: int
    phone_number: str
    nationality: str
    is_active: Optional[bool] = True

# Load users from DB
def fetch_users():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        return [User(**{
            "id": row[0], "username": row[1], "email": row[2], "password": row[3],
            "gender": row[4], "age": row[5], "phone_number": row[6],
            "nationality": row[7], "is_active": bool(row[8])
        }) for row in rows]

def insert_user(user: User):
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO users (id, username, email, password, gender, age, phone_number, nationality, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (user.id, user.username, user.email, user.password, user.gender, user.age,
              user.phone_number, user.nationality, int(user.is_active)))

# In-memory stores
users: List[User] = fetch_users()
products: List[ProductSummary] = []
carts: List[CartItemResponse] = []
orders: List[OrderResponse] = []

user_id_counter = max((user.id for user in users), default=0) + 1

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

def get_user_email_by_id(user_id: int) -> Optional[str]:
    for user in users:
        if user.id == user_id:
            return user.email
    return None

@app.post("/register", response_model=User)
def register(user: User):
    global user_id_counter
    if any(u.email == user.email for u in users):
        raise HTTPException(status_code=400, detail="Email already exists")
    user.id = user_id_counter
    user_id_counter += 1
    insert_user(user)
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
def get_user(user_id: int, current_user: str = Depends(get_current_user)):
    for user in users:
        if user.id == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")

@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, updated: User, current_user: str = Depends(get_current_user)):
    for i, user in enumerate(users):
        if user.id == user_id:
            updated.id = user.id
            users[i] = updated
            insert_user(updated)  # naive replacement
            return updated
    raise HTTPException(status_code=404, detail="User not found")

@app.delete("/users/{user_id}")
def delete_user(user_id: int, current_user: str = Depends(get_current_user)):
    for i, user in enumerate(users):
        if user.id == user_id:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            users.pop(i)
            return {"detail": f"User {user_id} deleted successfully"}
    raise HTTPException(status_code=404, detail="User not found")

@app.get("/users/{user_id}/products", response_model=List[ProductSummary])
def get_user_products(user_id: int, current_user: str = Depends(get_current_user)):
    if current_user != get_user_email_by_id(user_id):
        raise HTTPException(status_code=403, detail="Not authorized")
    return [product for product in products if getattr(product, 'owner_id', None) == user_id]

@app.get("/users/{user_id}/cart", response_model=List[CartItemResponse])
def get_user_cart(user_id: int, current_user: str = Depends(get_current_user)):
    if current_user != get_user_email_by_id(user_id):
        raise HTTPException(status_code=403, detail="Not authorized")
    return [item for item in carts if item.product_id and item.quantity and item.price and item.name and item.product_id > 0]

@app.get("/users/{user_id}/orders", response_model=List[OrderResponse])
def get_user_orders(user_id: int, current_user: str = Depends(get_current_user)):
    if current_user != get_user_email_by_id(user_id):
        raise HTTPException(status_code=403, detail="Not authorized")
    return [order for order in orders if order.order_id and order.total_amount and order.status and order.order_date]
