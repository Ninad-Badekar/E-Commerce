from sqlalchemy.orm import Session
import Users.models, Users.schemas, Users.utils

def get_user_by_email(db: Session, email: str):
    return db.query(Users.models.User).filter(Users.models.User.email == email).first()

def get_user_by_id(db: Session, user_id: int):
    return db.query(Users.models.User).filter(Users.models.User.id == user_id).first()

def create_user(db: Session, user: Users.schemas.UserCreate):
    hashed = Users.utils.hash_password(user.password)
    db_user = Users.models.User(**user.dict(exclude={"password"}), hashed_password=hashed)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_user_direct(db: Session, user: Users.schemas.UserIn):
    db_user = Users.models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, db_user: Users.models.User, updates: Users.schemas.UserUpdate):
    for field, value in updates.dict(exclude_unset=True).items():
        setattr(db_user, field, value)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, db_user: Users.models.User):
    db.delete(db_user)
    db.commit()
