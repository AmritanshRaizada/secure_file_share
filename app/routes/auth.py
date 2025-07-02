from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
import secrets
from typing import Optional

from app.models.user import User
from app.schemas.user import UserCreate, UserInDB, Token, UserLogin
from app.utils.auth import (
    get_password_hash,
    create_access_token,
    verify_password,
    get_current_user,
    get_current_active_user,
)
from app.utils.email import send_verification_email
from app.utils.security import generate_secure_token
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=UserInDB)
async def signup(user_data: UserCreate, db=Depends(get_db)):
    existing_user = await db["users"].find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    hashed_password = get_password_hash(user_data.password)
    verification_token = generate_secure_token()
    
    user_dict = {
        "email": user_data.email,
        "full_name": user_data.full_name,
        "hashed_password": hashed_password,
        "verification_token": verification_token,
        "is_verified": False,
        "is_ops_user": False,
    }
    
    user = await User(db).create_user(user_dict)
    
    # Send verification email
    verification_url = f"{settings.base_url}/auth/verify-email?token={verification_token}"
    await send_verification_email(user_data.email, verification_url)
    
    return user

@router.get("/verify-email")
async def verify_email(token: str, db=Depends(get_db)):
    success = await User(db).verify_user(token)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token",
        )
    return {"message": "Email verified successfully"}

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    user = await User(db).get_user_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user["is_verified"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not verified",
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/make-ops-user")
async def make_ops_user(
    email: str,
    current_user: dict = Depends(get_current_active_user),
    db=Depends(get_db)
):
    # In a real app, this would be protected by admin privileges
    if not current_user.get("is_ops_user"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform this action",
        )
    
    user = await User(db).make_ops_user(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return {"message": f"User {email} is now an ops user"}

async def get_db():
    from app.config import settings
    import motor.motor_asyncio
    client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.database_name]
    try:
        yield db
    finally:
        client.close()