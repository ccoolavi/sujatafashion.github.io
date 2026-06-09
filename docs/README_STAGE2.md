# README Stage 2 - Data & Integration

## Completed Integrations

### 1. Google Sheets Integration
- **Purpose**: Acts as a zero-config data backend for product listings, testimonials, and inquiries.
- **Google Sheet Folder URL**: https://docs.google.com/spreadsheets/d/1JT5j6xifWkRcaeZIDzQjhB1RArzFEyqxSLQxnAObfms/edit
- **Status**: ✅ Integrated and accessible via CSV export.

### 2. Cloudinary Integration
- **Purpose**: Handles media asset management and image uploads.
- **Cloud Name**: `di9yqqagj`
- **Sample Public Image URL**: https://res.cloudinary.com/di9yqqagj/image/upload/v1/sample.jpg
- **Status**: ✅ Account configured and accessible.

### 3. Product Management API
- **Purpose**: Full CRUD API endpoints for product management backed by SQLite.
- **Endpoints**: `GET /api/products`, `GET /api/products/{id}`, `POST /api/products`, `PUT /api/products/{id}`, `DELETE /api/products/{id}`
- **Features**: Filter by category, type (shop/rent), active status. Supports partial updates.
- **Tests**: 11 test cases covering CRUD, filtering, and edge cases.
- **Status**: ✅ Implemented and tested (21/21 tests passing).

### 4. Inquiry Submission API (Task 15)
- **Purpose**: Validated course inquiry submission endpoint with structured data handling.
- **Endpoints**: `POST /api/inquiries` (JSON body), `GET /api/inquiries`
- **Features**: Pydantic-based request validation (email format, required fields, length constraints), proper HTTP status codes (201 for creation, 422 for validation errors).
- **Models**: `InquiryCreate` (request), `InquiryResponse` (response) in `backend/auth.py`
- **Tests**: 1 new test for validation rejection (invalid email, missing fields, short name).
- **Status**: ✅ Implemented and tested.

### 5. Testimonials API (Task 16)
- **Purpose**: Backend CRUD API for student video testimonials with database-backed storage.
- **Endpoints**: `GET /api/testimonials`, `GET /api/testimonials/{id}`, `POST /api/testimonials`, `PUT /api/testimonials/{id}`, `DELETE /api/testimonials/{id}`
- **Features**: Full CRUD with query-parameter partial updates, active-only filtering, Pydantic validation for name length (2-200), rating (1-5), and field constraints.
- **Models**: `TestimonialCreate` (request), `TestimonialResponse` (response) in `backend/auth.py`
- **Database Table**: `testimonials` (id, name, course, review, video_url, rating, is_active, created_at)
- **Tests**: 11 test cases covering CRUD, validation, filtering, and edge cases.
- **Status**: ✅ Implemented and tested (32/32 tests passing).

### 6. Cloudinary Upload API (Task 17)
- **Purpose**: REST API endpoint for uploading images to Cloudinary for products, testimonials, and other media.
- **Endpoints**: `POST /api/upload` (multipart file upload, returns Cloudinary URL + metadata)
- **Features**: Accepts JPEG/PNG/WebP/GIF images, validates content type, returns secure URL and public_id.
- **Models**: `UploadResponse` (url, public_id, format, width, height) in `backend/auth.py`
- **Tests**: 2 test cases covering successful upload (mocked) and non-image rejection.
- **Status**: ✅ Implemented and tested (34/34 tests passing).

### 7. Database Seeding & Data Management API (Task 18)
- **Purpose**: Seed and manage sample data in the SQLite database for development and testing.
- **Endpoints**: `POST /api/seed` (add sample products + testimonials), `DELETE /api/seed` (clear all seeded data)
- **Features**: Seeds 12 products (8 shop + 4 rent) and 5 testimonials with realistic fashion data including Cloudinary image URLs. Idempotent seeding — call multiple times.
- **Module**: `backend/seeder.py` with configurable product and testimonial data arrays.
- **Tests**: 8 test cases covering seeding, clearing, re-seeding, and data verification via product/testimonial APIs.
- **Status**: ✅ Implemented and tested (42/42 tests passing).

### 8. Product & Testimonial Pagination + Search (Task 19)
- **Purpose**: Added pagination (`limit`/`offset`) and text search (`search`) to product and testimonial list endpoints for production-ready data access.
- **Endpoints**: `GET /api/products` now accepts `?limit=10&offset=20&search=silk`, `GET /api/testimonials` accepts `?limit=10&offset=0`
- **Features**: `X-Total-Count` response header on both endpoints for client-side pagination UIs. Search performs LIKE match on product name and description. Limit capped at 100 for safety.
- **Backward Compatible**: All existing 42 tests pass unchanged. Response format remains a JSON array.
- **Tests**: 7 new test cases covering pagination, search, empty search results, total count header, and limit enforcement.
- **Status**: ✅ Implemented and tested (49/49 tests passing).

### 9. Inquiry Management CRUD (Task 20)
- **Purpose**: Full CRUD management endpoints for course inquiries with status tracking and admin notes.
- **Endpoints**: `GET /api/inquiries/{id}` (single inquiry), `PUT /api/inquiries/{id}` (update status/notes/fields), `DELETE /api/inquiries/{id}` (remove inquiry)
- **Features**: Status tracking (`new`/`contacted`/etc.), admin notes field, partial updates, proper 404 handling.
- **Models**: `InquiryUpdate` in `backend/auth.py` with optional fields for status, notes, name, phone, email, course, message, preferred_date.
- **Database**: Added `status TEXT DEFAULT 'new'` and `notes TEXT` columns to `inquiries` table with migration support.
- **Tests**: 7 new test cases covering single retrieval, status update, partial update, delete, and 404 handling.
- **Status**: ✅ Implemented and tested (56/56 tests passing).

### 10. Newsletter Subscription API (Task 21)
- **Purpose**: REST API for newsletter email subscription management with CRUD operations.
- **Endpoints**: `POST /api/subscribe` (subscribe email + optional name), `GET /api/subscribers` (list all/active), `GET /api/subscribers/{id}` (single), `PUT /api/subscribers/{id}` (update name/status/email), `DELETE /api/subscribers/{id}` (remove subscriber)
- **Features**: Duplicate email detection with auto-reactivation, email validation via Pydantic's EmailStr, active-only filtering, proper 404 handling.
- **Database Table**: `subscriptions` (id, email, name, is_active, source, created_at)
- **Tests**: 15 test cases covering subscription, listing, active filter, single retrieval, update, deactivation, delete, and validation.
- **Status**: ✅ Implemented and tested (71/71 tests passing).

### 11. Rental Booking Management API (Task 22)
- **Purpose**: CRUD API for managing rental product bookings with customer info, date ranges, deposit tracking, and status workflow.
- **Endpoints**: `GET /api/bookings` (list with status filter + pagination), `GET /api/bookings/{id}`, `POST /api/bookings`, `PUT /api/bookings/{id}`, `DELETE /api/bookings/{id}`
- **Features**: Validates product exists and is rent-type, status tracking (pending/confirmed/cancelled/completed), deposit tracking, `X-Total-Count` header with pagination, Pydantic validation for names, phone, dates, and amounts.
- **Database Table**: `bookings` (id, product_id, customer_name, customer_phone, customer_email, start_date, end_date, total_amount, deposit_amount, status, notes, created_at)
- **Tests**: 16 test cases covering CRUD, status workflow, filtering, product validation, and error handling.
- **Status**: ✅ Implemented and tested (87/87 tests passing).

### 12. Shop Order Management API (Task 23)
- **Purpose**: CRUD API for purchasing shop-type products with customer info, quantity, shipping address, and status workflow.
- **Endpoints**: `GET /api/orders` (list with status filter + pagination + X-Total-Count), `GET /api/orders/{id}`, `POST /api/orders`, `PUT /api/orders/{id}`, `DELETE /api/orders/{id}`
- **Features**: Validates product exists and is shop-type, quantity tracking, shipping address management, status tracking (pending/confirmed/shipped/delivered/cancelled), Pydantic validation.
- **Database Table**: `orders` (id, product_id, customer_name, customer_phone, customer_email, quantity, total_amount, shipping_address, status, notes, created_at)
- **Tests**: 16 test cases covering CRUD, status workflow, filtering, product type validation, and error handling.
| **Status**: ✅ Implemented and tested (103/103 tests passing).

### 13. Wishlist / Favorites API (Task 24)
- **Purpose**: CRUD API for customers to save favorite products for later reference.
- **Endpoints**: `GET /api/wishlist` (list with pagination + X-Total-Count), `GET /api/wishlist/{id}` (single), `POST /api/wishlist` (add product), `PUT /api/wishlist/{id}` (update), `DELETE /api/wishlist/{id}` (remove), `GET /api/wishlist/find` (lookup by phone/email)
- **Features**: Validates product exists before adding, duplicate detection via (product_id + phone + email), pagination with X-Total-Count header, find-by-customer endpoint for lookup.
- **Database Table**: `wishlist` (id, product_id, customer_name, customer_phone, customer_email, notes, created_at)
- **Tests**: 17 test cases covering CRUD, duplicate detection, product validation, pagination, and customer lookup.
- **Status**: ✅ Implemented and tested (120/120 tests passing).

## Next Steps

1. Continue Stage 2: Data & Integration tasks (25-30)
2. Begin Stage 3: Backend Development
3. Implement advanced authentication flows.
4. Complete full API coverage for product management.

---
*Last updated: June 09, 2026*
*Branch: test/stylist*
*Stage: 2 - Data & Integration*
