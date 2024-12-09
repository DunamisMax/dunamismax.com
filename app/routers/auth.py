import os
from fastapi import APIRouter, Depends, HTTPException, Response, Request, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserLogin, UserRead
from app.utils import hash_password, verify_password
from datetime import timedelta, datetime
from app.config import SECRET_KEY

router = APIRouter()


@router.post("/register", response_model=UserRead)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")

    hashed = hash_password(user_data.password)
    new_user = User(username=user_data.username, password_hash=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login")
def login(user_data: UserLogin, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_data.username).first()
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Set session cookie
    # We'll store user_id in a signed cookie. For simplicity: no actual signing here.
    # In production, consider a secure, signed cookie solution or JWT.
    response.set_cookie(
        key="session_user_id", value=str(user.id), httponly=True, max_age=3600
    )
    return {"message": "Login successful"}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("session_user_id")
    return {"message": "Logged out"}
