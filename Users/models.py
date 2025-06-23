from sqlalchemy import Column, String, Integer, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    gender = Column(String(50))
    age = Column(Integer)
    phone_number = Column(String(20))
    nationality = Column(String(100))
    is_active = Column(Boolean, default=True)

DATABASE_URL = os.getenv("DATABASE_URL")
parsed = urlparse(DATABASE_URL)
dialect = "mysql+pymysql"
engine_url = f"{dialect}://{parsed.username}:{parsed.password}@{parsed.hostname}:{parsed.port or 3306}{parsed.path}"

engine = create_engine(engine_url)

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("✅ Users table created successfully.")

