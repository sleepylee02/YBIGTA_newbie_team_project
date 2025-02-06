from fastapi import Depends
from app.user.user_repository import UserRepository
from app.user.user_service import UserService
from database.mysql_connection import SessionLocal

def get_user_repository() -> UserRepository:
    db_session = SessionLocal() 
    try:
        return UserRepository(db_session)
    finally:
        db_session.close()

def get_user_service(repo: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(repo)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()