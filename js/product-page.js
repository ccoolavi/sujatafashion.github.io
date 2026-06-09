// Google Sheets API Configuration
const API_KEY = 'AIzaSyAWWpa4xPGR8aBWKqSq0oKOp6a0XELijh0';
const SPREADSHEET_ID = '1JT5j6xifWkRcaeZIDzQjhB1RArzFEyqxSLQxnAObfms';
const WHATSAPP_NUMBER = '+919763416561';

let currentProduct = null;

// Initialize product page
document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    const productId = urlParams.get('id')?.trim();
    const productType = urlParams.get('type')?.trim();
    
    console.log('Loading product:', productId, productType);
    
    if (productId && productType) {
        loadProductDetails(productId, productType);
    } else {
        showError('Invalid product URL');
    }
});

// Fetch data from Google Sheets
async function fetchSheetData(range) {
    const url = `https://sheets.googleapis.com/v4/spreadsheets/${SPREADSHEET_ID}/values/${range}?key=${API_KEY}`;
    console.log('Fetching from:', url);
    
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const result = await response.json();
    return result.values || [];
}

// Load product details
async function loadProductDetails(productId, type) {
    try {
        console.log('🔍 Loading product details for:', productId, type);
        
        const range = type === 'rent' ? 'Rental!A:V' : 'Sale!A:U';
        const data = await fetchSheetData(range);
        const product = parseAndFindProduct(data, type, productId);
        
        if (product) {
            currentProduct = product;
            displayProductDetails(product);
        } else {
            showError('Product not found');
        }
    } catch (error) {
        console.error('Error loading product:', error);
        showError('Failed to load product details');
    }
}

// Parse data and find specific product
function parseAndFindProduct(data, type, targetId) {
    if (!data || data.length < 2) return null;
    
    const rows = data.slice(1);
    
    for (let row of rows) {
        if (!row || row.length === 0) continue;
        
        const productId = row[0]?.toString().trim();
        if (productId !== targetId) continue;
        
        let product = {};
        
        if (type === 'shop') {
            product = {
                id: row[0],           // Column A
                name: row[1],         // Column B
                category: row[5],     // Column F
                price: row[8],        // Column I
                description: row[9],  // Column J
                mainImage: row[12],   // Column M
                image1: row[13],
                image2: row[14],
                image3: row[15],
                image4: row[16],
                type: type
            };
        } else {
            product = {
                id: row[0],           // Column A
                name: row[1],         // Column B
                category: row[5],     // Column F
                price: row[8],        // Column I
                securityDeposit: row[9], // Column J
                description: row[10], // Column K
                mainImage: row[13],   // Column N (FIXED!)
                image1: row[14],
                image2: row[15],
                image3: row[16],
                image4: row[17],
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

// Display product details - CLEAN VERSION
function displayProductDetails(product) {
    const container = document.getElementById('product-detail-container');
    
    container.innerHTML = `
        <div class="product-detail">
            <div class="image-gallery">
                <img 
                    src="${product.images[0] || 'https://via.placeholder.com/500x600?text=No+Image'}" 
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
    
    // Update page title
    document.title = `${product.name} - Sujata Fashion`;
}

// Change main image
function changeMainImage(imageSrc, index) {
    document.getElementById('main-product-image').src = imageSrc;
    
    document.querySelectorAll('.thumbnail').forEach((thumb, i) => {
        thumb.classList.toggle('active', i === index);
    });
}

// WhatsApp sharing
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

// Copy link
function copyProductLink() {
    navigator.clipboard.writeText(window.location.href).then(() => {
        alert('Product link copied to clipboard!');
    }).catch(() => {
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

// Go back
function goBack() {
    window.history.back();
}

// Show error
function showError(message) {
    const container = document.getElementById('product-detail-container');
    container.innerHTML = `
        <div class="error" style="text-align: center; padding: 40px; color: #dc3545;">
            <h3>⚠️ ${message}</h3>
            <button class="back-button" onclick="goBack()">← Go Back</button>
        </div>
    `;
}
