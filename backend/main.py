"""Sujata Fashion Backend — Main API Application."""
from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from datetime import timedelta
import json
import os
import cloudinary
import cloudinary.uploader

from .config import settings
from .database import get_connection, init_db
from .auth import (
    UserCreate, UserLogin, UserResponse, Token,
    InquiryCreate, InquiryUpdate, InquiryResponse,
    TestimonialCreate, TestimonialResponse,
    UploadResponse,
    SubscribeRequest, SubscriberUpdate, SubscriberResponse,
    verify_password, get_password_hash,
    create_access_token, decode_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from .utils.cloudinary_service import configure_cloudinary
from .seeder import seed_all, clear_seed_data

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


@app.get("/api/inquiries", response_model=list[InquiryResponse])
async def get_inquiries():
    """Get all inquiries (public for now, restrict later)."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM inquiries ORDER BY created_at DESC LIMIT 50"
        ).fetchall()
        results = []
        for row in rows:
            d = dict(row)
            d["created_at"] = str(d["created_at"]) if d.get("created_at") else ""
            d["status"] = d.get("status", "new")
            d["notes"] = d.get("notes")
            results.append(InquiryResponse(**d))
        return results
    finally:
        conn.close()


@app.post("/api/inquiries", status_code=201)
async def create_inquiry(inquiry: InquiryCreate):
    """Submit a new course inquiry with validated data."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            """INSERT INTO inquiries (name, phone, email, course, preferred_date, message)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (inquiry.name, inquiry.phone, inquiry.email, inquiry.course, inquiry.preferred_date, inquiry.message)
        )
        conn.commit()
        return {"status": "ok", "id": cursor.lastrowid}
    finally:
        conn.close()


@app.get("/api/inquiries/{inquiry_id}", response_model=InquiryResponse)
async def get_inquiry(inquiry_id: int):
    """Get a single inquiry by ID."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM inquiries WHERE id = ?", (inquiry_id,)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Inquiry not found")
        d = dict(row)
        d["created_at"] = str(d["created_at"]) if d.get("created_at") else ""
        d["status"] = d.get("status", "new")
        d["notes"] = d.get("notes")
        return InquiryResponse(**d)
    finally:
        conn.close()


@app.put("/api/inquiries/{inquiry_id}", response_model=InquiryResponse)
async def update_inquiry(inquiry_id: int, inquiry: InquiryUpdate):
    """Update an existing inquiry (status, notes, or contact fields)."""
    conn = get_connection()
    try:
        existing = conn.execute(
            "SELECT * FROM inquiries WHERE id = ?", (inquiry_id,)
        ).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Inquiry not found")

        fields = {}
        if inquiry.status is not None:
            fields["status"] = inquiry.status
        if inquiry.notes is not None:
            fields["notes"] = inquiry.notes
        if inquiry.name is not None:
            fields["name"] = inquiry.name
        if inquiry.phone is not None:
            fields["phone"] = inquiry.phone
        if inquiry.email is not None:
            fields["email"] = inquiry.email
        if inquiry.course is not None:
            fields["course"] = inquiry.course
        if inquiry.message is not None:
            fields["message"] = inquiry.message
        if inquiry.preferred_date is not None:
            fields["preferred_date"] = inquiry.preferred_date

        if not fields:
            d = dict(existing)
            d["created_at"] = str(d["created_at"]) if d.get("created_at") else ""
            d["status"] = d.get("status", "new")
            d["notes"] = d.get("notes")
            return InquiryResponse(**d)

        set_clause = ", ".join(f"{k} = ?" for k in fields)
        values = list(fields.values()) + [inquiry_id]
        conn.execute(
            f"UPDATE inquiries SET {set_clause} WHERE id = ?", values
        )
        conn.commit()

        row = conn.execute(
            "SELECT * FROM inquiries WHERE id = ?", (inquiry_id,)
        ).fetchone()
        d = dict(row)
        d["created_at"] = str(d["created_at"]) if d.get("created_at") else ""
        d["status"] = d.get("status", "new")
        d["notes"] = d.get("notes")
        return InquiryResponse(**d)
    finally:
        conn.close()


@app.delete("/api/inquiries/{inquiry_id}")
async def delete_inquiry(inquiry_id: int):
    """Delete an inquiry by ID."""
    conn = get_connection()
    try:
        existing = conn.execute(
            "SELECT * FROM inquiries WHERE id = ?", (inquiry_id,)
        ).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Inquiry not found")
        conn.execute("DELETE FROM inquiries WHERE id = ?", (inquiry_id,))
        conn.commit()
        return {"status": "ok", "deleted_id": inquiry_id}
    finally:
        conn.close()


# --- Testimonials API Endpoints ---


@app.get("/api/testimonials")
async def list_testimonials(active_only: bool = True, limit: int = 100, offset: int = 0):
    """List testimonials with optional active-only filter and pagination."""
    conn = get_connection()
    try:
        query = "FROM testimonials"
        params = []
        if active_only:
            query += " WHERE is_active = 1"

        # Get total count
        count_row = conn.execute(f"SELECT COUNT(*) as cnt {query}", params).fetchone()
        total = count_row["cnt"] if count_row else 0

        # Fetch paginated results
        full_query = f"SELECT * {query} ORDER BY created_at DESC LIMIT ? OFFSET ?"
        rows = conn.execute(full_query, params + [min(limit, 100), offset]).fetchall()
        results = []
        for row in rows:
            d = dict(row)
            d["created_at"] = str(d["created_at"]) if d.get("created_at") else ""
            results.append(TestimonialResponse(**d))

        from starlette.responses import Response
        import json as _json
        body = _json.dumps([r.model_dump() for r in results], default=str)
        return Response(
            content=body,
            media_type="application/json",
            headers={"X-Total-Count": str(total)}
        )
    finally:
        conn.close()


@app.get("/api/testimonials/{testimonial_id}", response_model=TestimonialResponse)
async def get_testimonial(testimonial_id: int):
    """Get a single testimonial by ID."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM testimonials WHERE id = ?", (testimonial_id,)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Testimonial not found")
        d = dict(row)
        d["created_at"] = str(d["created_at"]) if d.get("created_at") else ""
        return TestimonialResponse(**d)
    finally:
        conn.close()


@app.post("/api/testimonials", status_code=201, response_model=TestimonialResponse)
async def create_testimonial(testimonial: TestimonialCreate):
    """Create a new testimonial."""
    conn = get_connection()
    try:
        cursor = conn.execute(
            """INSERT INTO testimonials (name, course, review, video_url, rating)
               VALUES (?, ?, ?, ?, ?)""",
            (testimonial.name, testimonial.course, testimonial.review, testimonial.video_url, testimonial.rating)
        )
        conn.commit()
        testimonial_id = cursor.lastrowid
        row = conn.execute(
            "SELECT * FROM testimonials WHERE id = ?", (testimonial_id,)
        ).fetchone()
        d = dict(row)
        d["created_at"] = str(d["created_at"]) if d.get("created_at") else ""
        return TestimonialResponse(**d)
    finally:
        conn.close()


@app.put("/api/testimonials/{testimonial_id}", response_model=TestimonialResponse)
async def update_testimonial(
    testimonial_id: int, name: str = None, course: str = None,
    review: str = None, video_url: str = None, rating: int = None,
    is_active: bool = None
):
    """Update an existing testimonial."""
    conn = get_connection()
    try:
        existing = conn.execute(
            "SELECT * FROM testimonials WHERE id = ?", (testimonial_id,)
        ).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Testimonial not found")

        fields = {}
        if name is not None: fields["name"] = name
        if course is not None: fields["course"] = course
        if review is not None: fields["review"] = review
        if video_url is not None: fields["video_url"] = video_url
        if rating is not None: fields["rating"] = rating
        if is_active is not None: fields["is_active"] = 1 if is_active else 0

        if not fields:
            d = dict(existing)
            d["created_at"] = str(d["created_at"]) if d.get("created_at") else ""
            return TestimonialResponse(**d)

        set_clause = ", ".join(f"{k} = ?" for k in fields)
        values = list(fields.values()) + [testimonial_id]
        conn.execute(
            f"UPDATE testimonials SET {set_clause} WHERE id = ?", values
        )
        conn.commit()

        row = conn.execute(
            "SELECT * FROM testimonials WHERE id = ?", (testimonial_id,)
        ).fetchone()
        d = dict(row)
        d["created_at"] = str(d["created_at"]) if d.get("created_at") else ""
        return TestimonialResponse(**d)
    finally:
        conn.close()


@app.delete("/api/testimonials/{testimonial_id}")
async def delete_testimonial(testimonial_id: int):
    """Delete a testimonial by ID."""
    conn = get_connection()
    try:
        existing = conn.execute(
            "SELECT * FROM testimonials WHERE id = ?", (testimonial_id,)
        ).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Testimonial not found")
        conn.execute("DELETE FROM testimonials WHERE id = ?", (testimonial_id,))
        conn.commit()
        return {"status": "ok", "deleted_id": testimonial_id}
    finally:
        conn.close()


# --- Product API Endpoints ---

@app.get("/api/products")
async def list_products(
    category: str = None, type: str = None, active_only: bool = True,
    limit: int = 100, offset: int = 0, search: str = None
):
    """List products with optional filters, pagination, and text search."""
    conn = get_connection()
    try:
        base_query = "FROM products WHERE 1=1"
        params = []
        if active_only:
            base_query += " AND is_active = 1"
        if category:
            base_query += " AND category = ?"
            params.append(category)
        if type:
            base_query += " AND type = ?"
            params.append(type)
        if search:
            base_query += " AND (name LIKE ? OR description LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])

        # Get total count
        count_row = conn.execute(f"SELECT COUNT(*) as cnt {base_query}", params).fetchone()
        total = count_row["cnt"] if count_row else 0

        # Fetch paginated results
        query = f"SELECT * {base_query} ORDER BY created_at DESC LIMIT ? OFFSET ?"
        data_params = params + [min(limit, 100), offset]
        rows = conn.execute(query, data_params).fetchall()
        result = [dict(row) for row in rows]

        # Create response with total count header
        from starlette.responses import Response
        import json as _json
        body = _json.dumps(result, default=str)
        return Response(
            content=body,
            media_type="application/json",
            headers={"X-Total-Count": str(total)}
        )
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


# --- Database Seed/Data Management Endpoints ---


@app.post("/api/seed")
async def seed_database():
    """Seed the database with sample products and testimonials.

    Useful for development, testing, and demo environments.
    Idempotent — call multiple times (will append duplicates intentionally).
    """
    conn = get_connection()
    try:
        result = seed_all(conn)
        return {
            "status": "success",
            "message": f"Seeded {result['products_seeded']} products and {result['testimonials_seeded']} testimonials",
            **result,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Seeding failed: {str(e)}",
        )
    finally:
        conn.close()


@app.delete("/api/seed")
async def clear_database_data():
    """Remove all seed data from products and testimonials tables."""
    conn = get_connection()
    try:
        clear_seed_data(conn)
        return {"status": "success", "message": "Seed data cleared"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Clear failed: {str(e)}",
        )
    finally:
        conn.close()


# --- Newsletter Subscription Endpoints ---


@app.post("/api/subscribe", status_code=201, response_model=SubscriberResponse)
async def subscribe(subscription: SubscribeRequest):
    """Subscribe an email to the newsletter."""
    conn = get_connection()
    try:
        # Check if already subscribed
        existing = conn.execute(
            "SELECT * FROM subscriptions WHERE email = ?",
            (subscription.email,)
        ).fetchone()
        if existing:
            # Re-activate if previously unsubscribed
            conn.execute(
                "UPDATE subscriptions SET is_active = 1, name = COALESCE(?, name) WHERE id = ?",
                (subscription.name, existing["id"])
            )
            conn.commit()
            row = conn.execute(
                "SELECT * FROM subscriptions WHERE id = ?", (existing["id"],)
            ).fetchone()
            d = dict(row)
            d["created_at"] = str(d["created_at"]) if d.get("created_at") else ""
            return SubscriberResponse(**d)

        cursor = conn.execute(
            "INSERT INTO subscriptions (email, name) VALUES (?, ?)",
            (subscription.email, subscription.name)
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM subscriptions WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
        d = dict(row)
        d["created_at"] = str(d["created_at"]) if d.get("created_at") else ""
        return SubscriberResponse(**d)
    finally:
        conn.close()


@app.get("/api/subscribers", response_model=list[SubscriberResponse])
async def list_subscribers(active_only: bool = False, limit: int = 100, offset: int = 0):
    """List newsletter subscribers with optional filters."""
    conn = get_connection()
    try:
        query = "FROM subscriptions"
        params = []
        if active_only:
            query += " WHERE is_active = 1"
        rows = conn.execute(
            f"SELECT * {query} ORDER BY created_at DESC LIMIT ? OFFSET ?",
            params + [min(limit, 100), offset]
        ).fetchall()
        results = []
        for row in rows:
            d = dict(row)
            d["created_at"] = str(d["created_at"]) if d.get("created_at") else ""
            results.append(SubscriberResponse(**d))
        return results
    finally:
        conn.close()


@app.get("/api/subscribers/{subscriber_id}", response_model=SubscriberResponse)
async def get_subscriber(subscriber_id: int):
    """Get a single subscriber by ID."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM subscriptions WHERE id = ?", (subscriber_id,)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Subscriber not found")
        d = dict(row)
        d["created_at"] = str(d["created_at"]) if d.get("created_at") else ""
        return SubscriberResponse(**d)
    finally:
        conn.close()


@app.put("/api/subscribers/{subscriber_id}", response_model=SubscriberResponse)
async def update_subscriber(subscriber_id: int, update: SubscriberUpdate):
    """Update a subscriber's details or status."""
    conn = get_connection()
    try:
        existing = conn.execute(
            "SELECT * FROM subscriptions WHERE id = ?", (subscriber_id,)
        ).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Subscriber not found")

        fields = {}
        if update.is_active is not None:
            fields["is_active"] = 1 if update.is_active else 0
        if update.name is not None:
            fields["name"] = update.name
        if update.email is not None:
            fields["email"] = update.email

        if fields:
            set_clause = ", ".join(f"{k} = ?" for k in fields)
            values = list(fields.values()) + [subscriber_id]
            conn.execute(f"UPDATE subscriptions SET {set_clause} WHERE id = ?", values)
            conn.commit()

        row = conn.execute(
            "SELECT * FROM subscriptions WHERE id = ?", (subscriber_id,)
        ).fetchone()
        d = dict(row)
        d["created_at"] = str(d["created_at"]) if d.get("created_at") else ""
        return SubscriberResponse(**d)
    finally:
        conn.close()


@app.delete("/api/subscribers/{subscriber_id}")
async def delete_subscriber(subscriber_id: int):
    """Unsubscribe / remove a subscriber by ID."""
    conn = get_connection()
    try:
        existing = conn.execute(
            "SELECT * FROM subscriptions WHERE id = ?", (subscriber_id,)
        ).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Subscriber not found")
        conn.execute("DELETE FROM subscriptions WHERE id = ?", (subscriber_id,))
        conn.commit()
        return {"status": "ok", "deleted_id": subscriber_id}
    finally:
        conn.close()


# --- Cloudinary Image Upload Endpoint ---


@app.post("/api/upload", status_code=201, response_model=UploadResponse)
async def upload_image(file: UploadFile = File(...)):
    """Upload an image file to Cloudinary and return the URL.

    Accepts common image formats (JPEG, PNG, WebP, GIF).
    Requires multipart/form-data with field name 'file'.
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only image files are accepted (JPEG, PNG, WebP, GIF)",
        )

    try:
        configure_cloudinary()
        contents = await file.read()
        result = cloudinary.uploader.upload(
            contents,
            folder="sfa_assets",
            public_id=None,
            overwrite=True,
        )
        return UploadResponse(
            url=result["secure_url"],
            public_id=result["public_id"],
            format=result.get("format"),
            width=result.get("width"),
            height=result.get("height"),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image upload failed: {str(e)}",
        )


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
