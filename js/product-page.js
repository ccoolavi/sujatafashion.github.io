// Google Sheets API Configuration
const API_KEY = 'AIzaSyAWWpa4xPGR8aBWKqSq0oKOp6a0XELijh0';
const SPREADSHEET_ID = '1JT5j6xifWkRcaeZIDzQjhB1RArzFEyqxSLQxnAObfms';
const WHATSAPP_NUMBER = '+919763416561';

let currentProduct = null;

// Initialize product page
document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const productId = urlParams.get('id');
    const productType = urlParams.get('type');
    
    if (productId && productType) {
        loadProductDetails(productId, productType);
    } else {
        showError('Invalid product URL');
    }
});

// Load product details
async function loadProductDetails(productId, type) {
    try {
        console.log('🔍 Loading product details for:', productId, type);
        
        const range = type === 'rent' ? 'Rental!A:V' : 'Sale!A:U';
        const data = await fetchSheetData(range);
        const product = parseProductData(data, type, productId);
        
        if (product) {
            currentProduct = product;
            displayProductDetails(product);
            updatePageMeta(product);
        } else {
            showError('Product not found');
        }
    } catch (error) {
        console.error('Error loading product:', error);
        showError('Failed to load product details');
    }
}

// Fetch data from Google Sheets
async function fetchSheetData(range) {
    const url = `https://sheets.googleapis.com/v4/spreadsheets/${SPREADSHEET_ID}/values/${range}?key=${API_KEY}`;
    const response = await fetch(url);
    
    if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const result = await response.json();
    return result.values || [];
}

// Parse product data and find specific product
function parseProductData(data, type, targetId) {
    if (!data || data.length < 2) return null;
    
    const rows = data.slice(1);
    
    for (let row of rows) {
        if (!row || row.length === 0) continue;
        
        const productId = row[0];
        if (productId !== targetId) continue;
        
        let product = {};
        
        if (type === 'shop') {
            product = {
                id: row[0],
                name: row[1],
                nameHi: row[2],
                nameMr: row[3],
                category: row[5],
                price: row[8],
                description: row[9],
                mainImage: row[12],
                image1: row[13],
                image2: row[14],
                image3: row[15],
                image4: row[16],
                whatsappMessage: row[18],
                inStock: row[19],
                tags: row[20],
                type: type
            };
        } else {
            product = {
                id: row[0],
                name: row[1],
                nameHi: row[2],
                nameMr: row[3],
                category: row[5],
                price: row[8],
                securityDeposit: row[9],
                description: row[10],
                mainImage: row[13],
                image1: row[14],
                image2: row[15],
                image3: row[16],
                image4: row[17],
                whatsappMessage: row[18],
                available: row[19],
                tags: row[20],
                type: type
            };
        }
        
        // Create image gallery
        product.images = [
            product.mainImage,
            product.image1,
            product.image2,
            product.image3,
            product.image4
        ].filter(img => img && img !== 'NA' && img.trim());
        
        return product;
    }
    
    return null;
}

// Display product details with image carousel
function displayProductDetails(product) {
    const container = document.getElementById('product-detail-container');
    
    const imageGalleryHTML = product.images.length > 0 ? `
        <div class="image-gallery">
            <img 
                src="${product.images[0]}" 
                alt="${product.name}"
                class="main-image"
                id="main-product-image"
            >
            ${product.images.length > 1 ? `
                <div class="thumbnail-gallery">
                    ${product.images.map((img, index) => `
                        <img 
                            src="${img}" 
                            alt="${product.name} - Image ${index + 1}"
                            class="thumbnail ${index === 0 ? 'active' : ''}"
                            onclick="changeMainImage('${img}', ${index})"
                        >
                    `).join('')}
                </div>
            ` : ''}
        </div>
    ` : `
        <div class="image-gallery">
            <img 
                src="https://via.placeholder.com/500x500?text=No+Image"
                alt="No Image Available"
                class="main-image"
            >
        </div>
    `;
    
    container.innerHTML = `
        <div class="product-detail">
            ${imageGalleryHTML}
            <div class="product-info">
                <div class="product-category">${product.category}</div>
                <h1>${product.name}</h1>
                <div class="product-price">${formatPrice(product.price)}</div>
                ${product.securityDeposit ? `
                    <div class="security-deposit">Security Deposit: ${formatPrice(product.securityDeposit)}</div>
                ` : ''}
                <div class="product-description">
                    ${product.description || 'Beautiful fashion item from Sujata Fashion'}
                </div>
                <div class="action-buttons">
                    <button class="whatsapp-btn" onclick="shareOnWhatsApp()">
                        💬 WhatsApp Inquiry
                    </button>
                    <button class="facebook-btn" onclick="shareOnFacebook()">
                        📘 Share on Facebook
                    </button>
                    <button class="copy-btn" onclick="copyProductLink()">
                        🔗 Copy Link
                    </button>
                </div>
            </div>
        </div>
    `;
}

// Change main image in carousel
function changeMainImage(imageSrc, index) {
    document.getElementById('main-product-image').src = imageSrc;
    
    // Update active thumbnail
    document.querySelectorAll('.thumbnail').forEach((thumb, i) => {
        thumb.classList.toggle('active', i === index);
    });
}

// WhatsApp sharing with image and description
function shareOnWhatsApp() {
    if (!currentProduct) return;
    
    const actionType = currentProduct.type === 'rent' ? 'rent' : 'purchase';
    const message = `Hi! I'm interested in this ${actionType} item from Sujata Fashion:

🛍️ Product: ${currentProduct.name}
🆔 ID: ${currentProduct.id}
💰 Price: ${formatPrice(currentProduct.price)}
${currentProduct.securityDeposit ? `💳 Security: ${formatPrice(currentProduct.securityDeposit)}` : ''}
📱 Category: ${currentProduct.category}

🖼️ Image: ${currentProduct.mainImage}

📝 Description: ${currentProduct.description}

🔗 Product Link: ${window.location.href}

Could you please provide more details and availability?

Thank you! 🙏`;

    const whatsappUrl = `https://wa.me/${WHATSAPP_NUMBER.replace(/\D/g, '')}?text=${encodeURIComponent(message)}`;
    window.open(whatsappUrl, '_blank');
}

// Facebook sharing
function shareOnFacebook() {
    const url = encodeURIComponent(window.location.href);
    const facebookUrl = `https://www.facebook.com/sharer/sharer.php?u=${url}`;
    window.open(facebookUrl, '_blank', 'width=600,height=400');
}

// Copy product link
function copyProductLink() {
    navigator.clipboard.writeText(window.location.href).then(() => {
        alert('Product link copied to clipboard!');
    }).catch(() => {
        // Fallback for older browsers
        const tempInput = document.createElement('input');
        tempInput.value = window.location.href;
        document.body.appendChild(tempInput);
        tempInput.select();
        document.execCommand('copy');
        document.body.removeChild(tempInput);
        alert('Product link copied to clipboard!');
    });
}

// Format price
function formatPrice(price) {
    if (!price || price === '0') return 'Price on Request';
    
    const cleanPrice = price.toString().replace(/[^\d.,]/g, '');
    const numericPrice = parseFloat(cleanPrice.replace(',', ''));
    
    if (isNaN(numericPrice)) return price;
    
    return `₹${numericPrice.toLocaleString('en-IN')}`;
}

// Update page meta tags for SEO and social sharing
function updatePageMeta(product) {
    document.title = `${product.name} - Sujata Fashion`;
    
    // Update or create meta tags
    updateMetaTag('description', `${product.name} - ${product.description} | Price: ${formatPrice(product.price)}`);
    updateMetaTag('og:title', `${product.name} - Sujata Fashion`);
    updateMetaTag('og:description', product.description);
    updateMetaTag('og:image', product.mainImage);
    updateMetaTag('og:url', window.location.href);
    updateMetaTag('twitter:card', 'summary_large_image');
    updateMetaTag('twitter:title', `${product.name} - Sujata Fashion`);
    updateMetaTag('twitter:description', product.description);
    updateMetaTag('twitter:image', product.mainImage);
}

// Helper to update meta tags
function updateMetaTag(property, content) {
    let selector = `meta[property="${property}"]`;
    let element = document.querySelector(selector);
    
    if (!element) {
        selector = `meta[name="${property}"]`;
        element = document.querySelector(selector);
    }
    
    if (element) {
        element.setAttribute('content', content);
    } else {
        const meta = document.createElement('meta');
        if (property.startsWith('og:') || property.startsWith('twitter:')) {
            meta.setAttribute('property', property);
        } else {
            meta.setAttribute('name', property);
        }
        meta.setAttribute('content', content);
        document.head.appendChild(meta);
    }
}

// Go back to main page
function goBack() {
    window.history.back();
}

// Show error message
function showError(message) {
    const container = document.getElementById('product-detail-container');
    container.innerHTML = `
        <div class="error" style="text-align: center; padding: 40px; color: #dc3545;">
            <h3>⚠️ ${message}</h3>
            <button class="back-button" onclick="goBack()">← Go Back</button>
        </div>
    `;
}
