from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, status,Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from models.todo import User
from services.db import SessionLocal
import os

secret_key = os.getenv("SECRET_KEY")
algo="HS256"
exp_time = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy() 
    expire = datetime.utcnow() + timedelta(minutes=exp_time) 
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm=algo)

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algo])
        return payload.get("sub") 
    except JWTError:
        return None
    

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username=decode_access_token(token)
    if username is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found",
        )
    return user