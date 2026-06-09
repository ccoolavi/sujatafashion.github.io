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

class InquiryUpdate(BaseModel):
    """Request model for updating an inquiry."""
    status: str | None = Field(None, max_length=50, description="Inquiry status")
    notes: str | None = Field(None, max_length=2000, description="Admin notes")
    name: str | None = Field(None, min_length=2, max_length=100)
    phone: str | None = Field(None, min_length=7, max_length=20)
    email: str | None = Field(None)
    course: str | None = Field(None, max_length=200)
    message: str | None = Field(None, max_length=2000)
    preferred_date: str | None = Field(None, max_length=50)

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
    status: str = "new"
    notes: str | None = None
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

class UploadResponse(BaseModel):
    """Response model for a Cloudinary image upload."""
    url: str
    public_id: str
    format: str | None = None
    width: int | None = None
    height: int | None = None

# --- Newsletter Subscription Models ---

class SubscribeRequest(BaseModel):
    """Request model for newsletter subscription."""
    email: EmailStr = Field(..., description="Email address to subscribe")
    name: str | None = Field(None, max_length=100, description="Subscriber name")

class SubscriberUpdate(BaseModel):
    """Request model for updating a subscriber."""
    is_active: bool | None = None
    name: str | None = Field(None, max_length=100)
    email: EmailStr | None = None

class SubscriberResponse(BaseModel):
    """Response model for a subscriber."""
    id: int
    email: str
    name: str | None = None
    is_active: int = 1
    source: str = "website"
    created_at: str

# --- Order/Purchase Models ---

class OrderCreate(BaseModel):
    """Request model for creating a purchase order."""
    product_id: int = Field(..., description="ID of the product to purchase")
    customer_name: str = Field(..., min_length=2, max_length=200, description="Customer name")
    customer_phone: str = Field(..., min_length=7, max_length=20, description="Customer phone number")
    customer_email: str | None = Field(None, description="Customer email address")
    quantity: int = Field(1, ge=1, le=100, description="Quantity to purchase")
    total_amount: float | None = Field(None, ge=0, description="Total order amount")
    shipping_address: str | None = Field(None, max_length=500, description="Shipping address")
    notes: str | None = Field(None, max_length=2000, description="Order notes")

class OrderUpdate(BaseModel):
    """Request model for updating an order."""
    customer_name: str | None = Field(None, min_length=2, max_length=200)
    customer_phone: str | None = Field(None, min_length=7, max_length=20)
    customer_email: str | None = None
    quantity: int | None = Field(None, ge=1, le=100)
    total_amount: float | None = Field(None, ge=0)
    shipping_address: str | None = Field(None, max_length=500)
    status: str | None = Field(None, max_length=50, description="Order status")
    notes: str | None = Field(None, max_length=2000)

class OrderResponse(BaseModel):
    """Response model for a purchase order."""
    id: int
    product_id: int
    customer_name: str
    customer_phone: str
    customer_email: str | None = None
    quantity: int = 1
    total_amount: float | None = None
    shipping_address: str | None = None
    status: str = "pending"
    notes: str | None = None
    created_at: str

# --- Wishlist / Favorites Models ---

class WishlistCreate(BaseModel):
    """Request model for adding an item to wishlist."""
    product_id: int = Field(..., description="ID of the product to add")
    customer_name: str = Field(..., min_length=2, max_length=200, description="Customer name")
    customer_phone: str | None = Field(None, min_length=7, max_length=20, description="Customer phone")
    customer_email: str | None = Field(None, description="Customer email")
    notes: str | None = Field(None, max_length=500, description="Optional note about this wishlist item")

class WishlistUpdate(BaseModel):
    """Request model for updating a wishlist item."""
    customer_name: str | None = Field(None, min_length=2, max_length=200)
    customer_phone: str | None = Field(None, min_length=7, max_length=20)
    customer_email: str | None = None
    notes: str | None = Field(None, max_length=500)

class WishlistResponse(BaseModel):
    """Response model for a wishlist item."""
    id: int
    product_id: int
    customer_name: str
    customer_phone: str | None = None
    customer_email: str | None = None
    notes: str | None = None
    created_at: str

# --- Rental Booking Models ---

class BookingCreate(BaseModel):
    """Request model for creating a rental booking."""
    product_id: int = Field(..., description="ID of the product to rent")
    customer_name: str = Field(..., min_length=2, max_length=200, description="Customer name")
    customer_phone: str = Field(..., min_length=7, max_length=20, description="Customer phone number")
    customer_email: str | None = Field(None, description="Customer email address")
    start_date: str = Field(..., max_length=20, description="Rental start date (YYYY-MM-DD)")
    end_date: str = Field(..., max_length=20, description="Rental end date (YYYY-MM-DD)")
    total_amount: float | None = Field(None, ge=0, description="Total rental amount")
    deposit_amount: float | None = Field(0, ge=0, description="Security deposit amount")
    notes: str | None = Field(None, max_length=2000, description="Booking notes")

class BookingUpdate(BaseModel):
    """Request model for updating a booking."""
    customer_name: str | None = Field(None, min_length=2, max_length=200)
    customer_phone: str | None = Field(None, min_length=7, max_length=20)
    customer_email: str | None = None
    start_date: str | None = Field(None, max_length=20)
    end_date: str | None = Field(None, max_length=20)
    total_amount: float | None = Field(None, ge=0)
    deposit_amount: float | None = Field(None, ge=0)
    status: str | None = Field(None, max_length=50, description="Booking status")
    notes: str | None = Field(None, max_length=2000)

class BookingResponse(BaseModel):
    """Response model for a rental booking."""
    id: int
    product_id: int
    customer_name: str
    customer_phone: str
    customer_email: str | None = None
    start_date: str
    end_date: str
    total_amount: float | None = None
    deposit_amount: float = 0
    status: str = "pending"
    notes: str | None = None
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
