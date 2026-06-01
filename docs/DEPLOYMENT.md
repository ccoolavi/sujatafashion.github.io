# Deployment Guide — Sujata Fashions Static Site

## Quick Start

This is a static HTML/CSS/JS site. No build step, no server runtime. Deployable to any static host.

### GitHub Pages (Current)

The live site at **sujatafashion.in** is published via GitHub Pages from the **`test/stylist`** branch.

To update the live site:
1. Work on `I1site` (default branch) — never commit directly to `test/stylist`
2. When ready, open a PR from `I1site` → `test/stylist`
3. Merge and GitHub Pages auto-deploys within 2–3 minutes

### Deploy to a New Server

The repo is fully self-contained. To host elsewhere:

```bash
# Option A: Clone and serve via Nginx / Apache
git clone https://github.com/ccoolavi/sujatafashion.github.io.git /var/www/sujatafashion
# Point your web root to the cloned directory

# Option B: Serve with Python (for testing)
cd /path/to/repo
python3 -m http.server 8000

# Option C: Serve with Node
npx serve .
```

### Backup

Full sync to GitHub is the backup strategy. To backup locally:

```bash
git clone --mirror https://github.com/ccoolavi/sujatafashion.github.io.git
# The --mirror clone contains every branch and tag
```

## Requirements

- Static web server (Nginx, Apache, Caddy, or any CDN)
- DNS pointing to your host
- (Optional) Google Sheets API key for product data

## Environment Variables / Config

No build-time env vars needed. The following may need updating per deployment:

| File | Value |
|------|-------|
| `CNAME` | Update domain if not `sujatafashion.in` |
| `index.html` (line 1273) | Google Sheets API key `API_KEY` |
| `js/excel-handler.js` (line 11) | CSV export GIDs |
| `js/product-page.js` (line 2) | Google Sheets API key |

## Key Files

| File | Purpose |
|------|---------|
| `index.html` | Single-page app (Academy, Online, Shop, Rent tabs) |
| `product.html` | Product detail page (linked from shop/rental) |
| `stylist-test.html` | Interactive stylist quiz |
| `css/main.css` | Global styles |
| `js/main.js` | Core interactivity, data loading |
| `js/excel-handler.js` | Google Sheets CSV integration |
| `js/product-page.js` | Product page data fetching |
| `js/admin.js` | Admin page (password-protected) |
| `assets/images/` | Logo, product images, rental images |
| `robots.txt` | SEO crawler rules |
| `sitemap.xml` | Search engine sitemap |

## Live Site

**URL:** https://sujatafashion.in
**Repository:** https://github.com/ccoolavi/sujatafashion.github.io
