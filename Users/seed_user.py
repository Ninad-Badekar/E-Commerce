import random
import string
import time
from faker import Faker
import pymysql
from dotenv import load_dotenv
import os
from urllib.parse import urlparse

load_dotenv()
fake = Faker()

# Constants
TOTAL_USERS = 50000
BATCH_SIZE = 1000

# Parse DB URL from .env
DATABASE_URL = os.getenv("DATABASE_URL")
parsed_url = urlparse(DATABASE_URL)
DB_USER = parsed_url.username
DB_PASSWORD = parsed_url.password
DB_HOST = parsed_url.hostname
DB_PORT = parsed_url.port or 3306
DB_NAME = parsed_url.path.lstrip('/')

def random_password(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_user(user_id):
    return (
        user_id,
        fake.user_name(),
        fake.unique.email(),
        random_password(),
        random.choice(["male", "female", "non-binary"]),
        random.randint(18, 60),
        fake.unique.msisdn()[0:10],
        fake.country(),
        1  # is_active (1=True)
    )

def insert_batch(connection, batch):
    with connection.cursor() as cursor:
        sql = """
            INSERT INTO users (id, username, email, password, gender, age, phone_number, nationality, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.executemany(sql, batch)
    connection.commit()

if __name__ == "__main__":
    print(f"Starting to insert {TOTAL_USERS} users into MySQL...")

    connection = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT,
        autocommit=False
    )

    try:
        start_id = 1
        for i in range(0, TOTAL_USERS, BATCH_SIZE):
            fake.unique.clear()  # Reset uniqueness to avoid duplicates
            batch = [generate_user(start_id + j) for j in range(BATCH_SIZE)]
            insert_batch(connection, batch)
            print(f"Inserted users {start_id} to {start_id + BATCH_SIZE - 1}")
            start_id += BATCH_SIZE
            time.sleep(0.5)  # Optional pacing
        print("✅ Done seeding users into MySQL!")
    finally:
        connection.close()
