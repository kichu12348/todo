from pydantic import BaseModel
import datetime
from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str
    
class Token(BaseModel):
    access_token: str
    token_type: str="bearer"

class TodoCreate(BaseModel):
    title: str
    description: Optional[str] = None 
    due_time: Optional[datetime.datetime] = None
    user_id: int

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    due_time: Optional[datetime.datetime] = None

class TodoDelete(BaseModel):
    id: int



