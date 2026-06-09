"""Sujata Fashion Backend — Auth models and utilities."""
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field
import os
import json

from .config import settings

SECRET_KEY = settings.secret_key
ALGORITHM = settings.auth_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Pydantic Models ---

class UserCreate(BaseModel):
    email: str
    username: str
    password: str
    full_name: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    role: str
    is_active: bool

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: str | None = None

class InquiryCreate(BaseModel):
    """Request model for creating a course inquiry."""
    name: str = Field(..., min_length=2, max_length=100, description="Full name of the inquirer")
    phone: str = Field(..., min_length=7, max_length=20, description="Contact phone number")
    email: EmailStr = Field(..., description="Email address")
    course: str | None = Field(None, max_length=200, description="Course of interest")
    message: str | None = Field(None, max_length=2000, description="Additional message")
    preferred_date: str | None = Field(None, max_length=50, description="Preferred session date")

class InquiryResponse(BaseModel):
    """Response model for an inquiry."""
    id: int
    name: str
    phone: str
    email: str
    course: str | None = None
    message: str | None = None
    preferred_date: str | None = None
    source: str = "website"
    created_at: str

class TestimonialCreate(BaseModel):
    """Request model for creating a testimonial."""
    name: str = Field(..., min_length=2, max_length=200, description="Student name")
    course: str | None = Field(None, max_length=200, description="Course taken")
    review: str | None = Field(None, max_length=5000, description="Testimonial text")
    video_url: str | None = Field(None, max_length=500, description="YouTube video URL")
    rating: int | None = Field(5, ge=1, le=5, description="Rating (1-5)")

class TestimonialResponse(BaseModel):
    """Response model for a testimonial."""
    id: int
    name: str
    course: str | None = None
    review: str | None = None
    video_url: str | None = None
    rating: int = 5
    is_active: int = 1
    created_at: str

# --- Password Utilities ---

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# --- JWT Utilities ---

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
