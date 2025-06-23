import requests
from faker import Faker
import random
from tqdm import tqdm

API_URL = "http://localhost:8000/register"

fake = Faker()

def generate_random_user():
    return {
        "username": fake.user_name(),
        "email": fake.unique.email(),
        "password": "Test1234@",  # simple dummy password
        "gender": random.choice(["Male", "Female", "Other"]),
        "age": random.randint(18, 60),
        "phone_number": fake.unique.phone_number(),
        "nationality": fake.country()
    }

def bulk_register(count=10000):
    for _ in tqdm(range(count), desc="Sending data to API"):
        user_data = generate_random_user()
        try:
            response = requests.post(API_URL, json=user_data)
            if response.status_code != 200:
                print(f"Failed ({response.status_code}): {response.text}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    bulk_register()
