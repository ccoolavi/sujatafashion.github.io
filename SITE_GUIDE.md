# Sujata Fashions & Sujata Fashion Academy — Website Guide

## What is Sujata Fashions?

Sujata Fashions is a family-run business that has been **serving customers for 25+ years**. It does three things:

1. **Designer Fashion Shop** — sells readymade Indian women's and kids' clothing online
2. **Premium Rental Collection** — rents out bridal lehengas, festive wear, and party outfits
3. **Fashion Academy** — teaches fashion design courses (both in-person and online)

The business is run by **Sujata Ma'am** (the founder and head designer/teacher) and her team.

## What Does the Website Do?

The website is the **online face of the business**. Customers can:

- **Browse the Academy tab** to see course offerings (Professional Fashion Design, Blouse Design, Aari Embroidery, Online courses, etc.)
- **Browse the Shop tab** to see products available for purchase (with prices, photos, and "WhatsApp to buy" buttons)
- **Browse the Rent tab** to see outfits available for rental (with rental prices and security deposits)
- **Enrol in courses** by filling a form or sending a WhatsApp message
- **Contact the business** for enquiries

## How the Website Works Now (Live Site — sujatafashion.in)

| Feature | What it does |
|---------|-------------|
| **3 Tabs** | ACADEMY, SHOP, RENT — click to switch between them |
| **Course Cards** | Shows 6 courses with price, duration, learning items, "Enrol Now" button |
| **Product Cards** | Shows 8+ products with photo, name, price, category badge, "Details" + "WhatsApp" buttons |
| **Rental Cards** | Shows 14+ rental items with photo, rental price + security deposit, category badge |
| **Product Details Modal** | Click "Details" to see a larger photo, full description, and action buttons |
| **Video Testimonials** | Student success stories with video playback |
| **FAQ Accordion** | 5 common questions that expand/collapse when clicked |
| **Enquiry Form** | Name, phone, email, course selection, date picker, message field — sends to WhatsApp |
| **Floating WhatsApp Button** | A green WhatsApp icon that stays on screen — click to message the business |
| **Language Toggle** | Dropdown to switch language (feature skeleton) |
| **Category Filters** | Buttons to filter Shop items by Kids/Casual/Party/Formal and Rent items by Bridal/Festival |
| **Design Theme** | Modern, clean look with blue-purple gradients, rounded cards, smooth animations |

**Design Style:** The site uses a modern blue-purple gradient theme with:
- Inter font (clean, modern sans-serif)
- Glass-like translucent effects
- Smooth scroll animations
- Lots of white space and rounded corners
- WhatsApp green floating button

## What Was Built in I1site (Our Development Branch)

Our I1site branch added these things that the live site doesn't have:

| Feature | What it adds |
|---------|-------------|
| **Online Courses tab** | A 4th tab specifically for online/distance learning courses |
| **Footer** | Brand info, quick links, contact details, trust badges at the bottom of every page |
| **Trust Strip** | Number stats shown prominently (25+ years, 1000+ students, 100% practical, 4.9★ rating) |
| **SEO Meta Tags** | Better descriptions and keywords for Google search results |
| **Google Sheets Integration** | Placeholder to pull course/product data from a Google Sheet (not yet active) |

**Design Style:** Used a dark red / crimson theme with Georgia serif font — more traditional, classroom/academy feel.

## What We're Doing Now

We're **merging the best of both** into the I1site branch:

- **Keep the live site's modern design** (blue-purple gradients, animations, rounded cards)
- **Add the I1site's Online Courses tab, footer, trust strip**
- **Keep everything the live site already does well** (product modals, FAQ, video testimonials, enrolment form, WhatsApp button)
- **Host the improved site locally** on this server via Caddy (http://localhost:8080)
- **Test, review, and polish** until it's the best possible static website for Sujata Fashions

## How to View the Site

- **Live site** (production): https://sujatafashion.in
- **Local dev server** (our working copy): http://localhost:8080
- **GitHub repo**: https://github.com/ccoolavi/sujatafashion.github.io (branch: I1site)
- **GitHub Pages (test branch)**: publishes from `test/stylist` to sujatafashion.in

## Tech Behind the Scenes (for the curious)

- The site is **pure HTML + CSS + JavaScript** — no database, no server-side code
- **Google Sheets** is used to store product/course data (loaded via JavaScript)
- **Google reCAPTCHA** prevents spam on the enquiry form
- Images are stored in the `assets/images/` folder
- Hosted on **GitHub Pages** (free hosting)
- We're also running a local copy on this server using **Caddy** (a lightweight web server)
