/**
 * Excel Handler - Google Sheets CSV Integration for Sujata Fashion
 * ================================================================
 * 
 * This module fetches real product data from Google Sheets CSV exports
 * and displays it with proper image loading and WhatsApp integration.
 */
console.log('Excel Handler loading...');

// Google Sheets CSV URLs with correct GID numbers
const SHOP_CSV_URL = 'https://docs.google.com/spreadsheets/d/1YOUR_SHEET_ID/export?format=csv&gid=0';
const RENTAL_CSV_URL = 'https://docs.google.com/spreadsheets/d/1YOUR_SHEET_ID/export?format=csv&gid=1';

// WhatsApp configuration
const WHATSAPP_NUMBER = '+919763416561';

// Global variables
let shopProducts = [];
let rentalProducts = [];
let isLoading = false;

/**
 * Parse CSV text into array of objects
 */
function parseCSV(csvText) {
    const lines = csvText.split('\n');
    const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''));
    const products = [];
    
    for (let i = 1; i < lines.length; i++) {
        const line = lines[i].trim();
        if (!line) continue;
        
        const values = line.split(',').map(v => v.trim().replace(/"/g, ''));
        const product = {};
        
        headers.forEach((header, index) => {
            product[header] = values[index] || '';
        });
        
        // Map to expected structure
        if (product.ProductID && product.Name_en) {
            products.push({
                id: parseInt(product.ProductID) || 0,
                name: product.Name_en || 'Unnamed Product',
                price: parseFloat(product.Price) || 0,
                image: product.MainImage || '',
                category: (product.Category || '').toLowerCase(),
                description: product.Description_en || product.Name_en || 'No description available',
                nameHi: product.Name_hi || '',
                descriptionHi: product.Description_hi || '',
                gallery: [
                    product.MainImage,
                    product.Image2,
                    product.Image3,
                    product.Image4,
                    product.Image5
                ].filter(img => img && img.trim()),
                tags: (product.Tags || '').split(',').map(tag => tag.trim()).filter(tag => tag)
            });
        }
    }
    
    return products;
}

/**
 * Fetch CSV data from Google Sheets
 */
async function fetchCSVData(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const csvText = await response.text();
        return parseCSV(csvText);
    } catch (error) {
        console.error('Error fetching CSV data:', error);
        return [];
    }
}

/**
 * Load all product data
 */
async function loadAllProducts() {
    if (isLoading) {
        console.log('Already loading products...');
        return;
    }
    
    isLoading = true;
    console.log('Loading products from Google Sheets...');
    
    try {
        // Show loading state
        showLoadingState();
        
        // Fetch both shop and rental data in parallel
        const [shopData, rentalData] = await Promise.all([
            fetchCSVData(SHOP_CSV_URL),
            fetchCSVData(RENTAL_CSV_URL)
        ]);
        
        shopProducts = shopData;
        rentalProducts = rentalData;
        
        console.log(`Loaded ${shopProducts.length} shop products and ${rentalProducts.length} rental products`);
        
        // Display products
        displayProducts();
        
    } catch (error) {
        console.error('Error loading products:', error);
        showErrorState();
    } finally {
        isLoading = false;
    }
}

/**
 * Show loading state in UI
 */
function showLoadingState() {
    const container = document.getElementById('products-container');
    if (container) {
        container.innerHTML = `
            <div class="loading-state">
                <div class="spinner"></div>
                <p>Loading products from Google Sheets...</p>
            </div>
        `;
    }
}

/**
 * Show error state in UI
 */
function showErrorState() {
    const container = document.getElementById('products-container');
    if (container) {
        container.innerHTML = `
            <div class="error-state">
                <p>Error loading products. Please try again later.</p>
                <button onclick="loadAllProducts()" class="retry-btn">Retry</button>
            </div>
        `;
    }
}

/**
 * Display products in the UI
 */
function displayProducts() {
    const container = document.getElementById('products-container');
    if (!container) {
        console.error('Products container not found');
        return;
    }
    
    // Combine shop and rental products for display
    const allProducts = [...shopProducts, ...rentalProducts];
    
    if (allProducts.length === 0) {
        container.innerHTML = '<p class="no-products">No products available</p>';
        return;
    }
    
    container.innerHTML = allProducts.map(product => `
        <div class="product-card" data-product-id="${product.id}">
            <div class="product-image-container">
                <img src="${product.image}" 
                     alt="${product.name}" 
                     class="product-image"
                     onerror="this.src='https://via.placeholder.com/300x400?text=Image+Not+Available'">
            </div>
            <div class="product-info">
                <h3 class="product-name">${product.name}</h3>
                <p class="product-price">₹${product.price.toLocaleString()}</p>
                <p class="product-description">${product.description}</p>
                <div class="product-actions">
                    <button class="whatsapp-btn" onclick="openWhatsApp('${product.name}', ${product.price})">
                        💬 Order on WhatsApp
                    </button>
                </div>
            </div>
        </div>
    `).join('');
    
    console.log(`Displayed ${allProducts.length} products`);
}

/**
 * Open WhatsApp with product details
 */
function openWhatsApp(productName, price) {
    const message = `Hi! I'm interested in:\n${productName}\nPrice: ₹${price.toLocaleString()}\n\nCan you provide more details?`;
    const whatsappUrl = `https://wa.me/${WHATSAPP_NUMBER.replace(/[^0-9]/g, '')}?text=${encodeURIComponent(message)}`;
    window.open(whatsappUrl, '_blank');
}

/**
 * Filter products by category
 */
function filterProducts(category) {
    const allProducts = [...shopProducts, ...rentalProducts];
    const filtered = category === 'all' ? allProducts : allProducts.filter(p => p.category === category);
    
    const container = document.getElementById('products-container');
    if (container && filtered.length > 0) {
        container.innerHTML = filtered.map(product => `
            <div class="product-card" data-product-id="${product.id}">
                <div class="product-image-container">
                    <img src="${product.image}" 
                         alt="${product.name}" 
                         class="product-image"
                         onerror="this.src='https://via.placeholder.com/300x400?text=Image+Not+Available'">
                </div>
                <div class="product-info">
                    <h3 class="product-name">${product.name}</h3>
                    <p class="product-price">₹${product.price.toLocaleString()}</p>
                    <p class="product-description">${product.description}</p>
                    <div class="product-actions">
                        <button class="whatsapp-btn" onclick="openWhatsApp('${product.name}', ${product.price})">
                            💬 Order on WhatsApp
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }
}

/**
 * Search products by name or description
 */
function searchProducts(query) {
    if (!query.trim()) {
        displayProducts();
        return;
    }
    
    const allProducts = [...shopProducts, ...rentalProducts];
    const searchTerm = query.toLowerCase();
    const filtered = allProducts.filter(product => 
        product.name.toLowerCase().includes(searchTerm) ||
        product.description.toLowerCase().includes(searchTerm) ||
        product.tags.some(tag => tag.toLowerCase().includes(searchTerm))
    );
    
    const container = document.getElementById('products-container');
    if (container) {
        if (filtered.length === 0) {
            container.innerHTML = `<p class="no-results">No products found for "${query}"</p>`;
        } else {
            container.innerHTML = filtered.map(product => `
                <div class="product-card" data-product-id="${product.id}">
                    <div class="product-image-container">
                        <img src="${product.image}" 
                             alt="${product.name}" 
                             class="product-image"
                             onerror="this.src='https://via.placeholder.com/300x400?text=Image+Not+Available'">
                    </div>
                    <div class="product-info">
                        <h3 class="product-name">${product.name}</h3>
                        <p class="product-price">₹${product.price.toLocaleString()}</p>
                        <p class="product-description">${product.description}</p>
                        <div class="product-actions">
                            <button class="whatsapp-btn" onclick="openWhatsApp('${product.name}', ${product.price})">
                                💬 Order on WhatsApp
                            </button>
                        </div>
                    </div>
                </div>
            `).join('');
        }
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadAllProducts);
} else {
    loadAllProducts();
}

// Export functions for global use
window.filterProducts = filterProducts;
window.searchProducts = searchProducts;
window.openWhatsApp = openWhatsApp;
window.loadAllProducts = loadAllProducts;

console.log('Excel Handler loaded successfully');
