from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv
from logger import log

load_dotenv()

DB_URL = f"mysql+pymysql://{os.getenv('DB_User')}:{os.getenv('DB_Password')}@{os.getenv('DB_Host')}:{os.getenv('DB_Port')}/{os.getenv('DB_Name')}"

try:
    engine = create_engine(DB_URL)
    log.info("Database engine created successfully")
except Exception as e:
    log.error(f"Failed to create database engine: {e}")
    raise

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    log.debug("Database session started")
    try:
        yield db
    finally:
        db.close()
        log.debug("Database session closed")
