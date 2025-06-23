import random
import string
import time
import requests
from faker import Faker

fake = Faker()

API_URL = "http://localhost:8001/register"  # Update if your API runs elsewhere
TOTAL_USERS = 50000
BATCH_SIZE = 1000  # To avoid overwhelming your API

def random_password(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

from uuid import uuid4

def generate_user():
    return {
        "id": str(uuid4()),  # Add this line
        "username": fake.user_name(),
        "email": fake.unique.email(),
        "password": random_password(),
        "gender": random.choice(["male", "female", "non-binary"]),
        "age": random.randint(18, 60),
        "phone_number": fake.unique.msisdn()[0:10],
        "nationality": fake.country(),
        "is_active": True
    }

def send_batch(batch):
    for user in batch:
        try:
            r = requests.post(API_URL, json=user)
            if r.status_code not in (200, 201):
                print(f"Failed ({r.status_code}): {r.json()}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    print(f"Starting to create {TOTAL_USERS} fake users...")
    for i in range(0, TOTAL_USERS, BATCH_SIZE):
        batch = [generate_user() for _ in range(BATCH_SIZE)]
        print(f"Sending users {i + 1} to {i + BATCH_SIZE}")
        send_batch(batch)
        time.sleep(1)  # Give the server some breathing room
    print("✅ Done seeding users!")
