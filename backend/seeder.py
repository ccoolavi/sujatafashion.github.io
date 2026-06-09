"""Sujata Fashion Backend — Database Seed Data and Management.

Provides realistic sample products, testimonials, and seeding logic
so the backend APIs can serve meaningful data for testing and development.
"""
import sqlite3

# ── Product Seed Data ──────────────────────────────────────────────

PRODUCTS = [
    # Shop Products
    {
        "name": "Elegant Silk Saree",
        "category": "C1",
        "price": 7990.0,
        "description": "Beautiful handwoven silk saree with intricate embroidery work, perfect for special occasions and traditional events.",
        "image_url": "https://res.cloudinary.com/di9yqqagj/image/upload/v1/sfa_assets/saree_elegant.jpg",
        "type": "shop",
    },
    {
        "name": "Designer Banarasi Saree",
        "category": "C1",
        "price": 12500.0,
        "description": "Premium Banarasi silk saree with golden zari work and traditional motifs, crafted by skilled artisans.",
        "image_url": "https://res.cloudinary.com/di9yqqagj/image/upload/v1/sfa_assets/saree_banarasi.jpg",
        "type": "shop",
    },
    {
        "name": "Cotton Kurta Set",
        "category": "C2",
        "price": 4500.0,
        "description": "Comfortable cotton kurta with matching palazzo pants, ideal for daily wear and casual outings.",
        "image_url": "https://res.cloudinary.com/di9yqqagj/image/upload/v1/sfa_assets/kurta_cotton.jpg",
        "type": "shop",
    },
    {
        "name": "Anarkali Suit Set",
        "category": "C2",
        "price": 8900.0,
        "description": "Stunning Anarkali suit with heavy embroidery and dupatta, perfect for festivities and celebrations.",
        "image_url": "https://res.cloudinary.com/di9yqqagj/image/upload/v1/sfa_assets/anarkali_suit.jpg",
        "type": "shop",
    },
    {
        "name": "Embroidered Blouse",
        "category": "C3",
        "price": 2500.0,
        "description": "Beautifully embroidered blouse with Aari work, perfect for pairing with sarees and lehengas.",
        "image_url": "https://res.cloudinary.com/di9yqqagj/image/upload/v1/sfa_assets/blouse_embroidered.jpg",
        "type": "shop",
    },
    {
        "name": "Designer Lehenga Choli",
        "category": "C4",
        "price": 18500.0,
        "description": "Exquisite designer lehenga choli with intricate mirror work and embroidery for bridal occasions.",
        "image_url": "https://res.cloudinary.com/di9yqqagj/image/upload/v1/sfa_assets/lehenga_designer.jpg",
        "type": "shop",
    },
    {
        "name": "Baby Frock Set",
        "category": "C5",
        "price": 1200.0,
        "description": "Adorable baby frock made with soft cotton fabric, safe and comfortable for your little one.",
        "image_url": "https://res.cloudinary.com/di9yqqagj/image/upload/v1/sfa_assets/baby_frock.jpg",
        "type": "shop",
    },
    {
        "name": "Casual Palazzo Set",
        "category": "C6",
        "price": 3200.0,
        "description": "Trendy palazzo set with matching top, perfect for everyday wear with a touch of style.",
        "image_url": "https://res.cloudinary.com/di9yqqagj/image/upload/v1/sfa_assets/palazzo_set.jpg",
        "type": "shop",
    },
    # Rental Products
    {
        "name": "Festival Lehenga Gold",
        "category": "festival",
        "price": 3000.0,
        "description": "Heavy embroidered festival lehenga with golden work, perfect for traditional celebrations and Diwali festivities.",
        "image_url": "https://res.cloudinary.com/di9yqqagj/image/upload/v1/sfa_assets/rental_festival_gold.jpg",
        "type": "rent",
    },
    {
        "name": "Festival Saree Royal",
        "category": "festival",
        "price": 2500.0,
        "description": "Royal silk saree with intricate zari work, ideal for festival occasions and special celebrations.",
        "image_url": "https://res.cloudinary.com/di9yqqagj/image/upload/v1/sfa_assets/rental_saree_royal.jpg",
        "type": "rent",
    },
    {
        "name": "Wedding Lehenga Premium",
        "category": "wedding",
        "price": 5000.0,
        "description": "Premium wedding lehenga with heavy embroidery and pearl work, designed for the most special day.",
        "image_url": "https://res.cloudinary.com/di9yqqagj/image/upload/v1/sfa_assets/rental_wedding_lehenga.jpg",
        "type": "rent",
    },
    {
        "name": "Wedding Saree Luxury",
        "category": "wedding",
        "price": 4500.0,
        "description": "Luxurious wedding saree with golden zari and traditional motifs, perfect for bridal occasions.",
        "image_url": "https://res.cloudinary.com/di9yqqagj/image/upload/v1/sfa_assets/rental_wedding_saree.jpg",
        "type": "rent",
    },
]

# ── Testimonial Seed Data ──────────────────────────────────────────

TESTIMONIALS = [
    {
        "name": "Priya Sharma",
        "course": "1 Year Fashion Design",
        "review": "Amazing experience at Sujata Fashion! The instructors are knowledgeable and supportive. I learned everything from basic stitching to advanced pattern making.",
        "video_url": "https://youtube.com/watch?v=test001",
        "rating": 5,
    },
    {
        "name": "Anita Patel",
        "course": "Aari Work Course",
        "review": "Learned so much in the Aari work course. Now I have my own small business! The hands-on training was excellent and very practical.",
        "video_url": "",
        "rating": 5,
    },
    {
        "name": "Meera Singh",
        "course": "Blouse Design Course",
        "review": "The blouse design course was perfect for me. I can now design and stitch blouses for my family and friends professionally.",
        "video_url": "https://youtube.com/watch?v=test002",
        "rating": 5,
    },
    {
        "name": "Kavya Reddy",
        "course": "1 Year Fashion Design",
        "review": "Best decision ever! The comprehensive fashion design course gave me all the skills I needed to start my own boutique.",
        "video_url": "",
        "rating": 5,
    },
    {
        "name": "Rajeshwari Devi",
        "course": "Fashion Illustration",
        "review": "Excellent course structure and very patient teachers. The illustration techniques I learned have helped me launch my design career.",
        "video_url": "https://youtube.com/watch?v=test003",
        "rating": 4,
    },
]


def seed_products(conn: sqlite3.Connection) -> int:
    """Insert seed products into the database. Returns count of inserted rows."""
    cursor = conn.cursor()
    count = 0
    for product in PRODUCTS:
        cursor.execute(
            """INSERT INTO products (name, category, price, description, image_url, type, is_active)
               VALUES (?, ?, ?, ?, ?, ?, 1)""",
            (
                product["name"],
                product["category"],
                product["price"],
                product["description"],
                product["image_url"],
                product["type"],
            ),
        )
        count += 1
    conn.commit()
    return count


def seed_testimonials(conn: sqlite3.Connection) -> int:
    """Insert seed testimonials into the database. Returns count of inserted rows."""
    cursor = conn.cursor()
    count = 0
    for testimonial in TESTIMONIALS:
        cursor.execute(
            """INSERT INTO testimonials (name, course, review, video_url, rating, is_active)
               VALUES (?, ?, ?, ?, ?, 1)""",
            (
                testimonial["name"],
                testimonial["course"],
                testimonial["review"],
                testimonial["video_url"],
                testimonial["rating"],
            ),
        )
        count += 1
    conn.commit()
    return count


def seed_all(conn: sqlite3.Connection) -> dict:
    """Seed all data into the database. Returns a summary dict."""
    products_count = seed_products(conn)
    testimonials_count = seed_testimonials(conn)
    return {
        "products_seeded": products_count,
        "testimonials_seeded": testimonials_count,
    }


def clear_seed_data(conn: sqlite3.Connection) -> dict:
    """Remove all seed data from products and testimonials tables."""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products")
    cursor.execute("DELETE FROM testimonials")
    conn.commit()
    return {"cleared": True}
