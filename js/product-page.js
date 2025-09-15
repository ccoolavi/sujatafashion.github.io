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
                id: row[0],           // Column A: ProductID
                name: row[1],         // Column B: Name_en
                category: row[5],     // Column F: Category_en
                price: row[8],        // Column I: Price
                description: row[9],  // Column J: Description_en
                mainImage: row[12],   // Column M: MainImage
                image1: row[13],      // Column N: Image 1
                image2: row[14],      // Column O: Image 2
                image3: row[15],      // Column P: Image 3
                image4: row[16],      // Column Q: Image 4
                type: type
            };
        } else {
            product = {
                id: row[0],           // Column A: ProductID
                name: row[1],         // Column B: Name_en
                category: row[5],     // Column F: Category_en
                price: row[8],        // Column I: RentalPrice
                securityDeposit: row[9], // Column J: SecurityDeposit
                description: row[10], // Column K: Description_en
                mainImage: row[13],   // Column N: MainImage
                image1: row[14],      // Column O: Image 1
                image2: row[15],      // Column P: Image 2
                image3: row[16],      // Column Q: Image 3
                image4: row[17],      // Column R: Image 4
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

// Display product details with FIXED image carousel
function displayProductDetails(product) {
    const container = document.getElementById('product-detail-container');
    
    const imageGalleryHTML = product.images.length > 0 ? `
        <div class="image-gallery">
            <img 
                src="${product.images[0]}" 
                alt="${product.name}"
                class="main-image"
                id="main-product-image"
                style="width: 100%; max-height: 600px; object-fit: contain; border-radius: 8px; background: #f8f9fa;"
            >
            ${product.images.length > 1 ? `
                <div class="thumbnail-gallery">
                    ${product.images.map((img, index) => `
                        <img 
                            src="${img}" 
                            alt="${product.name} - Image ${index + 1}"
                            class="thumbnail ${index === 0 ? 'active' : ''}"
                            onclick="changeMainImage('${img}', ${index})"
                            style="width: 80px; height: 80px; object-fit: contain; border: 2px solid ${index === 0 ? '#667eea' : 'transparent'}; border-radius: 4px; cursor: pointer; background: #f8f9fa;"
                        >
                    `).join('')}
                </div>
            ` : ''}
        </div>
    ` : `
        <div class="image-gallery">
            <img 
                src="https://via.placeholder.com/500x600?text=No+Image"
                alt="No Image Available"
                class="main-image"
                style="width: 100%; max-height: 600px; object-fit: contain; border-radius: 8px;"
            >
        </div>
    `;
    
    container.innerHTML = `
        <div class="product-detail" style="display: grid; grid-template-columns: 1fr 1fr; gap: 40px; padding: 40px; background: white; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
            ${imageGalleryHTML}
            <div class="product-info">
                <div class="product-category" style="background: #f0f0f0; padding: 8px 16px; border-radius: 20px; display: inline-block; margin-bottom: 20px; color: #666;">${product.category}</div>
                <h1 style="color: #333; font-size: 2em; margin-bottom: 10px;">${product.name}</h1>
                <div class="product-price" style="font-size: 2em; color: #667eea; font-weight: bold; margin: 15px 0;">${formatPrice(product.price)}</div>
                ${product.securityDeposit ? `
                    <div class="security-deposit" style="font-size: 1.1em; color: #666; margin-bottom: 20px;">Security Deposit: ${formatPrice(product.securityDeposit)}</div>
                ` : ''}
                <div class="product-description" style="color: #666; line-height: 1.6; margin-bottom: 30px; font-size: 1.1em;">
                    ${product.description || 'Beautiful fashion item from Sujata Fashion'}
                </div>
                <div class="action-buttons" style="display: flex; gap: 15px; flex-wrap: wrap;">
                    <button onclick="shareOnWhatsApp()" style="background: #25D366; color: white; border: none; padding: 15px 25px; border-radius: 25px; font-weight: bold; cursor: pointer; font-size: 1em; flex: 1; min-width: 150px;">
                        💬 WhatsApp Inquiry
                    </button>
                    <button onclick="shareOnFacebook()" style="background: #1877F2; color: white; border: none; padding: 15px 25px; border-radius: 25px; font-weight: bold; cursor: pointer; font-size: 1em; flex: 1; min-width: 150px;">
                        📘 Share on Facebook
                    </button>
                    <button onclick="copyProductLink()" style="background: #6c757d; color: white; border: none; padding: 15px 25px; border-radius: 25px; font-weight: bold; cursor: pointer; font-size: 1em; flex: 1; min-width: 150px;">
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
        thumb.style.border = i === index ? '2px solid #667eea' : '2px solid transparent';
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

// Update page meta tags
function updatePageMeta(product) {
    document.title = `${product.name} - Sujata Fashion`;
}

// Go back to main page
function goBack() {
    window.history.back();
}

// Show error message
function showError(message) {
    const container = document.getElementById('product-detail-container');
    container.innerHTML = `
        <div style="text-align: center; padding: 40px; color: #dc3545;">
            <h3>⚠️ ${message}</h3>
            <button onclick="goBack()" style="background: #667eea; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin-top: 20px;">← Go Back</button>
        </div>
    `;
}
