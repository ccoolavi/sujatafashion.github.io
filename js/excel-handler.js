/**
 * Excel Handler - Google Sheets CSV Integration for Sujata Fashion
 * ================================================================
 * 
 * This module fetches real product data from Google Sheets CSV exports
 * and displays it with proper image loading and WhatsApp integration.
 */
console.log('Excel Handler loading...');

// Google Sheets CSV URLs with correct GID numbers
const SHOP_CSV_URL = 'https://docs.google.com/spreadsheets/d/1JT5j6xifWkRcaeZIDzQjhB1RArzFEyqxSLQxnAObfms/export?format=csv&gid=1717675571';
const RENTAL_CSV_URL = 'https://docs.google.com/spreadsheets/d/1JT5j6xifWkRcaeZIDzQjhB1RArzFEyqxSLQxnAObfms/export?format=csv&gid=1815405474';

// WhatsApp configuration
const WHATSAPP_NUMBER = '+919763416561';

// Global variables
let shopProducts = [];
let rentalProducts = [];
let isLoading = false;

/**
 * Parse CSV text into array of objects with proper handling for quoted fields
 */
function parseCSV(csvText) {
    const lines = csvText.split('\n');
    if (lines.length < 2) return [];
    
    // Parse header row
    const headers = parseCSVLine(lines[0]);
    const products = [];
    
    for (let i = 1; i < lines.length; i++) {
        const line = lines[i].trim();
        if (!line) continue;
        
        const values = parseCSVLine(line);
        const product = {};
        
        headers.forEach((header, index) => {
            product[header] = values[index] || '';
        });
        
        // Map to expected structure with proper field mapping
        if (product['Product ID'] && product['Name (English)']) {
            products.push({
                id: parseInt(product['Product ID']) || 0,
                name: product['Name (English)'] || 'Unnamed Product',
                price: parseFloat(product['Price']) || 0,
                image: product['Main Image'] || '',
                category: (product['Category'] || '').toLowerCase(),
                description: product['Description (English)'] || product['Name (English)'] || 'No description available',
                nameHi: product['Name (Hindi)'] || '',
                descriptionHi: product['Description (Hindi)'] || '',
                gallery: [
                    product['Main Image'],
                    product['Image 2'],
                    product['Image 3'],
                    product['Image 4'],
                    product['Image 5']
                ].filter(img => img && img.trim()),
                tags: (product['Tags'] || '').split(',').map(tag => tag.trim()).filter(tag => tag)
            });
        }
    }
    
    return products;
}

/**
 * Parse a single CSV line handling quoted fields properly
 */
function parseCSVLine(line) {
    const result = [];
    let current = '';
    let inQuotes = false;
    
    for (let i = 0; i < line.length; i++) {
        const char = line[i];
        
        if (char === '"') {
            if (inQuotes && line[i + 1] === '"') {
                // Handle escaped quotes
                current += '"';
                i++; // Skip next quote
            } else {
                // Toggle quote state
                inQuotes = !inQuotes;
            }
        } else if (char === ',' && !inQuotes) {
            // End of field
            result.push(current.trim());
            current = '';
        } else {
            current += char;
        }
    }
    
    // Add the last field
    result.push(current.trim());
    return result;
}

/**
 * Fetch and parse CSV data from Google Sheets
 */
async function fetchProductData(csvUrl) {
    try {
        console.log('Fetching data from:', csvUrl);
        const response = await fetch(csvUrl);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const csvText = await response.text();
        console.log('CSV data received:', csvText.substring(0, 200) + '...');
        
        return parseCSV(csvText);
    } catch (error) {
        console.error('Error fetching product data:', error);
        return [];
    }
}

/**
 * Load shop products
 */
async function loadShopProducts() {
    if (isLoading) return;
    isLoading = true;
    
    try {
        shopProducts = await fetchProductData(SHOP_CSV_URL);
        console.log('Shop products loaded:', shopProducts.length);
        return shopProducts;
    } catch (error) {
        console.error('Error loading shop products:', error);
        return [];
    } finally {
        isLoading = false;
    }
}

/**
 * Load rental products
 */
async function loadRentalProducts() {
    if (isLoading) return;
    isLoading = true;
    
    try {
        rentalProducts = await fetchProductData(RENTAL_CSV_URL);
        console.log('Rental products loaded:', rentalProducts.length);
        return rentalProducts;
    } catch (error) {
        console.error('Error loading rental products:', error);
        return [];
    } finally {
        isLoading = false;
    }
}

/**
 * Get products by category
 */
function getProductsByCategory(products, category) {
    if (!category || category === 'all') return products;
    return products.filter(product => 
        product.category && product.category.includes(category.toLowerCase())
    );
}

/**
 * Create WhatsApp message for product inquiry
 */
function createWhatsAppMessage(product, type = 'shop') {
    const productType = type === 'rental' ? 'Rental' : 'Purchase';
    const message = `Hi! I'm interested in this ${productType.toLowerCase()} item:\n\n` +
                   `${product.name}\n` +
                   `Price: ₹${product.price}\n` +
                   `Product ID: ${product.id}\n\n` +
                   `Could you please provide more details?`;
    
    return encodeURIComponent(message);
}

/**
 * Open WhatsApp with product inquiry
 */
function inquireOnWhatsApp(product, type = 'shop') {
    const message = createWhatsAppMessage(product, type);
    const whatsappUrl = `https://wa.me/${WHATSAPP_NUMBER}?text=${message}`;
    window.open(whatsappUrl, '_blank');
}

/**
 * Initialize the excel handler
 */
async function initializeExcelHandler() {
    console.log('Initializing Excel Handler...');
    
    // Pre-load data if needed
    try {
        await Promise.all([
            loadShopProducts(),
            loadRentalProducts()
        ]);
        console.log('Excel Handler initialized successfully');
    } catch (error) {
        console.error('Error initializing Excel Handler:', error);
    }
}

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeExcelHandler);
} else {
    initializeExcelHandler();
}

// Export functions for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        loadShopProducts,
        loadRentalProducts,
        getProductsByCategory,
        inquireOnWhatsApp,
        shopProducts,
        rentalProducts
    };
}
