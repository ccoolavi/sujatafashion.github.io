"""Sujata Fashion Backend — Main API Application."""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from datetime import timedelta
import json
import os

from .config import settings
from .database import get_connection, init_db
from .auth import (
    UserCreate, UserLogin, UserResponse, Token,
    verify_password, get_password_hash,
    create_access_token, decode_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

# CORS — allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)


# --- Dependency: Get current user from token ---
async def get_current_user(token: str = Depends(lambda: None)):
    """Extract user from Authorization header."""
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    return payload


# --- Auth Endpoints ---

@app.on_event("startup")
async def startup():
    init_db()


@app.post("/api/auth/register", response_model=UserResponse)
async def register(user: UserCreate):
    """Register a new user account."""
    conn = get_connection()
    try:
        # Check if user exists
        existing = conn.execute(
            "SELECT id FROM users WHERE email = ? OR username = ?",
            (user.email, user.username)
        ).fetchone()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email or username already registered",
            )

        hashed_pw = get_password_hash(user.password)
        cursor = conn.execute(
            """INSERT INTO users (email, username, hashed_password, full_name)
               VALUES (?, ?, ?, ?)""",
            (user.email, user.username, hashed_pw, user.full_name)
        )
        conn.commit()

        user_id = cursor.lastrowid
        return UserResponse(
            id=user_id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            role="user",
            is_active=True,
        )
    finally:
        conn.close()


@app.post("/api/auth/login", response_model=Token)
async def login(login_data: UserLogin):
    """Authenticate user and return JWT token."""
    conn = get_connection()
    try:
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (login_data.username,)
        ).fetchone()
        
        if not user or not verify_password(login_data.password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )

        if not user["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled",
            )

        access_token = create_access_token(
            data={"sub": user["username"], "user_id": user["id"], "role": user["role"]},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        return Token(access_token=access_token)
    finally:
        conn.close()


@app.get("/api/auth/me", response_model=UserResponse)
async def get_me(token: str = Depends(get_current_user)):
    """Get current authenticated user details."""
    conn = get_connection()
    try:
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (token.get("sub"),)
        ).fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return UserResponse(
            id=user["id"],
            email=user["email"],
            username=user["username"],
            full_name=user["full_name"],
            role=user["role"],
            is_active=bool(user["is_active"]),
        )
    finally:
        conn.close()


# --- Public API Endpoints ---

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "message": "Sujata Fashion API is running"}


@app.get("/api/inquiries")
async def get_inquiries():
    """Get all inquiries (public for now, restrict later)."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM inquiries ORDER BY created_at DESC LIMIT 50"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


@app.post("/api/inquiries")
async def create_inquiry(
    name: str, phone: str, email: str,
    course: str = None, message: str = None,
    preferred_date: str = None
):
    """Submit a new course inquiry."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            """INSERT INTO inquiries (name, phone, email, course, preferred_date, message)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (name, phone, email, course, preferred_date, message)
        )
        conn.commit()
        return {"status": "ok", "id": cursor.lastrowid}
    finally:
        conn.close()


# --- Product API Endpoints ---

@app.get("/api/products")
async def list_products(category: str = None, type: str = None, active_only: bool = True):
    """List products with optional filters."""
    conn = get_connection()
    try:
        query = "SELECT * FROM products WHERE 1=1"
        params = []
        if active_only:
            query += " AND is_active = 1"
        if category:
            query += " AND category = ?"
            params.append(category)
        if type:
            query += " AND type = ?"
            params.append(type)
        query += " ORDER BY created_at DESC"
        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


@app.get("/api/products/{product_id}")
async def get_product(product_id: int):
    """Get a single product by ID."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM products WHERE id = ?", (product_id,)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Product not found")
        return dict(row)
    finally:
        conn.close()


@app.post("/api/products", status_code=201)
async def create_product(
    name: str, category: str = None, price: float = None,
    description: str = None, image_url: str = None, type: str = "shop"
):
    """Create a new product entry."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            """INSERT INTO products (name, category, price, description, image_url, type)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (name, category, price, description, image_url, type)
        )
        conn.commit()
        product_id = cursor.lastrowid
        row = conn.execute(
            "SELECT * FROM products WHERE id = ?", (product_id,)
        ).fetchone()
        return dict(row)
    finally:
        conn.close()


@app.put("/api/products/{product_id}")
async def update_product(
    product_id: int, name: str = None, category: str = None,
    price: float = None, description: str = None,
    image_url: str = None, type: str = None, is_active: bool = None
):
    """Update an existing product."""
    conn = get_connection()
    try:
        existing = conn.execute(
            "SELECT * FROM products WHERE id = ?", (product_id,)
        ).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Product not found")

        fields = {}
        if name is not None: fields["name"] = name
        if category is not None: fields["category"] = category
        if price is not None: fields["price"] = price
        if description is not None: fields["description"] = description
        if image_url is not None: fields["image_url"] = image_url
        if type is not None: fields["type"] = type
        if is_active is not None: fields["is_active"] = 1 if is_active else 0

        if not fields:
            return dict(existing)

        set_clause = ", ".join(f"{k} = ?" for k in fields)
        values = list(fields.values()) + [product_id]
        conn.execute(
            f"UPDATE products SET {set_clause} WHERE id = ?", values
        )
        conn.commit()

        row = conn.execute(
            "SELECT * FROM products WHERE id = ?", (product_id,)
        ).fetchone()
        return dict(row)
    finally:
        conn.close()


@app.delete("/api/products/{product_id}")
async def delete_product(product_id: int):
    """Delete a product by ID."""
    conn = get_connection()
    try:
        existing = conn.execute(
            "SELECT * FROM products WHERE id = ?", (product_id,)
        ).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Product not found")
        conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        return {"status": "ok", "deleted_id": product_id}
    finally:
        conn.close()


@app.post("/api/setup-admin")
async def setup_admin():
    """Create default admin account (first-run setup)."""
    conn = get_connection()
    try:
        existing = conn.execute("SELECT id FROM users WHERE role = 'admin'").fetchone()
        if existing:
            return {"status": "already_exists", "message": "Admin account already exists"}

        hashed_pw = get_password_hash("admin123")
        conn.execute(
            """INSERT INTO users (email, username, hashed_password, full_name, role)
               VALUES (?, ?, ?, ?, ?)""",
            ("admin@sujatafashion.com", "admin", hashed_pw, "Admin", "admin")
        )
        conn.commit()
        return {
            "status": "created",
            "message": "Default admin created. Username: admin, Password: admin123",
            "warning": "CHANGE THIS PASSWORD IMMEDIATELY"
        }
    finally:
        conn.close()


# Serve static frontend files (for production deployment)
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)))
if os.path.exists(os.path.join(static_dir, "index.html")):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=settings.server_reload,
    )
