from sqlalchemy import Column, Integer, String,Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from services.db import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String,nullable=False)

    todos = relationship("Todo", back_populates="owner")


class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(String, index=True)
    due_time= Column(DateTime, nullable=True)
    completed= Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user_id = Column(Integer,ForeignKey("users.id"),nullable=False)
    owner = relationship("User", back_populates="todos")

