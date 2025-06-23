import requests
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from models import Base, User
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD", "adminpass")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

API_BASE = "http://localhost:8001"
USERS_ENDPOINT = f"{API_BASE}/users"
TOKEN_ENDPOINT = f"{API_BASE}/token"

def get_access_token():
    resp = requests.post(TOKEN_ENDPOINT, data={
        "username": ADMIN_EMAIL,
        "password": ADMIN_PASS
    })
    resp.raise_for_status()
    return resp.json()["access_token"]

def fetch_users(token):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(USERS_ENDPOINT, headers=headers)
    resp.raise_for_status()
    return resp.json()

def sync_users():
    session = SessionLocal()
    try:
        token = get_access_token()
        api_users = fetch_users(token)
        existing = {u.email: u for u in session.query(User).all()}

        inserted = 0
        updated = 0

        for u in api_users:
            if u["email"] not in existing:
                session.add(User(
                    id=u["id"],
                    username=u["username"],
                    email=u["email"],
                    password=u["password"],
                    gender=u["gender"],
                    age=u["age"],
                    phone_number=u["phone_number"],
                    nationality=u["nationality"],
                    is_active=u.get("is_active", True)
                ))
                inserted += 1
            else:
                db_user = existing[u["email"]]
                changed = False
                for field in ["username", "password", "gender", "age", "phone_number", "nationality", "is_active"]:
                    if getattr(db_user, field) != u.get(field):
                        setattr(db_user, field, u.get(field))
                        changed = True
                if changed:
                    updated += 1

        session.commit()
        logging.info(f"✅ Inserted {inserted} new, updated {updated} users.")
    except Exception as e:
        logging.exception("❌ Sync failed:")
    finally:
        session.close()

import time

if __name__ == "__main__":
    logging.info("🚀 Starting continuous user sync...")
    while True:
        sync_users()
        time.sleep(60)  # Wait 60 seconds between each sync cycle

