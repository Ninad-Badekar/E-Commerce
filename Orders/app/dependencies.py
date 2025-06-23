from app.db import SessionLocal

def get_db():
    db=SessionLocal() # It opens the connection
    try:
        yield db
    finally:
        db.close()