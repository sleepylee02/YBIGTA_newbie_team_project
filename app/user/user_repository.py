from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, Column, String
from database.mysql_connection import Base  # same Base as before
from app.user.user_schema import User as PydanticUser  # your Pydantic user schema

# SQLAlchemy ORM model for the "users" table
class User(Base):
    __tablename__ = "users"

    # Match the test's CREATE TABLE columns exactly
    email = Column(String, primary_key=True)
    password = Column(String, nullable=False)
    username = Column(String, nullable=False)

class UserRepository:
    def __init__(self, db_session: Session) -> None:
        self.db_session = db_session

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db_session.execute(
            select(User).where(User.email == email)
        ).scalars().first()

    def save_user(self, user: PydanticUser) -> User:
        """Insert or update a user (based on email)"""
        # Check if there's an existing user
        existing_user = self.get_user_by_email(user.email)
        if existing_user:
            # Update existing
            existing_user.password = user.password
            existing_user.username = user.username
            self.db_session.commit()
            self.db_session.refresh(existing_user)
            return existing_user
        else:
            # Insert new
            new_user = User(
                email=user.email,
                password=user.password,
                username=user.username
            )
            self.db_session.add(new_user)
            self.db_session.commit()
            self.db_session.refresh(new_user)
            return new_user

    def delete_user(self, user: PydanticUser) -> Optional[User]:
        orm_user = self.get_user_by_email(user.email)
        if orm_user:
            self.db_session.delete(orm_user)
            self.db_session.commit()
            return orm_user
        return None

    def get_users(self) -> List[User]:
        return self.db_session.execute(select(User)).scalars().all()