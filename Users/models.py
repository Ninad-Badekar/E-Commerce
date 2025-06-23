from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True)
    username = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    gender = Column(String(50))
    age = Column(Integer)
    phone_number = Column(String(20))
    nationality = Column(String(100))
    is_active = Column(Boolean, default=True)
